"""Heartbeat for the Redlog CAD run.

FIXED after it misled me: the first version recorded the SIZE OF THE LOG FILE, which
never changes because Redlog buffers its output until a phase ends.  A run at 100% of a
core for fifty minutes looked identical to a dead one.  L32 says measure a delta, and the
metric has to be one that actually moves: this records CPU TIME.
"""
import json, os, time, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
LOG = r'C:\TEMP\claude\C--Users-Tyrant-Desktop-erdos-stuff\0f8429fa-27a0-4b48-9c61-1b012fe4813e\scratchpad\qe_out.log'
OUT = 'results/qe_typeIII_progress.json'
t0 = time.time()
hist = []
while True:
    alive = 'bpsl.exe' in subprocess.run(['tasklist', '/FI', 'IMAGENAME eq bpsl.exe'],
                                         capture_output=True, text=True).stdout
    sz = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    tail = ''
    if sz:
        with open(LOG, 'rb') as f:
            f.seek(max(0, sz - 400)); tail = f.read().decode('utf-8', 'replace')
    cpu = mb = 0.0
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command',
                            "$p=Get-CimInstance Win32_Process -Filter \"Name='bpsl.exe'\";"
                            "if($p){'{0} {1}' -f $p.UserModeTime,$p.WorkingSetSize}"],
                           capture_output=True, text=True, timeout=30).stdout.split()
        if len(r) == 2:
            cpu, mb = float(r[0]) / 1e7, float(r[1]) / 1048576
    except Exception:
        pass
    prev = hist[-1]['cpu_s'] if hist else 0.0
    hist.append(dict(t=round(time.time() - t0, 1), bytes=sz, alive=alive,
                     cpu_s=round(cpu, 1), mb=round(mb), d_cpu=round(cpu - prev, 1)))
    print('  t=%6.0fs  cpu=%8.0fs (+%5.1f)  mem=%5dMB  log=%d' %
          (time.time() - t0, cpu, cpu - prev, mb, sz), flush=True)
    json.dump(dict(history=hist[-200:], last_tail=tail, alive=alive,
                   completed=(not alive)), open(OUT, 'w'), indent=1)
    if not alive:
        print('bpsl exited after %.0f s' % (time.time() - t0), flush=True)
        break
    if time.time() - t0 > 20000:
        print('watch giving up at %.0f s; process still alive' % (time.time() - t0), flush=True)
        break
    time.sleep(60)
