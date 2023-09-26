# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 15:36:26 2023

@author: rudanxiao
"""


import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import numpy as np
import pydicom
from pydicom import dcmread
import pylibjpeg
import openjpeg

class ImageLabelerApp:
    def __init__(self, root,history_file):
        self.root = root
        self.history_file=history_file
        self.root.title("Image Labeler")
        self.image_paths = []
        self.current_index = 0
        self.labels = {}

#        self.history_file = "history_label.txt"
        self.load_history()

        self.label_var = tk.StringVar()
        self.label_var.set("Label: ")

        self.load_button = ttk.Button(self.root, text="Load Images", command=self.load_images)
        self.y_button = ttk.Button(self.root, text="Y", command=lambda: self.label_image("Y"))
        self.n_button = ttk.Button(self.root, text="N", command=lambda: self.label_image("N"))

        self.image_label = ttk.Label(self.root)

        self.load_button.pack(pady=10)
        self.y_button.pack(side=tk.LEFT, padx=10)
        self.n_button.pack(side=tk.RIGHT, padx=10)
        self.image_label.pack(padx=10, pady=10)
        self.finish_button = ttk.Button(self.root, text="Finish Labeling", command=self.finish_labeling)
        self.finish_button.pack(pady=10)

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    image_path, label = line.strip().split(": ")
                    self.labels[image_path] = label

    def save_history(self):
        with open(self.history_file, "w") as f:
            for image_path, label in self.labels.items():
                f.write(f"{image_path}: {label}\n")

    def load_images(self):
        folder = filedialog.askdirectory(title="Select Image Folder")
        if folder:
            self.image_paths = [path for path in self.get_image_paths(folder) if path not in self.labels]
            self.current_index = 0
            self.show_image()

    def get_image_paths(self, folder):
        image_paths = []
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.dcm')):
                    image_paths.append(os.path.join(root, file))
        return image_paths

    def show_image(self):
        if self.current_index < len(self.image_paths):
            image_path = self.image_paths[self.current_index]
            if image_path in self.labels:
                label = self.labels[image_path]
            else:
                label = "Unlabeled"

            if image_path.lower().endswith('.dcm'):
                dicom_data = dcmread(image_path)
                # dicom_data.PhotometricInterpretation = 'YBR_FULL'
                pixel_data = dicom_data.pixel_array
                im = np.max(pixel_data) - pixel_data
                image_array = (
                    255
                    * (im.astype(np.float32) - im.min().astype(np.float32))
                    / im.ptp().astype(np.float32)
                ).astype(np.uint8)
                image = Image.fromarray(image_array)
            else:
                image = Image.open(image_path)

            image.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(image=image)

            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.label_var.set(f"Label: {label}")


    def finish_labeling(self):
        self.save_history()
        self.root.quit()

    def label_image(self, label):
        if self.current_index < len(self.image_paths):
            image_path = self.image_paths[self.current_index]
            self.labels[image_path] = label
            self.save_history()
            self.show_image()
            self.current_index += 1
            

if __name__ == "__main__":
    root = tk.Tk()
    history_file='C:\postdoc\data\survival_data\history_label.txt'
    app = ImageLabelerApp(root,history_file)
    root.mainloop()
