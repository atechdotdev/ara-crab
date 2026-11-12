"""Servo test control page: eight MG90S on ports 1-6, 13, 14 and the screen on 9+10.

    python3 control.py            # then open http://localhost:8766

The server holds the board's USB port (close `atech monitor` first) and reconnects by itself
when the board comes back. The page moves each servo, runs the test modes and flashes
project.yaml. The board reports its eight angles 5 times a second; the page draws them live.
Calibration (which leg and joint each port is, its true 90 deg, its limits) is saved to
calibration.json at every change.
"""
import glob
import sys
import json
import subprocess
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import serial

HERE = Path(__file__).resolve().parent
PAGE = HERE / "control.html"
CAL = HERE / "calibration.json"
SNAPS = HERE / "calibrations"          # former calibrations, one file each
MAKE = HERE / "make_project.py"
SETTINGS = HERE / "settings.json"      # servos moving at once, speed
# the page's joint names -> Sesame's channel numbers (R1 R2 L1 L2 R4 R3 L3 L4 = 0..7)
SESAME = {"FR hip": 0, "BR hip": 1, "FL hip": 2, "BL hip": 3,
          "BR knee": 4, "FR knee": 5, "FL knee": 6, "BL knee": 7}
PORT_HTTP = 8766
PORTS = [1, 2, 3, 4, 5, 6, 13, 14]


class Board:
    def __init__(self):
        self.ser = None
        self.lock = threading.Lock()
        self.acks = deque()
        self.cv = threading.Condition()
        self.paused = False
        self.angles = [None] * len(PORTS)
        self.step = ""
        self.angles_at = 0.0
        self.boots = 0
        self.log = deque(maxlen=200)
        self.need_cal = True
        threading.Thread(target=self._reader, daemon=True).start()

    def note(self, line):
        self.log.append(f"{time.strftime('%H:%M:%S')} {line}")

    def _open(self):
        devs = sorted(glob.glob("/dev/cu.usbmodem*"))
        if not devs:
            return False
        s = serial.Serial()
        s.port, s.baudrate, s.timeout = devs[0], 115200, 0.2
        s.dtr = s.rts = False                    # don't reset the board on open
        s.open()
        self.ser = s
        self.need_cal = True
        self.note(f"connected to {devs[0]}")
        return True

    def close(self):
        try:
            if self.ser:
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
                        time.sleep(0.5)
                        continue
                except Exception:
                    time.sleep(0.5)
                    continue
            try:
                raw = self.ser.readline()
            except Exception:
                if not self.paused:
                    self.note("USB dropped (too much servo current on USB power?)")
                self.close()
                continue
            if not raw:
                continue
            line = raw.decode(errors="replace").strip()
            try:
                msg = json.loads(line)
            except Exception:
                # the chip's own text: reset cause, brownout, crash report
                if any(k in line for k in ("rst:", "Brownout", "brownout", "Guru", "panic", "Backtrace",
                                           "abort", "Exception", "watchdog", "WDT", "assert")):
                    self.note("chip: " + line[:200])
                continue
            t, p = msg.get("type"), msg.get("payload", {})
            if t == "ack":
                with self.cv:
                    self.acks.append(p)
                    self.cv.notify_all()
            elif t == "boot":
                self.boots += 1
                self.need_cal = True
                bad = [m["instance"] for m in p.get("modules", []) if not m.get("ok")]
                self.note(f"board started (reset: {p.get('reset_reason')}); "
                          + ("all modules ok" if not bad else "not ok: " + ", ".join(bad)))
            elif t == "event" and p.get("key") == "angles":
                self.angles, self.angles_at = p["value"], time.time()
            elif t == "event" and p.get("key") == "test":
                self.step = p["value"]
                self.note(f"board: {p['value']}")

    def call(self, action, value=""):
        with self.lock:
            if not self.ser:
                return {"ok": False, "error": "no board on USB"}
            with self.cv:
                self.acks.clear()
            try:
                self.ser.write((json.dumps({"action": action, "value": str(value)}) + "\n").encode())
            except Exception as e:
                return {"ok": False, "error": str(e)}
            end = time.time() + 2
            with self.cv:
                while time.time() < end:
                    for a in list(self.acks):
                        if a.get("action") == action:
                            self.acks.remove(a)
                            return {"ok": bool(a.get("ok")), "error": a.get("error")}
                    self.cv.wait(0.05)
            return {"ok": False, "error": "no answer from the board"}


board = Board()


def load_cal():
    if CAL.exists():
        return json.loads(CAL.read_text())
    return {"version": 0, "servos": {}}


cal_lock = threading.Lock()


def load_settings():
    d = {"max_moving": 4, "speed": 300, "amount": 50}
    if SETTINGS.exists():
        d.update(json.loads(SETTINGS.read_text()))
    return d


def push_limit():
    st = load_settings()
    r = board.call("limit", f"{int(st['max_moving'])},{int(st['speed'])},{int(st['amount'])}")
    board.note(f"moves: at most {st['max_moving']} servos at once, {st['speed']} deg/s, {st['amount']} % swing"
               + ("" if r["ok"] else f" -> FAILED: {r['error']}"))


