"""Runs a TownBuilder script and records the outcome in Saved/TownBuilder/last_run.txt.

    py exec(open(r'D:/StartOfTheJourney 5.8/Tools/TownBuilder/run.py').read()); run('dump_props.py')
"""
import sys
import traceback

import unreal

TOOLS_DIR = "D:/StartOfTheJourney 5.8/Tools/TownBuilder/"


def run(script, *args):
    status = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "TownBuilder/last_run.txt"
    sys.argv = [script, *args]
    try:
        with open(TOOLS_DIR + script, encoding="utf-8") as f:
            code = compile(f.read(), TOOLS_DIR + script, "exec")
        exec(code, {"__name__": "__main__", "__file__": TOOLS_DIR + script})
        msg = f"OK {script}\n"
    except Exception:
        msg = f"FAIL {script}\n{traceback.format_exc()}"
    with open(status, "w", encoding="utf-8") as f:
        f.write(msg)
