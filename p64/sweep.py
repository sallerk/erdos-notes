"""Drive run.py over a range of n, logging as we go."""
import subprocess
import sys
import time

ns = [int(x) for x in sys.argv[1].split(",")]
split = sys.argv[2] if len(sys.argv) > 2 else "14"
workers = sys.argv[3] if len(sys.argv) > 3 else "5"

log = open("results/sweep.log", "a", buffering=1)
for n in ns:
    t = time.time()
    p = subprocess.run([sys.executable, "run.py", str(n), split, workers],
                       capture_output=True, text=True)
    msg = p.stdout + p.stderr
    print(f"===== n={n}  ({time.time()-t:.1f}s) =====", flush=True)
    print(msg, flush=True)
    log.write(f"===== n={n}  ({time.time()-t:.1f}s) =====\n{msg}\n")
    if p.returncode != 0:
        print("ABORT: run.py failed", flush=True)
        break
