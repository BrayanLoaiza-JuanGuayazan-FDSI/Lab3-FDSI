#!/usr/bin/env python3
"""Regla de detección del laboratorio: >= 5 respuestas 404 de una misma IP en 5 minutos.

Uso:  python3 detect_404.py /var/log/nginx/lab3_access.log
"""
import re
import sys
from collections import defaultdict, deque
from datetime import datetime, timedelta

THRESHOLD = 5
WINDOW = timedelta(minutes=5)
LINE = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+)[^"]*" (\d{3}) ')

path = sys.argv[1] if len(sys.argv) > 1 else "/var/log/nginx/lab3_access.log"
events = defaultdict(deque)
alerted = set()

with open(path, encoding="utf-8", errors="replace") as f:
    for raw in f:
        m = LINE.match(raw)
        if not m or m.group(5) != "404":
            continue
        ip, stamp, method, uri = m.group(1), m.group(2), m.group(3), m.group(4)
        t = datetime.strptime(stamp, "%d/%b/%Y:%H:%M:%S %z")
        q = events[ip]
        q.append((t, method, uri))
        while q and t - q[0][0] > WINDOW:
            q.popleft()
        if len(q) >= THRESHOLD and ip not in alerted:
            alerted.add(ip)
            rutas = sorted({u for _, _, u in q})
            print(f"ALERTA {t.isoformat()} ip={ip} 404s_en_5min={len(q)} rutas={rutas}")

if not alerted:
    print("Sin alertas.")
