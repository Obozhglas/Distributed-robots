import time

class Robot:
    def __init__(self, robot_id):
        self.id = robot_id
        self.load = 0
        self.status = "IDLE"
        self.current_task = None
        self.last_heartbeat = time.time()

    def heartbeat(self):
        self.last_heartbeat = time.time()

    def is_alive(self, timeout):
        return (time.time() - self.last_heartbeat) < timeout

    def assign_task(self, task):
        self.current_task = task
        self.status = "BUSY"
        self.load += 1

    def finish_task(self):
        self.current_task = None
        self.status = "IDLE"
        self.load = max(0, self.load - 1)