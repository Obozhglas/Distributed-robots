import tkinter as tk
import random
import math
from robot.heartbeat import update_heartbeats, detect_failures
from robot.agent import run_auction


# --------------------------
# TASK MODEL
# --------------------------
class Task:
    def __init__(self, task_id, x, y, target_id):
        self.id = task_id
        self.x = x
        self.y = y
        self.target_id = target_id

        self.history = []     # история переназначений
        self.trail = []       # след движения
        self.color = "blue"   # цвет задачи


class GUI:
    def __init__(self, robots, env):
        self.robots = robots
        self.env = env

        self.root = tk.Tk()
        self.root.title("Distributed Robot System - Balanced Flow")

        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg="white")
        self.canvas.pack()

        self.robot_pos = {}
        self.tasks = []
        self.task_id = 0

        self.init_layout()
        self.create_controls()

    # --------------------------
    # РУЧНОЕ УПРАВЛЕНИЕ
    # --------------------------
    def create_controls(self):
        frame = tk.Frame(self.root)
        frame.pack()

        for r in self.robots:
            tk.Button(
                frame,
                text=f"FAIL {r.id}",
                command=lambda rr=r: self.set_robot_state(rr.id, "FAILED")
            ).pack(side=tk.LEFT)

            tk.Button(
                frame,
                text=f"OK {r.id}",
                command=lambda rr=r: self.set_robot_state(rr.id, "IDLE")
            ).pack(side=tk.LEFT)

    def set_robot_state(self, robot_id, state):
        for r in self.robots:
            if r.id == robot_id:
                r.status = state
                if state == "FAILED":
                    r.load = 0

    # --------------------------
    # ЛОКАЦИЯ
    # --------------------------
    def init_layout(self):
        spacing = 250
        for i, r in enumerate(self.robots):
            x = 150 + i * spacing
            y = 450
            self.robot_pos[r.id] = (x, y)

    # --------------------------
    # БАЛАНСИРОВКА РОБОТОВ
    # --------------------------
    def choose_robot(self):
        candidates = [r for r in self.robots if r.status != "FAILED"]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda r: (r.load, random.random())
        ).id

    def rebalance_tasks(self):
    alive = [r for r in self.robots if r.status != "FAILED"]

    if not alive:
        return

    for t in self.tasks:
        target_robot = next((r for r in self.robots if r.id == t.target_id), None)

        if target_robot and target_robot.status != "FAILED":
            continue

        new_target = min(alive, key=lambda r: r.load).id

        if new_target != t.target_id:
            t.history.append(t.target_id)
            t.target_id = new_target
            t.color = "purple"  

    # --------------------------
    # ЗАДАЧИ
    # --------------------------
    def spawn_task(self):
        winner = self.choose_robot()
        if winner is None:
            return

        self.tasks.append(Task(
            self.task_id,
            500,
            50,
            winner
        ))

        self.task_id += 1

    def update_tasks(self):
        self.rebalance_tasks()

        speed = 4

        for t in self.tasks[:]:
            target_robot = next(
                (r for r in self.robots if r.id == t.target_id),
                None
            )

            if target_robot is None or target_robot.status == "FAILED":
                new_target = self.choose_robot()
                if new_target:
                    t.history.append(t.target_id)
                    t.target_id = new_target
                    t.color = "purple"
                continue

            tx, ty = self.robot_pos[t.target_id]

            dx = tx - t.x
            dy = ty - t.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 10:
                self.tasks.remove(t)
                target_robot.assign_task("task")
                continue

            t.trail.append((t.x, t.y))
            if len(t.trail) > 10:
                t.trail.pop(0)

    # --------------------------
    # РЕНДЕР
    # --------------------------
    def draw_robots(self):
        for r in self.robots:
            x, y = self.robot_pos[r.id]

            color = "green"
            if r.status == "FAILED":
                color = "red"
            elif r.status == "BUSY":
                color = "orange"

            self.canvas.create_oval(x-35, y-35, x+35, y+35, fill=color)
            self.canvas.create_text(x, y, text=r.id)
            self.canvas.create_text(x, y+50, text=f"load:{r.load}")

    def draw_tasks(self):
    for t in self.tasks:
        tx, ty = self.robot_pos[t.target_id]

        # линия направления
        self.canvas.create_line(
            t.x, t.y,
            tx, ty,
            dash=(2, 2),
            fill="gray"
        )

        # след движения
        for i in range(len(t.trail) - 1):
            x1, y1 = t.trail[i]
            x2, y2 = t.trail[i + 1]

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill="lightblue"
            )

        # сама задача
        self.canvas.create_oval(
            t.x-5, t.y-5,
            t.x+5, t.y+5,
            fill=t.color
        )

    # --------------------------
    # ЦИКЛ
    # --------------------------
    def update(self):
        self.canvas.delete("all")

        # входной поток
        for i in range(10):
            self.canvas.create_oval(
                100 + i*80, 20,
                110 + i*80, 30,
                fill="lightgray"
            )

        self.canvas.create_text(500, 10, text="Incoming Flow")

        update_heartbeats(self.robots)
        detect_failures(self.robots)

        if random.random() < 0.25:
            self.spawn_task()

        self.draw_robots()
        self.update_tasks()
        self.draw_tasks()

        self.root.after(50, self.update)

    def run(self):
        self.update()
        self.root.mainloop()
