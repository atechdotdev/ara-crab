"""Crab rig: a local page for mapping Sesame's 8 joints to the board's ports.

    python3 rig_server.py            # then open http://localhost:8765

The server holds the board's USB port, so close `atech monitor` first. Everything the
page does is logged to rig_log.txt; Save writes rig_config.json, puts the map and the
neutral angles into project.yaml (between CONFIG BEGIN / END) and flashes the board.
"""
import json
import re
import subprocess
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import serial
from serial.tools import list_ports

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "rig_config.json"
LOG = HERE / "rig_log.txt"
PROJECT = HERE / "project.yaml"
PAGE = HERE / "rig.html"
PORT_HTTP = 8765

JOINTS = ["FL hip", "FL knee", "FR hip", "FR knee", "RL hip", "RL knee", "RR hip", "RR knee"]
DEFAULT = {
    "joints": {
        "FL hip": {"pin": "3", "neutral": 45}, "FL knee": {"pin": "4", "neutral": 0},
        "FR hip": {"pin": "10", "neutral": 135}, "FR knee": {"pin": "11", "neutral": 180},
        "RL hip": {"pin": "5", "neutral": 135}, "RL knee": {"pin": "6", "neutral": 180},
        "RR hip": {"pin": "13", "neutral": 45}, "RR knee": {"pin": "14", "neutral": 0},
    },
    "status": {},
    "notes": "",
}


def log(line):
    stamp = time.strftime("%H:%M:%S")
    with LOG.open("a") as f:
        f.write(f"{stamp} {line}\n")
    board.recent.append(f"{stamp} {line}")


class BoardLink:
    """One serial connection: a reader thread for events and acks, one action at a time."""

    def __init__(self):
        self.ser = None
        self.lock = threading.Lock()
        self.acks = deque()
        self.ack_cv = threading.Condition()
        self.recent = deque(maxlen=300)
        self.paused = False
        threading.Thread(target=self._reader, daemon=True).start()

    def _find(self):
        for p in list_ports.comports():
            if p.vid == 0x303A:
                return p.device
        return None

    def _open(self):
        dev = self._find()
        if not dev:
            return False
        s = serial.Serial()
        s.port, s.baudrate, s.timeout = dev, 115200, 0.2
        s.dtr = s.rts = False                     # don't reset the board on open
        s.open()
        self.ser = s
        log(f"connected to {dev}")
        return True

    def close(self):
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None

    def _reader(self):
        while True:
            if self.paused:
                time.sleep(0.2)
                continue
            if not self.ser:
                try:
                    if not self._open():
                        time.sleep(1)
                        continue
                except Exception:
                    time.sleep(1)
                    continue
            try:
                raw = self.ser.readline()
            except Exception:
                log("board disconnected")
                self.close()
                continue
            if not raw:
                continue
            text = raw.decode(errors="replace").strip()
            try:
                msg = json.loads(text)
            except Exception:
                continue
            if msg.get("type") == "ack":
                with self.ack_cv:
                    self.acks.append(msg["payload"])
                    self.ack_cv.notify_all()
            elif msg.get("type") == "event" and msg["payload"].get("key") == "check":
                port, what = str(msg["payload"]["value"]).split(":")
                board.check[port] = what
                board.check_at = time.strftime("%H:%M:%S")
                if port == "14":
                    log("wiring check: " + ", ".join(f"{p}={w}" for p, w in board.check.items()))
            elif msg.get("type") == "event":
                v = msg["payload"].get("value")
                if not (isinstance(v, str) and v.startswith("hello")):
                    log(f"board: {v}")
                else:
                    board.last_hello = v
            elif msg.get("type") == "boot":
                log(f"board booted (reset: {msg['payload'].get('reset_reason')})")

    def call(self, action, value=""):
        with self.lock:
            if not self.ser:
                return {"ok": False, "error": "no board on USB"}
            with self.ack_cv:
                self.acks.clear()
            line = json.dumps({"action": action, "value": str(value)}) + "\n"
            try:
                self.ser.write(line.encode())
            except Exception as e:
                return {"ok": False, "error": str(e)}
            deadline = time.time() + 3
            with self.ack_cv:
                while time.time() < deadline:
                    for a in list(self.acks):
                        if a.get("action") == action:
                            self.acks.remove(a)
                            return {"ok": bool(a.get("ok")), "error": a.get("error")}
                    self.ack_cv.wait(0.1)
            return {"ok": False, "error": "no answer from the board"}


board = BoardLink()
board.last_hello = ""
board.check = {}
board.check_at = ""
flash_state = {"running": False, "output": ""}


# MG90S: 0..180 deg = 500..2400 us; never pulse it outside that (it stalls against its end stop)
MG90S_MIN_US, MG90S_MAX_US = 500, 2400


def mg90s_us(deg):
    return round(MG90S_MIN_US + float(deg) * (MG90S_MAX_US - MG90S_MIN_US) / 180)


