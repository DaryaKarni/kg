import tkinter as tk
from tkinter import ttk, messagebox
import time
import math

WIDTH, HEIGHT = 800, 800
CELL_SIZE = 20
GRID_MIN, GRID_MAX = -20, 20

X0 = WIDTH // 2
Y0 = HEIGHT // 2


def grid_to_screen(x, y):
    sx = X0 + x * CELL_SIZE
    sy = Y0 - y * CELL_SIZE
    return sx, sy


def draw_grid(canvas):
    canvas.delete("all")
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="white", outline="")

    for gx in range(GRID_MIN, GRID_MAX + 1):
        sx1, sy1 = grid_to_screen(gx, GRID_MIN)
        sx2, sy2 = grid_to_screen(gx, GRID_MAX)
        canvas.create_line(sx1, sy1, sx2, sy2, fill="#dddddd")

    for gy in range(GRID_MIN, GRID_MAX + 1):
        sx1, sy1 = grid_to_screen(GRID_MIN, gy)
        sx2, sy2 = grid_to_screen(GRID_MAX, gy)
        canvas.create_line(sx1, sy1, sx2, sy2, fill="#dddddd")

    sx1, sy1 = grid_to_screen(GRID_MIN, 0)
    sx2, sy2 = grid_to_screen(GRID_MAX, 0)
    canvas.create_line(sx1, sy1, sx2, sy2, width=2, fill="black")

    sx1, sy1 = grid_to_screen(0, GRID_MIN)
    sx2, sy2 = grid_to_screen(0, GRID_MAX)
    canvas.create_line(sx1, sy1, sx2, sy2, width=2, fill="black")

    for v in range(GRID_MIN, GRID_MAX + 1, 5):
        if v == 0:
            continue
        sx, sy = grid_to_screen(v, 0)
        canvas.create_text(sx, sy + 10, text=str(v), fill="black", font=("Arial", 8))
        sx, sy = grid_to_screen(0, v)
        canvas.create_text(sx - 10, sy, text=str(v), fill="black", font=("Arial", 8))

    canvas.create_text(X0 + (GRID_MAX - 1) * CELL_SIZE, Y0 + 15,
                       text="X", font=("Arial", 10, "bold"))
    canvas.create_text(X0 - 15, Y0 - (GRID_MAX - 1) * CELL_SIZE,
                       text="Y", font=("Arial", 10, "bold"))


def draw_pixel(canvas, x, y, color="red"):
    if x < GRID_MIN or x >= GRID_MAX or y < GRID_MIN or y >= GRID_MAX:
        return

    x1 = X0 + x * CELL_SIZE
    x2 = X0 + (x + 1) * CELL_SIZE
    y2 = Y0 - y * CELL_SIZE
    y1 = Y0 - (y + 1) * CELL_SIZE

    canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)


def step_by_step_line(x1, y1, x2, y2):
    points = []

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return [(x1, y1)]

    if abs(dx) >= abs(dy):
        k = dy / dx
        b = y1 - k * x1
        step = 1 if x2 >= x1 else -1
        x = x1
        while True:
            y = k * x + b
            points.append((int(round(x)), int(round(y))))
            if x == x2:
                break
            x += step
    else:
        k = dx / dy
        b = x1 - k * y1
        step = 1 if y2 >= y1 else -1
        y = y1
        while True:
            x = k * y + b
            points.append((int(round(x)), int(round(y))))
            if y == y2:
                break
            y += step

    return points


def dda_line(x1, y1, x2, y2):
    points = []

    dx = x2 - x1
    dy = y2 - y1

    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        return [(x1, y1)]

    x_inc = dx / steps
    y_inc = dy / steps

    x = x1
    y = y1
    for _ in range(steps + 1):
        points.append((int(round(x)), int(round(y))))
        x += x_inc
        y += y_inc

    return points


def bresenham_line(x1, y1, x2, y2):
    points = []

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    x, y = x1, y1
    while True:
        points.append((x, y))
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    return points


