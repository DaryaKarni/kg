import tkinter as tk
from tkinter import ttk, colorchooser

# Конвертации RGB <-> HSV
def rgb_to_hsv(r, g, b):
    r_p, g_p, b_p = r / 255.0, g / 255.0, b / 255.0
    c_max, c_min = max(r_p, g_p, b_p), min(r_p, g_p, b_p)
    delta = c_max - c_min
    h = 0
    s = 0
    v = c_max
    if delta != 0:
        s = delta / c_max
        if c_max == r_p:
            h = 60 * (((g_p - b_p) / delta) % 6)
        elif c_max == g_p:
            h = 60 * ((b_p - r_p) / delta + 2)
        else:
            h = 60 * ((r_p - g_p) / delta + 4)
    return int(round(h)), int(round(s * 100)), int(round(v * 100))

def hsv_to_rgb(h, s, v):
    s /= 100.0
    v /= 100.0
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    r_p = g_p = b_p = 0
    if 0 <= h < 60: r_p, g_p, b_p = c, x, 0
    elif 60 <= h < 120: r_p, g_p, b_p = x, c, 0
    elif 120 <= h < 180: r_p, g_p, b_p = 0, c, x
    elif 180 <= h < 240: r_p, g_p, b_p = 0, x, c
    elif 240 <= h < 300: r_p, g_p, b_p = x, 0, c
    elif 300 <= h < 360: r_p, g_p, b_p = c, 0, x
    r = int(round((r_p + m) * 255))
    g = int(round((g_p + m) * 255))
    b = int(round((b_p + m) * 255))
    return r, g, b

# Конвертации RGB <-> CMYK
def rgb_to_cmyk(r, g, b):
    if r == g == b == 0:
        return 0, 0, 0, 100
    r_p, g_p, b_p = r / 255.0, g / 255.0, b / 255.0
    k = 1 - max(r_p, g_p, b_p)
    c = (1 - r_p - k) / (1 - k)
    m = (1 - g_p - k) / (1 - k)
    y = (1 - b_p - k) / (1 - k)
    return int(round(c * 100)), int(round(m * 100)), int(round(y * 100)), int(round(k * 100))

def cmyk_to_rgb(c, m, y, k):
    r = 255 * (1 - c / 100) * (1 - k / 100)
    g = 255 * (1 - m / 100) * (1 - k / 100)
    b = 255 * (1 - y / 100) * (1 - k / 100)
    return int(round(r)), int(round(g)), int(round(b))

class ColorConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("Конвертер Цвета (RGB/CMYK/HSV)")
        master.configure(bg="#E0E0E0")

        # Начальные значения
        self.r_val = tk.IntVar(value=255)
        self.g_val = tk.IntVar(value=255)
        self.b_val = tk.IntVar(value=255)
        self.c_val = tk.IntVar(value=0)
        self.m_val = tk.IntVar(value=0)
        self.y_val = tk.IntVar(value=0)
        self.k_val = tk.IntVar(value=0)
        self.h_val = tk.IntVar(value=0)
        self.s_val = tk.IntVar(value=0)
        self.v_val = tk.IntVar(value=100)
        self.hex_code = tk.StringVar(value="#FFFFFF")

        # Верхняя панель с HEX и цветом
        top_frame = tk.Frame(master, bg="white", relief="solid", bd=1)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.color_preview = tk.Label(top_frame, text="Образец Цвета", bg="#FFFFFF", fg="#000000",
                                      font=("Arial", 16, "bold"), width=30, height=3)
        self.color_preview.pack(pady=(10, 5))

        self.hex_label = tk.Label(top_frame, textvariable=self.hex_code, font=("Arial", 12), bg="white")
        self.hex_label.pack(pady=(0, 10))

        btn_color = tk.Button(top_frame, text="Выбрать цвет из палитры", command=self.open_color_picker)
        btn_color.pack(pady=(0, 10))

        # Контрольная панель (RGB, CMYK, HSV) — в одну строку
        controls_frame = tk.Frame(master, bg="#E0E0E0")
        controls_frame.pack(fill="x", padx=10, pady=0)

        self.create_rgb_section(controls_frame).pack(side="left", fill="x", expand=True, padx=5)
        self.create_cmyk_section(controls_frame).pack(side="left", fill="x", expand=True, padx=5)
        self.create_hsv_section(controls_frame).pack(side="left", fill="x", expand=True, padx=5)

        self.update_color(source='rgb')

    def open_color_picker(self):
        color_code = colorchooser.askcolor(title="Выберите цвет")
        if color_code and color_code[0]:
            r, g, b = map(int, color_code[0])
            self.r_val.set(r)
            self.g_val.set(g)
            self.b_val.set(b)
            self.update_color(source='rgb')

    def create_scale_and_entry(self, parent, text, var, from_, to, color, command):
        frame = tk.Frame(parent, bg="#F8F8F8", pady=2)
        lbl = tk.Label(frame, text=text, fg=color, bg="#F8F8F8", width=2, anchor="w")
        lbl.pack(side="left", padx=(5, 2))

        scale = tk.Scale(frame, from_=from_, to=to, orient="horizontal", variable=var,
                         showvalue=0, length=120, bg="#F8F8F8", troughcolor="#CCC",
                         command=lambda e=None: command())
        scale.pack(side="left", padx=2)

        entry = tk.Entry(frame, textvariable=var, width=4, justify="center")
        entry.pack(side="left", padx=(2, 5))

        # Обновление по вводу
        entry.bind("<Return>", lambda e: command())
        entry.bind("<FocusOut>", lambda e: command())

        return frame

    def create_rgb_section(self, parent):
        frame = tk.Frame(parent, bg="#F8F8F8", bd=1, relief="solid", padx=5, pady=5)
        title = tk.Label(frame, text="Модель RGB", bg="#F8F8F8", font=("Arial", 10, "bold"))
        title.pack(anchor="w", pady=(0, 5))

        self.r_scale = self.create_scale_and_entry(frame, "R", self.r_val, 0, 255, "red", lambda: self.update_color('rgb'))
        self.r_scale.pack(anchor="w")
        self.g_scale = self.create_scale_and_entry(frame, "G", self.g_val, 0, 255, "green", lambda: self.update_color('rgb'))
        self.g_scale.pack(anchor="w")
        self.b_scale = self.create_scale_and_entry(frame, "B", self.b_val, 0, 255, "blue", lambda: self.update_color('rgb'))
        self.b_scale.pack(anchor="w")
        return frame

    def create_cmyk_section(self, parent):
        frame = tk.Frame(parent, bg="#F8F8F8", bd=1, relief="solid", padx=5, pady=5)
        title = tk.Label(frame, text="Модель CMYK", bg="#F8F8F8", font=("Arial", 10, "bold"))
        title.pack(anchor="w", pady=(0, 5))

        self.c_scale = self.create_scale_and_entry(frame, "C", self.c_val, 0, 100, "cyan", lambda: self.update_color('cmyk'))
        self.c_scale.pack(anchor="w")
        self.m_scale = self.create_scale_and_entry(frame, "M", self.m_val, 0, 100, "magenta", lambda: self.update_color('cmyk'))
        self.m_scale.pack(anchor="w")
        self.y_scale = self.create_scale_and_entry(frame, "Y", self.y_val, 0, 100, "yellow", lambda: self.update_color('cmyk'))
        self.y_scale.pack(anchor="w")
        self.k_scale = self.create_scale_and_entry(frame, "K", self.k_val, 0, 100, "black", lambda: self.update_color('cmyk'))
        self.k_scale.pack(anchor="w")
        return frame

    def create_hsv_section(self, parent):
        frame = tk.Frame(parent, bg="#F8F8F8", bd=1, relief="solid", padx=5, pady=5)
        title = tk.Label(frame, text="Модель HSV", bg="#F8F8F8", font=("Arial", 10, "bold"))
        title.pack(anchor="w", pady=(0, 5))

        self.h_scale = self.create_scale_and_entry(frame, "H", self.h_val, 0, 360, "purple", lambda: self.update_color('hsv'))
        self.h_scale.pack(anchor="w")
        self.s_scale = self.create_scale_and_entry(frame, "S", self.s_val, 0, 100, "purple", lambda: self.update_color('hsv'))
        self.s_scale.pack(anchor="w")
        self.v_scale = self.create_scale_and_entry(frame, "V", self.v_val, 0, 100, "purple", lambda: self.update_color('hsv'))
        self.v_scale.pack(anchor="w")
        return frame

    def update_color(self, source=None):
        try:
            if source == 'rgb':
                r, g, b = self.r_val.get(), self.g_val.get(), self.b_val.get()
            elif source == 'cmyk':
                r, g, b = cmyk_to_rgb(self.c_val.get(), self.m_val.get(), self.y_val.get(), self.k_val.get())
            elif source == 'hsv':
                r, g, b = hsv_to_rgb(self.h_val.get(), self.s_val.get(), self.v_val.get())
            else:
                r, g, b = self.r_val.get(), self.g_val.get(), self.b_val.get()
        except Exception as e:
            print(f"Ошибка конвертации: {e}")
            return

        self.r_val.set(r)
        self.g_val.set(g)
        self.b_val.set(b)

        c, m, y, k = rgb_to_cmyk(r, g, b)
        if source != 'cmyk':
            self.c_val.set(c)
            self.m_val.set(m)
            self.y_val.set(y)
            self.k_val.set(k)

        h, s, v = rgb_to_hsv(r, g, b)
        if source != 'hsv':
            self.h_val.set(h)
            self.s_val.set(s)
            self.v_val.set(v)

        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        self.hex_code.set(hex_color)
        self.color_preview.config(bg=hex_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorConverterApp(root)
    root.mainloop()
