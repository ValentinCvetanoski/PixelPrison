import cv2
import hashlib
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Image Message Hider")
        self.root.geometry("850x650")

        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 10))
        self.style.configure("Warning.TLabel", foreground="orange")

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.image_preview = ttk.Label(self.main_frame)
        self.image_preview.pack(pady=10)

        self.warning_label = ttk.Label(self.main_frame, text="", style="Warning.TLabel")
        self.warning_label.pack(pady=5)

        self.image_path = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.image_path, width=60).pack(pady=5)
        ttk.Button(self.main_frame, text="Browse Image", command=self.browse_image).pack(pady=5)

        ttk.Label(self.main_frame, text="Secret Message:").pack(pady=5)
        self.secret_message = tk.Text(self.main_frame, height=4, width=60)
        self.secret_message.pack(pady=5)

        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.pack(pady=10)
        ttk.Button(self.btn_frame, text="Embed Message", command=self.embed_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Extract Message", command=self.extract_message).pack(side=tk.LEFT, padx=5)

        self.status = ttk.Label(self.main_frame, text="Ready", foreground="gray")
        self.status.pack(pady=10)

    def browse_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")])
        if path:
            self.warning_label.config(text="")
            self.image_path.set(path)

            if path.lower().endswith(('.jpg', '.jpeg')):
                self.convert_jpg_to_png(path)

            self.show_image_preview(self.image_path.get())

    def convert_jpg_to_png(self, jpg_path):
        try:
            img = cv2.imread(jpg_path)
            if img is None:
                raise ValueError("Failed to read JPG image")
            png_path = os.path.splitext(jpg_path)[0] + "_converted.png"
            cv2.imwrite(png_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            self.image_path.set(png_path)
            self.warning_label.config(
                text="Warning: JPG converted to PNG. Hidden data may be unreliable due to prior JPG compression."
            )
            return png_path
        except Exception as e:
            self.show_error(f"JPG conversion failed: {str(e)}")
            return jpg_path

    def show_image_preview(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((350, 350))
            photo = ImageTk.PhotoImage(img)
            self.image_preview.config(image=photo)
            self.image_preview.image = photo
        except Exception as e:
            self.show_error(f"Preview error: {str(e)}")

    def embed_message(self):
        path = self.image_path.get()
        message = self.secret_message.get("1.0", tk.END).strip()

        if not path or not message:
            self.show_error("Please select an image and enter a message!")
            return

        try:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Invalid image file")

            protected_msg = f"{message}|{hashlib.md5(message.encode()).hexdigest()}"
            max_chars = ((img.shape[0] * img.shape[1] * 3) // 8) - 70
            if len(protected_msg) > max_chars:
                raise ValueError(f"Message too long! Max {max_chars} characters")

            b, g, r = cv2.split(img)
            merged = np.concatenate((b.flatten(), g.flatten(), r.flatten()))

            encoded_merged = self.encode_lsb(merged, protected_msg)

            total_pixels = img.shape[0] * img.shape[1]
            b = encoded_merged[:total_pixels].reshape(img.shape[0], img.shape[1])
            g = encoded_merged[total_pixels:total_pixels*2].reshape(img.shape[0], img.shape[1])
            r = encoded_merged[total_pixels*2:].reshape(img.shape[0], img.shape[1])

            encoded_img = cv2.merge((b, g, r))

            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Files", "*.png")]
            )
            if save_path:
                cv2.imwrite(save_path, encoded_img)
                self.show_success(f"Message embedded in:\n{save_path}")

        except Exception as e:
            self.show_error(str(e))

    def extract_message(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.bmp;*.tiff")])
        if not path:
            return

        try:
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Invalid image file")

            b, g, r = cv2.split(img)
            merged = np.concatenate((b.flatten(), g.flatten(), r.flatten()))

            extracted = self.decode_lsb(merged)

            if "|" not in extracted:
                raise ValueError("No valid message found (possibly corrupted by JPG compression)")

            msg, checksum = extracted.rsplit("|", 1)
            if hashlib.md5(msg.encode()).hexdigest() != checksum:
                raise ValueError("Message corrupted! This image was likely saved as JPG previously.")

            self.secret_message.delete("1.0", tk.END)
            self.secret_message.insert("1.0", msg)
            self.show_success("Message extracted and verified!")

        except Exception as e:
            self.show_error(f"{str(e)}\n\nPossible causes:\n- Image was previously JPG compressed\n- Image was edited after encoding")

    def encode_lsb(self, image, data):
        binary_data = ''.join(format(ord(c), '08b') for c in data)
        data_len = len(binary_data)
        header = format(data_len, '032b')  # 32 bits to store message length
        binary_data = header + binary_data

        if len(binary_data) > len(image):
            raise ValueError("Image too small to hold the data")

        for i in range(len(binary_data)):
            image[i] = (image[i] & ~1) | int(binary_data[i])

        return image

    def decode_lsb(self, image):
        flat_img = image.flatten()
        header_bits = ''.join(str(pixel & 1) for pixel in flat_img[:32])
        data_len = int(header_bits, 2)

        binary_data = ''.join(str(pixel & 1) for pixel in flat_img[32:32+data_len])

        chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
        return ''.join(chr(int(byte, 2)) for byte in chars)


    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status.config(text=f"Error: {message}", foreground="red")

    def show_success(self, message):
        messagebox.showinfo("Success", message)
        self.status.config(text=message, foreground="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
