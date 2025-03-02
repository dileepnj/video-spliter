#!/usr/bin/env python

import os
import subprocess
import json
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

# Core splitting functions (original එකෙන් ගත්තා)
def split_by_seconds(filename, split_length, output_dir=None, vcodec="copy", acodec="copy", extra=""):
    video_length = get_video_length(filename)
    if split_length <= 0:
        raise ValueError("Split length can't be 0")
    split_count = int(video_length / float(split_length)) + 1
    if split_count == 1:
        raise ValueError("Video is shorter than split length")

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filebase = ".".join(filename.split(".")[:-1])
    fileext = filename.split(".")[-1]

    for n in range(0, split_count):
        split_start = split_length * n
        output_path = os.path.join(output_dir, f"{filebase}-{n+1}-of-{split_count}.{fileext}") if output_dir else f"{filebase}-{n+1}-of-{split_count}.{fileext}"
        split_cmd = ["ffmpeg", "-i", filename, "-ss", str(split_start), "-t", str(split_length), "-vcodec", vcodec, "-acodec", acodec, "-y", output_path] + extra.split()
        subprocess.check_output(split_cmd)

def split_by_manifest(filename, manifest, output_dir=None, vcodec="copy", acodec="copy", extra=""):
    if not os.path.exists(manifest):
        raise FileNotFoundError("Manifest file not found")

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(manifest) as manifest_file:
        manifest_type = manifest.split(".")[-1]
        if manifest_type == "json":
            config = json.load(manifest_file)
        elif manifest_type == "csv":
            config = csv.DictReader(manifest_file)
        else:
            raise ValueError("Manifest must be JSON or CSV")

        fileext = filename.split(".")[-1]
        for video_config in config:
            split_start = video_config["start_time"]
            split_length = video_config.get("end_time", None) or video_config["length"]
            filebase = video_config["rename_to"]
            if fileext not in filebase:
                filebase += "." + fileext
            output_path = os.path.join(output_dir, filebase) if output_dir else filebase
            split_cmd = ["ffmpeg", "-i", filename, "-ss", str(split_start), "-t", str(split_length), "-vcodec", vcodec, "-acodec", acodec, "-y", output_path] + extra.split()
            subprocess.check_output(split_cmd)

def get_video_length(filename):
    output = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename]).strip()
    return int(float(output))

# GUI එක
class VideoSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Splitter - Machan Edition")
        
        # Video File Picker
        tk.Label(root, text="Select Video File:").grid(row=0, column=0, padx=5, pady=5)
        self.video_file = tk.StringVar()
        tk.Entry(root, textvariable=self.video_file, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.browse_video).grid(row=0, column=2, padx=5, pady=5)

        # Split by Seconds
        tk.Label(root, text="Split by Seconds:").grid(row=1, column=0, padx=5, pady=5)
        self.split_seconds = tk.StringVar()
        tk.Entry(root, textvariable=self.split_seconds).grid(row=1, column=1, padx=5, pady=5)

        # Split by Manifest
        tk.Label(root, text="Or Split by Manifest:").grid(row=2, column=0, padx=5, pady=5)
        self.manifest_file = tk.StringVar()
        tk.Entry(root, textvariable=self.manifest_file, width=50).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.browse_manifest).grid(row=2, column=2, padx=5, pady=5)

        # Output Directory
        tk.Label(root, text="Output Directory:").grid(row=3, column=0, padx=5, pady=5)
        self.output_dir = tk.StringVar()
        tk.Entry(root, textvariable=self.output_dir, width=50).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.browse_output).grid(row=3, column=2, padx=5, pady=5)

        # Start Button
        tk.Button(root, text="Start Splitting", command=self.start_splitting).grid(row=4, column=1, pady=10)

    def browse_video(self):
        self.video_file.set(filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")]))

    def browse_manifest(self):
        self.manifest_file.set(filedialog.askopenfilename(filetypes=[("Manifest Files", "*.json *.csv")]))

    def browse_output(self):
        self.output_dir.set(filedialog.askdirectory())

    def start_splitting(self):
        try:
            video = self.video_file.get()
            seconds = self.split_seconds.get()
            manifest = self.manifest_file.get()
            output = self.output_dir.get() or None

            if not video:
                messagebox.showerror("Error", "Please select a video file!")
                return

            if seconds and manifest:
                messagebox.showerror("Error", "Choose either seconds or manifest, not both!")
                return

            if seconds:
                split_by_seconds(video, int(seconds), output)
                messagebox.showinfo("Success", "Video split by seconds successfully!")
            elif manifest:
                split_by_manifest(video, manifest, output)
                messagebox.showinfo("Success", "Video split by manifest successfully!")
            else:
                messagebox.showerror("Error", "Please enter seconds or select a manifest file!")
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong: {str(e)}")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSplitterApp(root)
    root.mainloop()