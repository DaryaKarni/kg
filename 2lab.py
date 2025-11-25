import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os
import sys

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 2, вариант 8")
        self.root.geometry("1200x800")
        
        self.original_img = None
        self.processed_img = None
        self.test_images_dir = "test_images"
     
        if sys.platform.startswith('win'):
            self.test_images_dir = "test_images_lab_2"
        
        self.setup_ui()
        self.create_test_images()
    
    def setup_ui(self):
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(left_frame, text="Исходное").pack()
        self.original_label = ttk.Label(left_frame)
        self.original_label.pack()
        
        ttk.Button(left_frame, text="Загрузить своё", 
                  command=self.load_image).pack(pady=5)
        ttk.Button(left_frame, text="Тест 1 (размытое)", 
                  command=lambda: self.load_test(0)).pack(pady=2)
        ttk.Button(left_frame, text="Тест 2 (контраст)", 
                  command=lambda: self.load_test(1)).pack(pady=2)
        ttk.Button(left_frame, text="Тест 3 (шум)", 
                  command=lambda: self.load_test(2)).pack(pady=2)
        
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(right_frame, text="Результат").pack()
        self.processed_label = ttk.Label(right_frame)
        self.processed_label.pack()
        
        control = ttk.LabelFrame(self.root, text="Методы обработки")
        control.pack(fill=tk.X, padx=10, pady=5)
        
        self.method_var = tk.StringVar(value="sharpen")
        methods = [("Высокочастотный фильтр", "sharpen"),
                   ("Порог ручной", "threshold_manual"),
                   ("Порог Otsu", "threshold_otsu")]
        for i, (text, value) in enumerate(methods):
            ttk.Radiobutton(control, text=text, variable=self.method_var,
                           value=value, command=self.process_image).pack(anchor=tk.W, padx=10)
        
        ttk.Label(control, text="Порог:").pack(anchor=tk.W)
        self.threshold_var = tk.DoubleVar(value=127)
        scale = ttk.Scale(control, from_=0, to=255, variable=self.threshold_var, 
                         orient=tk.HORIZONTAL, command=self.on_param_change)
        scale.pack(fill=tk.X, padx=10, pady=5)
        self.threshold_label = ttk.Label(control, text="127")
        self.threshold_label.pack()
        
        ttk.Button(control, text="Обработать", command=self.process_image).pack(pady=10)
    
    def create_test_images(self):
        """Создаёт тестовые изображения с АНГЛИЙСКИМИ именами"""
        if not os.path.exists(self.test_images_dir):
            os.makedirs(self.test_images_dir)
            
        # Тест 1: размытое
        blurry = self.create_blurry()
        blurry.save(os.path.join(self.test_images_dir, "blurry_test.jpg"), quality=95)
        
        #Тест 2: низкий контраст
        low_contrast = self.create_low_contrast()
        low_contrast.save(os.path.join(self.test_images_dir, "low_contrast_test.jpg"), quality=95)
        
        # Тест 3:с шумом
        noisy = self.create_noisy()
        noisy.save(os.path.join(self.test_images_dir, "noisy_test.jpg"), quality=95)
    
    def create_blurry(self):
        img = np.zeros((300, 400), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (350, 250), 200, -1)
        cv2.circle(img, (200, 150), 80, 100, -1)
        return Image.fromarray(cv2.GaussianBlur(img, (15, 15), 0))
    
    def create_low_contrast(self):
        img = np.zeros((300, 400), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (350, 250), 120, -1)
        cv2.circle(img, (200, 150), 80, 60, -1)
        return Image.fromarray(img)
    
    def create_noisy(self):
        img = np.zeros((300, 400), dtype=np.uint8)
        cv2.rectangle(img, (80, 80), (320, 220), 255, -1)
        cv2.circle(img, (200, 150), 60, 0, -1)
        noise = np.random.normal(0, 25, img.shape)
        noisy = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if file_path:
            self.original_img = cv2.imread(file_path)
            if self.original_img is not None:
                self.display_original()
                self.process_image()
    
    def load_test(self, index):
        test_files = ["blurry_test.jpg", "low_contrast_test.jpg", "noisy_test.jpg"]
        test_path = os.path.join(self.test_images_dir, test_files[index])
        
        if os.path.exists(test_path):
            self.original_img = cv2.imread(test_path)
            self.display_original()
            self.process_image()
        else:
            print(f"Файл {test_path} не найден. Создаю тестовые...")
            self.create_test_images()
            self.original_img = cv2.imread(test_path)
            self.display_original()
    
    def display_original(self):
        if self.original_img is not None:
            display_img = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB)
            display_img = cv2.resize(display_img, (400, 400))
            img_pil = Image.fromarray(display_img)
            photo = ImageTk.PhotoImage(img_pil)
            self.original_label.configure(image=photo)
            self.original_label.image = photo
    
    def process_image(self):
        if self.original_img is None:
            return
        
        method = self.method_var.get()
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        
        if method == "sharpen":
            self.processed_img = self.apply_sharpen(gray)
        elif method == "threshold_manual":
            thresh = int(self.threshold_var.get())
            _, self.processed_img = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
        elif method == "threshold_otsu":
            _, self.processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        self.display_processed()
    
    def apply_sharpen(self, img):
        kernel = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ], dtype=np.float32)

        sharpened = cv2.filter2D(img, -1, kernel)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    
    def display_processed(self):
        if self.processed_img is not None:
            display_img = cv2.resize(self.processed_img, (400, 400))
            img_pil = Image.fromarray(display_img)
            photo = ImageTk.PhotoImage(img_pil)
            self.processed_label.configure(image=photo)
            self.processed_label.image = photo
    
    def on_param_change(self, value):
        self.threshold_label.config(text=f"{int(float(value))}")
        if self.method_var.get() == "threshold_manual":
            self.process_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