def castle_pitway_line(x1, y1, x2, y2):
    return bresenham_line(x1, y1, x2, y2)


def bresenham_circle(xc, yc, r):
    points = []

    x = 0
    y = r
    d = 3 - 2 * r

    def add_symmetry_points(cx, cy, x, y, container):
        container.extend([
            (cx + x, cy + y),
            (cx - x, cy + y),
            (cx + x, cy - y),
            (cx - x, cy - y),
            (cx + y, cy + x),
            (cx - y, cy + x),
            (cx + y, cy - x),
            (cx - y, cy - x),
        ])

    while x <= y:
        add_symmetry_points(xc, yc, x, y, points)
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1

    points = list(dict.fromkeys(points))
    return points


def timed(func, *args, **kwargs):
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    t1 = time.perf_counter()
    return result, (t1 - t0)


def blend_color(base_hex, alpha):
    base_hex = base_hex.lstrip("#")
    br = int(base_hex[0:2], 16)
    bg = int(base_hex[2:4], 16)
    bb = int(base_hex[4:6], 16)

    fr, fg, fb = 255, 255, 255
    r = int(round(fr + (br - fr) * alpha))
    g = int(round(fg + (bg - fg) * alpha))
    b = int(round(fb + (bb - fb) * alpha))
    return f"#{r:02x}{g:02x}{b:02x}"


def wu_line(canvas, x0, y0, x1, y1, base_color="#ff0000"):
    if x0 == x1 or y0 == y1:
        pts = bresenham_line(x0, y0, x1, y1)
        for (x, y) in pts:
            draw_pixel(canvas, x, y, color=base_color)
        return len(pts)

    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 0.0

    def plot_alpha(px, py, alpha):
        if alpha <= 0:
            return
        if steep:
            px, py = py, px
        if px < GRID_MIN or px >= GRID_MAX or py < GRID_MIN or py >= GRID_MAX:
            return

        x1_ = X0 + px * CELL_SIZE
        x2_ = X0 + (px + 1) * CELL_SIZE
        y2_ = Y0 - py * CELL_SIZE
        y1_ = Y0 - (py + 1) * CELL_SIZE

        color = blend_color(base_color, max(0.0, min(1.0, alpha)))
        canvas.create_rectangle(x1_, y1_, x2_, y2_, fill=color, outline=color)

    count = 0

    for x in range(x0, x1 + 1):
        y_real = y0 + gradient * (x - x0)
        y_int = math.floor(y_real)
        frac = y_real - y_int
        plot_alpha(x, y_int, 1.0 - frac)
        plot_alpha(x, y_int + 1, frac)
        count += 2

    return count