def load_config():
    cfg = json.loads(CONFIG.read_text()) if CONFIG.exists() else json.loads(json.dumps(DEFAULT))
    cfg.setdefault("version", 1)
    cfg.setdefault("status", {})
    for j in cfg["joints"].values():
        # the defaults (and older configs) hold degrees: stored as an MG90S pulse
        if "neutral_us" not in j:
            j["neutral_us"] = mg90s_us(j.pop("neutral", 90))
        j.setdefault("us0", MG90S_MIN_US)
        j.setdefault("us180", MG90S_MAX_US)
        j.setdefault("min_us", MG90S_MIN_US)
        j.setdefault("max_us", MG90S_MAX_US)
        for k in ("us0", "us180", "min_us", "max_us", "neutral_us"):
            j[k] = max(MG90S_MIN_US, min(MG90S_MAX_US, int(j[k])))
    return cfg


def write_project(cfg):
    names = JOINTS
    pins = [str(cfg["joints"][n]["pin"]) for n in names]
    ints = lambda key: ", ".join(str(int(cfg["joints"][n][key])) for n in names)
    block = (
        "    // CONFIG BEGIN (written by rig_server.py)\n"
        f"    static const char* const JOINT_NAMES[8] = {{{', '.join(json.dumps(n) for n in names)}}};\n"
        f"    static const char* const JOINT_PINS[8] = {{{', '.join(json.dumps(p) for p in pins)}}};\n"
        f"    static const int JOINT_NEUTRAL_US[8] = {{{ints('neutral_us')}}};\n"
        f"    static const int JOINT_US0[8] = {{{ints('us0')}}};\n"
        f"    static const int JOINT_MIN_US[8] = {{{ints('min_us')}}};\n"
        f"    static const int JOINT_MAX_US[8] = {{{ints('max_us')}}};\n"
        f"    static const int JOINT_US180[8] = {{{ints('us180')}}};\n"
        "    // CONFIG END\n"
    )
    text = PROJECT.read_text()
    text = re.sub(r"    // CONFIG BEGIN.*?    // CONFIG END\n", block, text, flags=re.S)
    PROJECT.write_text(text)


def flash():
    flash_state.update(running=True, output="")
    board.paused = True
    board.close()
    time.sleep(0.5)
    log("flashing: atech upload crab_rig")
    p = subprocess.run(["atech", "upload", str(HERE)], capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip().splitlines()
    tail = "\n".join(out[-6:])
    flash_state.update(output=tail)
    log("flash " + ("done" if p.returncode == 0 else "FAILED") + ": " + (out[-1] if out else ""))
    time.sleep(2)
    board.paused = False
    flash_state["running"] = False


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/state":
            return self._send(200, {
                "config": load_config(),
                "connected": board.ser is not None and not board.paused,
                "port": board.ser.port if board.ser else None,
                "hello": board.last_hello,
                "check": board.check,
                "check_at": board.check_at,
                "flash": flash_state,
                "log": list(board.recent)[-80:],
            })
        self._send(404, {"error": "not found"})

    def do_POST(self):
        body = self._body()
        if self.path == "/api/cmd":
            r = board.call(body["action"], body.get("value", ""))
            if not body.get("quiet"):
                log(f"{body['action']} {body.get('value', '')} -> " + ("ok" if r["ok"] else f"FAILED: {r['error']}"))
            return self._send(200, r)
        if self.path == "/api/status":
            # status only: saved at once, leaves the map, the stand values and the version alone
            cfg = load_config()
            cfg["status"][body["joint"]] = body.get("status", "")
            CONFIG.write_text(json.dumps(cfg, indent=2))
            log(f"status: {body['joint']} = {body.get('status') or 'untested'}")
            return self._send(200, {"ok": True})
        if self.path == "/api/note":
            log(f"NOTE: {body.get('text', '')}")
            return self._send(200, {"ok": True})
        if self.path == "/api/save":
            cfg = body["config"]
            current = load_config()
            if cfg.get("version") != current["version"]:
                log("save refused: that page was out of date (it reloads now)")
                return self._send(409, {"ok": False, "error": "stale"})
            cfg["version"] = current["version"] + 1
            CONFIG.write_text(json.dumps(cfg, indent=2))
            write_project(cfg)
            log(f"saved rig_config.json v{cfg['version']}: " + ", ".join(f"{n}={cfg['joints'][n]['pin']}@{cfg['joints'][n]['neutral_us']}us" for n in JOINTS))
            if body.get("flash") and not flash_state["running"]:
                threading.Thread(target=flash, daemon=True).start()
            return self._send(200, {"ok": True, "version": cfg["version"]})
        self._send(404, {"error": "not found"})


if __name__ == "__main__":
    if not CONFIG.exists():
        CONFIG.write_text(json.dumps(DEFAULT, indent=2))
    log(f"rig server on http://localhost:{PORT_HTTP}")
    ThreadingHTTPServer(("127.0.0.1", PORT_HTTP), Handler).serve_forever()
