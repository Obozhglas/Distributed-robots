import time
from simulation.task import Task
from robot.agent import run_auction

class Environment:
    def __init__(self, robots):
        self.robots = robots
        self.task_id = 0
        self.queue = []

    def generate_task(self):
        task = Task(self.task_id)
        self.task_id += 1
        self.queue.append(task)
        return task

    def assign_tasks(self):
        if not self.queue:
            return None

        task = self.queue.pop(0)

        winner, bids = run_auction(self.robots)

        if winner is None:
            self.queue.insert(0, task)
            return None

        for r in self.robots:
            if r.id == winner:
                r.assign_task(task)

        return winner, bids, task

    def process_tasks(self):
        for r in self.robots:
            if r.status == "BUSY":
                r.finish_task()