def push_cal():
    """Send every port's calibration to the board and store it in its flash."""
    cal = load_cal()
    sent = []
    for port in PORTS:
        c = cal["servos"].get(str(port), {})
        joint = SESAME.get(c.get("joint", ""), -1)
        v = (f"{port},{joint},{int(c.get('neutral', 90))},{-1 if c.get('reversed') else 1},"
             f"{int(c.get('min', 0))},{int(c.get('max', 180))}")
        r = board.call("cal", v)
        if not r["ok"]:
            return board.note(f"calibration not sent: {r['error']}")
        if joint >= 0:
            sent.append(f"P{port}={c['joint']}")
    board.call("calsave")
    board.note(f"calibration v{cal['version']} on the board: " + (", ".join(sent) or "no joints named"))


def cal_pusher():
    while True:
        time.sleep(0.3)
        if board.need_cal and board.ser and not board.paused:
            board.need_cal = False
            time.sleep(0.5)          # let the board finish starting
            push_cal()
            push_limit()


threading.Thread(target=cal_pusher, daemon=True).start()


def snapshot(name):
    SNAPS.mkdir(exist_ok=True)
    safe = "".join(ch for ch in name if ch.isalnum() or ch in " -_.")[:60].strip() or "calibration"
    path = SNAPS / f"{time.strftime('%Y-%m-%d_%H%M%S')} {safe}.json"
    path.write_text(CAL.read_text() if CAL.exists() else json.dumps(load_cal()))
    return path.name
flash_state = {"running": False, "output": ""}


def flash():
    flash_state.update(running=True, output="")
    board.paused = True
    board.close()
    time.sleep(0.4)
    board.note("flashing project.yaml ...")
    subprocess.run([sys.executable, str(MAKE)], capture_output=True, text=True)
    p = subprocess.run(["atech", "upload", str(HERE)], capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip().splitlines()
    flash_state["output"] = "\n".join(out[-4:])
    board.note("flash " + ("done" if p.returncode == 0 else "FAILED: " + (out[-1] if out else "")))
    time.sleep(1.5)
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

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/cal":
            return self._send(200, load_cal())
        if self.path == "/api/settings":
            return self._send(200, load_settings())
        if self.path == "/api/snapshots":
            files = sorted(SNAPS.glob("*.json"), reverse=True) if SNAPS.exists() else []
            out = []
            for f in files:
                try:
                    d = json.loads(f.read_text())
                    n = sum(1 for c in d.get("servos", {}).values() if c.get("joint"))
                except Exception:
                    n = 0
                out.append({"file": f.name, "joints": n})
            return self._send(200, out)
        if self.path == "/api/state":
            return self._send(200, {
                "connected": board.ser is not None and not board.paused,
                "port": board.ser.port if board.ser else None,
                "ports": PORTS,
                "angles": board.angles,
                "live": time.time() - board.angles_at < 1.0,
                "step": board.step,
                "boots": board.boots,
                "flash": flash_state,
                "log": list(board.log)[-60:],
            })
        self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/api/cmd":
            r = board.call(body["action"], body.get("value", ""))
            if not body.get("quiet"):
                board.note(f"sent {body['action']} {body.get('value', '')}"
                           + ("" if r["ok"] else f" -> FAILED: {r['error']}"))
            return self._send(200, r)
        if self.path == "/api/cal":
            # one servo's calibration: {"port": 3, "joint": "FL hip", "neutral": 92, "min": .., "max": .., "reversed": false}
            with cal_lock:
                cal = load_cal()
                port = str(body.pop("port"))
                entry = cal["servos"].get(port, {})
                entry.update(body)
                entry["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
                cal["servos"][port] = entry
                cal["version"] += 1
                CAL.write_text(json.dumps(cal, indent=2))
            changed = ", ".join(f"{k}={v}" for k, v in body.items())
            board.note(f"calibration: port {port}: {changed}")
            board.need_cal = True
            return self._send(200, cal)
        if self.path == "/api/settings":
            st = load_settings()
            st.update({k: int(v) for k, v in body.items() if k in ("max_moving", "speed", "amount")})
            SETTINGS.write_text(json.dumps(st, indent=2))
            push_limit()
            return self._send(200, st)
        if self.path == "/api/snapshot":
            name = snapshot(body.get("name", ""))
            board.note(f"calibration saved as {name}")
            return self._send(200, {"ok": True, "file": name})
        if self.path == "/api/restore":
            src = SNAPS / Path(body["file"]).name
            if not src.exists():
                return self._send(404, {"ok": False, "error": "no such calibration"})
            with cal_lock:
                before = snapshot("before restore")
                d = json.loads(src.read_text())
                d["version"] = load_cal()["version"] + 1
                CAL.write_text(json.dumps(d, indent=2))
            board.note(f"restored {src.name} (the one before is kept as {before})")
            board.need_cal = True
            return self._send(200, {"ok": True})
        if self.path == "/api/go":
            r = board.call("go", body.get("move", "stand"))
            board.note(f"move {body.get('move')}" + ("" if r["ok"] else f" -> FAILED: {r['error']}"))
            return self._send(200, r)
        if self.path == "/api/flash":
            if not flash_state["running"]:
                threading.Thread(target=flash, daemon=True).start()
            return self._send(200, {"ok": True})
        self._send(404, {"error": "not found"})


if __name__ == "__main__":
    print(f"servo test control on http://localhost:{PORT_HTTP}")
    ThreadingHTTPServer(("127.0.0.1", PORT_HTTP), Handler).serve_forever()
