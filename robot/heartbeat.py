import time
from config import TIMEOUT

def update_heartbeats(robots):
    for r in robots:
        if r.status != "FAILED":
            r.heartbeat()

def detect_failures(robots):
    for r in robots:
        if r.status != "FAILED":
            if not r.is_alive(TIMEOUT):
                r.status = "FAILED"