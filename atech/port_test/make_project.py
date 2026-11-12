"""Write project.yaml from project.in.yaml: Sesame's moves go in at %MOVES%.

    python3 make_project.py

The moves come from this repository's firmware/movement-sequences.h (Sesame, Dorian Todd,
Apache-2.0), played through by atech/firmware/make_firmware.py into keyframes. Edit
project.in.yaml, not project.yaml. The control page's Flash button runs this first.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "firmware"))
import make_firmware as mf  # noqa: E402


def main():
    moves = mf.moves_cpp(mf._bodies(mf.SEQUENCES.read_text()))
    tpl = (HERE / "project.in.yaml").read_text()
    assert "    %MOVES%" in tpl
    text = tpl.replace("    %MOVES%", "\n".join("    " + line for line in moves.splitlines()))
    (HERE / "project.yaml").write_text("# Written by make_project.py from project.in.yaml: edit that file.\n" + text)
    print("wrote project.yaml")


if __name__ == "__main__":
    main()
