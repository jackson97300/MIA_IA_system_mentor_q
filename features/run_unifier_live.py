#!/usr/bin/env python3
# Run the unifier every minute (no .bat needed)
import time, datetime, subprocess, sys, os

BASE = r"D:\MIA_IA_system"
PY = sys.executable  # current Python interpreter path

def today():
    return datetime.datetime.now().strftime("%Y%m%d")

while True:
    ymd = today()
    cmd = [
        PY, os.path.join(BASE, "mia_unifier.py"),
        "--indir", BASE, "--date", ymd,
        "--menthorq-alerts",
        "--tick-size", "0.25",
        "--confluence-thr", "3",
        "--cluster-min-levels", "2",
        "--cluster-thr", "3"
    ]
    try:
        subprocess.run(cmd, check=False)
    except Exception as e:
        print("unifier run error:", e)
    time.sleep(60)
