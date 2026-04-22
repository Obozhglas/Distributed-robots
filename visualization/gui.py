import tkinter as tk
import random
import math
from robot.heartbeat import update_heartbeats, detect_failures


# --------------------------
# TASK MODEL
# --------------------------
class Task:
    def __init__(self, task_id, x, y, target_id):
        self.id = task_id
        self.x = x
        self.y = y
        self.target_id = target_id

        self.history = []
        self.trail = []
        self.color = "blue"


# --------------------------
# GUI
# --------------------------
class GUI:
    def __init__(self, robots, env):
        self.robots = robots
        self.env = env

        self.root = tk.Tk()
        self.root.title("Distributed Robot System - Parallel Execution")

        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg="white")
        self.canvas.pack()

        self.robot_pos = {}
        self.tasks = []
        self.task_id = 0

        # init load tracking
        for r in self.robots:
            r.load = 0

        self.init_layout()
        self.create_controls()

    # --------------------------
    # CONTROLS
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
    # LAYOUT
    # --------------------------
    def init_layout(self):
        spacing = 250
        for i, r in enumerate(self.robots):
            x = 150 + i * spacing
            y = 450
            self.robot_pos[r.id] = (x, y)

    # --------------------------
    # PARALLEL TASK ASSIGNMENT (KEY FIX)
    # --------------------------
    def assign_task_to_robot(self, task):
        alive = [r for r in self.robots if r.status != "FAILED"]

        if not alive:
            return

        robot = min(alive, key=lambda r: r.load)

        task.target_id = robot.id
        robot.load += 1

    # --------------------------
    # TASK CREATION
    # --------------------------
    def spawn_task(self):
        t = Task(self.task_id, 500, 50, None)

        self.assign_task_to_robot(t)

        self.tasks.append(t)
        self.task_id += 1

    # --------------------------
    # TASK UPDATE
    # --------------------------
    def update_tasks(self):
        speed = 4

        for t in self.tasks[:]:
            target_robot = next((r for r in self.robots if r.id == t.target_id), None)

            if target_robot is None or target_robot.status == "FAILED":
                self.assign_task_to_robot(t)
                t.color = "purple"
                continue

            if t.target_id not in self.robot_pos:
                continue

            tx, ty = self.robot_pos[t.target_id]

            dx = tx - t.x
            dy = ty - t.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 10:
                if t in self.tasks:
                    self.tasks.remove(t)

                target_robot.load = max(0, target_robot.load - 1)
                continue

            if dist != 0:
                t.x += (dx / dist) * speed
                t.y += (dy / dist) * speed

            t.trail.append((t.x, t.y))
            if len(t.trail) > 10:
                t.trail.pop(0)

    # --------------------------
    # DRAW ROBOTS
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

    # --------------------------
    # DRAW TASKS
    # --------------------------
    def draw_tasks(self):
        for t in self.tasks:
            if t.target_id not in self.robot_pos:
                continue

            tx, ty = self.robot_pos[t.target_id]

            self.canvas.create_line(
                t.x, t.y,
                tx, ty,
                dash=(2, 2),
                fill="gray"
            )

            for i in range(len(t.trail) - 1):
                x1, y1 = t.trail[i]
                x2, y2 = t.trail[i + 1]

                self.canvas.create_line(x1, y1, x2, y2, fill="lightblue")

            self.canvas.create_oval(
                t.x-5, t.y-5,
                t.x+5, t.y+5,
                fill=t.color
            )

    # --------------------------
    # MAIN LOOP
    # --------------------------
    def update(self):
        self.canvas.delete("all")

        # heartbeat system
        update_heartbeats(self.robots)
        detect_failures(self.robots)

        # parallel task generation
        if random.random() < 0.25:
            self.spawn_task()

        # background flow
        for i in range(10):
            self.canvas.create_oval(
                100 + i*80, 20,
                110 + i*80, 30,
                fill="lightgray"
            )

        self.canvas.create_text(500, 10, text="Incoming Flow")

        self.draw_robots()
        self.update_tasks()
        self.draw_tasks()

        self.root.after(50, self.update)

    def run(self):
        self.update()
        self.root.mainloop()