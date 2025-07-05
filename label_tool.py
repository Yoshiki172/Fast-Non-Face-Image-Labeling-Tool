import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class ImageLabelingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Tool")
        self.style = ttk.Style("cyborg")

        self.image_paths = []
        self.current_index = 0
        self.all_rectangles = {}
        self.rect_ids = []
        self.grid_lines = []
        self.start_x = self.start_y = self.end_x = self.end_y = None
        self.rect_color = "red"
        self.square_mode = False
        self.output_txt_path = "annotations.txt"
        self.scale_factor = 1.0
        self.snap_to_grid = True

        self.grid_div_x = 64
        self.grid_div_y = 32

        self.control_frame = ttk.Frame(root, padding=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        self.load_button = ttk.Button(self.control_frame, text="Load Folder", command=self.load_folder, bootstyle=PRIMARY)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.square_button = ttk.Button(self.control_frame, text="Rect Mode", command=self.toggle_square_mode, bootstyle=INFO)
        self.square_button.pack(side=tk.LEFT, padx=5)

        self.grid_toggle_button = ttk.Button(self.control_frame, text="Disable Grid", command=self.toggle_grid_snap, bootstyle=INFO)
        self.grid_toggle_button.pack(side=tk.LEFT, padx=5)

        self.grid_label = ttk.Label(self.control_frame, text=f"Grid: {self.grid_div_x} x {self.grid_div_y}")
        self.grid_label.pack(side=tk.LEFT, padx=5)

        self.grid_x_entry = ttk.Entry(self.control_frame, width=4)
        self.grid_x_entry.insert(0, str(self.grid_div_x))
        self.grid_x_entry.pack(side=tk.LEFT, padx=(0,5))
        self.grid_x_entry.bind("<Return>", self.update_grid_divisions)

        self.grid_y_entry = ttk.Entry(self.control_frame, width=4)
        self.grid_y_entry.insert(0, str(self.grid_div_y))
        self.grid_y_entry.pack(side=tk.LEFT, padx=(0,10))
        self.grid_y_entry.bind("<Return>", self.update_grid_divisions)

        self.prev_button = ttk.Button(self.control_frame, text="Prev", command=self.prev_image, bootstyle=SECONDARY)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(self.control_frame, text="Next", command=self.save_and_next_image, bootstyle=WARNING)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.next_no_save_button = ttk.Button(self.control_frame, text="Next (No Save)", command=self.next_without_save, bootstyle=SECONDARY)
        self.next_no_save_button.pack(side=tk.LEFT, padx=5)

        self.color_button = ttk.Button(self.control_frame, text="Color", command=self.choose_color, bootstyle=INFO)
        self.color_button.pack(side=tk.LEFT, padx=5)

        self.label_entry = ttk.Entry(self.control_frame)
        self.label_entry.insert(0, "0")
        self.label_entry.pack(side=tk.LEFT, padx=5)

        self.reset_zoom_button = ttk.Button(self.control_frame, text="Reset Zoom", command=self.reset_zoom, bootstyle=INFO)
        self.reset_zoom_button.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(root, cursor="cross", bg="gray")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.slider = ttk.Scale(root, from_=0.1, to=5.0, orient=tk.HORIZONTAL, command=self.on_scale, length=300)
        self.slider.set(1.0)
        self.slider.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click)

    def reset_zoom(self):
        self.slider.set(1.0)

    def update_grid_divisions(self, event=None):
        try:
            x_val = int(self.grid_x_entry.get())
            y_val = int(self.grid_y_entry.get())
            if x_val <= 0 or y_val <= 0:
                raise ValueError()
            self.grid_div_x = x_val
            self.grid_div_y = y_val
            self.grid_label.config(text=f"Grid: {self.grid_div_x} x {self.grid_div_y}")
            if self.snap_to_grid:
                self.draw_grid()
        except ValueError:
            messagebox.showerror("Invalid input", "Grid divisions must be positive integers.")

    def draw_grid(self):
        for line in self.grid_lines:
            self.canvas.delete(line)
        self.grid_lines.clear()
        if not hasattr(self, 'resized_image'):
            return
        width, height = self.resized_image.size
        step_x = width / self.grid_div_x
        step_y = height / self.grid_div_y
        for i in range(1, self.grid_div_x):
            x = int(i * step_x)
            self.grid_lines.append(self.canvas.create_line(x, 0, x, height, fill='white', dash=(2, 2)))
        for j in range(1, self.grid_div_y):
            y = int(j * step_y)
            self.grid_lines.append(self.canvas.create_line(0, y, width, y, fill='white', dash=(2, 2)))

    def snap_to_grid_coord(self, x, y):
        if not hasattr(self, 'resized_image'):
            return x, y
        width, height = self.resized_image.size
        step_x = width / self.grid_div_x
        step_y = height / self.grid_div_y
        snapped_x = round(x / step_x) * step_x
        snapped_y = round(y / step_y) * step_y
        snapped_x = min(int(snapped_x), width - 1)
        snapped_y = min(int(snapped_y), height - 1)
        return snapped_x, snapped_y


    def toggle_grid_snap(self):
        self.snap_to_grid = not self.snap_to_grid
        self.grid_toggle_button.config(text="Disable Grid" if self.snap_to_grid else "Enable Grid")
        if self.snap_to_grid:
            self.draw_grid()
        else:
            self.clear_grid()

    def clear_grid(self):
        for line in self.grid_lines:
            self.canvas.delete(line)
        self.grid_lines.clear()

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]
            self.image_paths.sort()
            self.current_index = 0
            self.all_rectangles.clear()
            self.load_current_image()

    def load_current_image(self):
        if not self.image_paths:
            return
        image_path = self.image_paths[self.current_index]
        self.image = Image.open(image_path)
        self.update_resized_image()
        self.show_existing_rectangles()

    def update_resized_image(self):
        img_w, img_h = self.image.size
        scale = self.scale_factor
        new_size = (int(img_w * scale), int(img_h * scale))
        self.resized_image = self.image.resize(new_size, Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.resized_image)
        self.canvas.config(width=new_size[0], height=new_size[1])
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        if self.snap_to_grid:
            self.draw_grid()

    def show_existing_rectangles(self):
        self.clear_rectangles_on_canvas()
        rects = self.all_rectangles.get(self.current_index, [])
        scale = self.scale_factor
        for (x1, y1, x2, y2, label) in rects:
            sx1, sy1, sx2, sy2 = int(x1 * scale), int(y1 * scale), int(x2 * scale), int(y2 * scale)
            rect_id = self.canvas.create_rectangle(sx1, sy1, sx2, sy2, outline=self.rect_color, width=2)
            self.rect_ids.append(rect_id)

    def clear_rectangles_on_canvas(self):
        for rid in self.rect_ids:
            self.canvas.delete(rid)
        self.rect_ids.clear()

    def on_scale(self, val):
        self.scale_factor = float(val)
        if hasattr(self, 'image'):
            self.update_resized_image()
            self.show_existing_rectangles()
        

    def toggle_square_mode(self):
        self.square_mode = not self.square_mode
        mode = "Square" if self.square_mode else "Rect"
        self.square_button.config(text=f"{mode} Mode")

    def on_mouse_down(self, event):
        self.start_x, self.start_y = self.snap_to_grid_coord(event.x, event.y) if self.snap_to_grid else (event.x, event.y)

    def on_mouse_drag(self, event):
        self.canvas.delete("preview")
        end_x, end_y = self.snap_to_grid_coord(event.x, event.y) if self.snap_to_grid else (event.x, event.y)
        if self.square_mode:
            side = min(abs(end_x - self.start_x), abs(end_y - self.start_y))
            end_x = self.start_x + side if end_x >= self.start_x else self.start_x - side
            end_y = self.start_y + side if end_y >= self.start_y else self.start_y - side
        self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y,
                                     outline=self.rect_color, width=2, tags="preview")

    def on_mouse_up(self, event):
        self.end_x, self.end_y = self.snap_to_grid_coord(event.x, event.y) if self.snap_to_grid else (event.x, event.y)

        if self.square_mode:
            side = min(abs(self.end_x - self.start_x), abs(self.end_y - self.start_y))
            self.end_x = self.start_x + side if self.end_x >= self.start_x else self.start_x - side
            self.end_y = self.start_y + side if self.end_y >= self.start_y else self.start_y - side

        # === 追加: 矩形サイズが0のものは無視 ===
        if self.start_x == self.end_x or self.start_y == self.end_y:
            self.canvas.delete("preview")
            return

        label = self.label_entry.get()
        box = (min(self.start_x, self.end_x), min(self.start_y, self.end_y),
               max(self.start_x, self.end_x), max(self.start_y, self.end_y), label)
        rect_id = self.canvas.create_rectangle(*box[:4], outline=self.rect_color, width=2)
        self.rect_ids.append(rect_id)

        scale_inv = 1 / self.scale_factor
        x1, y1, x2, y2 = [int(coord * scale_inv) for coord in box[:4]]

        # 元画像のサイズを取得
        img_w, img_h = self.image.size

        # 最大値に制限（端がちょうど入るように）
        x1 = max(0, min(x1, img_w))
        x2 = max(0, min(x2, img_w))
        y1 = max(0, min(y1, img_h))
        y2 = max(0, min(y2, img_h))
        x1, y1, x2, y2 = [int(coord * scale_inv) for coord in box[:4]]
        self.all_rectangles.setdefault(self.current_index, []).append((x1, y1, x2, y2, label))
        self.canvas.delete("preview")

    def on_right_click(self, event):
        for i in reversed(range(len(self.rect_ids))):
            coords = self.canvas.coords(self.rect_ids[i])
            x1, y1, x2, y2 = coords
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.canvas.delete(self.rect_ids[i])
                del self.rect_ids[i]
                rect_list = self.all_rectangles.get(self.current_index, [])
                if rect_list:
                    scale = self.scale_factor
                    for j, (rx1, ry1, rx2, ry2, label) in enumerate(rect_list):
                        sx1, sy1, sx2, sy2 = rx1 * scale, ry1 * scale, rx2 * scale, ry2 * scale
                        if sx1 <= event.x <= sx2 and sy1 <= event.y <= sy2:
                            del rect_list[j]
                            break
                self.update_annotation_file()
                break

    def update_annotation_file(self):
        if not self.image_paths or not (0 <= self.current_index < len(self.image_paths)):
            return  # ← ここで不正な状態なら抜ける
        if not os.path.exists(self.output_txt_path):
            # ファイルがなければ空ファイルを作成
            with open(self.output_txt_path, "w") as f:
                pass

        with open(self.output_txt_path, "r") as f:
            lines = f.readlines()

        image_path = os.path.relpath(self.image_paths[self.current_index])
        rect_list = self.all_rectangles.get(self.current_index, [])
        boxes_str = ' '.join([f"{x1},{y1},{x2},{y2},{label}" for x1, y1, x2, y2, label in rect_list])
        new_line = f"{image_path} {boxes_str}\n" if boxes_str else ""

        found = False
        new_lines = []
        for line in lines:
            if line.startswith(image_path):
                if new_line:
                    new_lines.append(new_line)
                found = True
            else:
                new_lines.append(line)
        if not found and new_line:
            new_lines.append(new_line)

        with open(self.output_txt_path, "w") as f:
            f.writelines(new_lines)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.rect_color = color

    def next_without_save(self):
        if self.current_index + 1 < len(self.image_paths):
            self.current_index += 1
            self.load_current_image()
        else:
            messagebox.showinfo("Done", "All images processed.")

    def save_and_next_image(self):
        if self.current_index >= len(self.image_paths):
            return
        image_path = self.image_paths[self.current_index]
        relative_path = os.path.relpath(image_path)
        with open(self.output_txt_path, "a") as f:
            rect_list = self.all_rectangles.get(self.current_index, [])
            boxes_str = ' '.join([f"{x1},{y1},{x2},{y2},{label}" for x1, y1, x2, y2, label in rect_list])
            f.write(f"{relative_path} {boxes_str}\n")
        self.current_index += 1
        if self.current_index < len(self.image_paths):
            self.load_current_image()
        else:
            messagebox.showinfo("Done", "All images annotated.")

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
        else:
            messagebox.showinfo("Info", "This is the first image.")
    
if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = ImageLabelingTool(root)
    root.geometry("1200x600")
    root.mainloop()