class RasterApp:
    def __init__(self, root):
        self.root = root
        root.title("ЛР3: Базовые растровые алгоритмы")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=10)

        control = tk.Frame(root)
        control.grid(row=0, column=1, sticky="nw", padx=10, pady=10)

        tk.Label(control, text="Отрезок: (x1,y1) → (x2,y2)").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        tk.Label(control, text="x1").grid(row=1, column=0, sticky="e")
        tk.Label(control, text="y1").grid(row=2, column=0, sticky="e")
        tk.Label(control, text="x2").grid(row=3, column=0, sticky="e")
        tk.Label(control, text="y2").grid(row=4, column=0, sticky="e")

        self.x1_entry = tk.Entry(control, width=6)
        self.y1_entry = tk.Entry(control, width=6)
        self.x2_entry = tk.Entry(control, width=6)
        self.y2_entry = tk.Entry(control, width=6)

        self.x1_entry.grid(row=1, column=1)
        self.y1_entry.grid(row=2, column=1)
        self.x2_entry.grid(row=3, column=1)
        self.y2_entry.grid(row=4, column=1)

        tk.Label(control, text="Окружность: центр (xc,yc), R").grid(
            row=5, column=0, columnspan=2, sticky="w"
        )

        tk.Label(control, text="xc").grid(row=6, column=0, sticky="e")
        tk.Label(control, text="yc").grid(row=7, column=0, sticky="e")
        tk.Label(control, text="R").grid(row=8, column=0, sticky="e")

        self.xc_entry = tk.Entry(control, width=6)
        self.yc_entry = tk.Entry(control, width=6)
        self.r_entry = tk.Entry(control, width=6)

        self.xc_entry.grid(row=6, column=1)
        self.yc_entry.grid(row=7, column=1)
        self.r_entry.grid(row=8, column=1)

        tk.Label(control, text="Алгоритм для отрезка").grid(
            row=9, column=0, columnspan=2, sticky="w"
        )

        self.alg_var = tk.StringVar(value="step")
        alg_box = ttk.Combobox(
            control,
            textvariable=self.alg_var,
            state="readonly",
            values=[
                "step",
                "dda",
                "bresenham",
                "castle",
                "smooth",
            ],
            width=15,
        )
        alg_box.grid(row=10, column=0, columnspan=2, pady=3)

        self.info_label = tk.Label(control, text="Время: -", fg="blue")
        self.info_label.grid(row=11, column=0, columnspan=2, pady=5)

        tk.Button(
            control, text="Нарисовать отрезок", command=self.draw_line
        ).grid(row=12, column=0, columnspan=2, pady=3, sticky="we")
        tk.Button(
            control, text="Нарисовать окружность (Брезенхем)", command=self.draw_circle
        ).grid(row=13, column=0, columnspan=2, pady=3, sticky="we")
        tk.Button(
            control, text="Очистить", command=self.clear_canvas
        ).grid(row=14, column=0, columnspan=2, pady=3, sticky="we")

        draw_grid(self.canvas)

    def clear_canvas(self):
        draw_grid(self.canvas)
        self.info_label.config(text="Время: -")

    def get_int(self, entry, name):
        try:
            return int(entry.get())
        except ValueError:
            raise ValueError(f"Некорректное целое значение в поле {name}")

    def draw_line(self):
        try:
            x1 = self.get_int(self.x1_entry, "x1")
            y1 = self.get_int(self.y1_entry, "y1")
            x2 = self.get_int(self.x2_entry, "x2")
            y2 = self.get_int(self.y2_entry, "y2")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        alg = self.alg_var.get()

        if alg == "smooth":
            t0 = time.perf_counter()
            count = wu_line(self.canvas, x1, y1, x2, y2, base_color="#ff0000")
            dt = time.perf_counter() - t0
            self.info_label.config(
                text=f"Время (smooth/Wu): {dt * 1000:.4f} мс, закрашенных клеток: {count}"
            )
            return

        if alg == "step":
            func = step_by_step_line
            color = "red"
        elif alg == "dda":
            func = dda_line
            color = "blue"
        elif alg == "bresenham":
            func = bresenham_line
            color = "green"
        elif alg == "castle":
            func = castle_pitway_line
            color = "orange"
        else:
            messagebox.showerror("Ошибка", "Неизвестный алгоритм")
            return

        points, dt = timed(func, x1, y1, x2, y2)

        for (x, y) in points:
            draw_pixel(self.canvas, x, y, color=color)

        self.info_label.config(
            text=f"Время ({alg}): {dt * 1000:.4f} мс, пикселей: {len(points)}"
        )

    def draw_circle(self):
        try:
            xc = self.get_int(self.xc_entry, "xc")
            yc = self.get_int(self.yc_entry, "yc")
            r = self.get_int(self.r_entry, "R")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        if r <= 0:
            messagebox.showerror("Ошибка", "Радиус должен быть > 0")
            return

        points, dt = timed(bresenham_circle, xc, yc, r)

        for (x, y) in points:
            draw_pixel(self.canvas, x, y, color="purple")

        self.info_label.config(
            text=f"Время (окружн. Брезенхем): {dt * 1000:.4f} мс, пикселей: {len(points)}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = RasterApp(root)
    root.mainloop()
