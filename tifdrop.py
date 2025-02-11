import ffmpeg
import os
os.environ["TKDND_LIBRARY"] = "/Users/devinwilson/anaconda3/lib/python3.11/site-packages/tkinterdnd2/tkdnd"
import shutil
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES  # Import the tkinterdnd2 module

def convert_mp4_to_tiff(mp4_files):
    for mp4_file in mp4_files:
        try:
            # Ensure file path is properly formatted (handles spaces and special characters)
            mp4_file = mp4_file.strip().strip("{}")  # Remove curly braces from paths (common in drag-and-drop)
            mp4_file = mp4_file.replace("\\", "/")  # Ensure proper path format

            if not os.path.isfile(mp4_file) or not mp4_file.lower().endswith(".mp4"):
                print(f"Skipping invalid file: {mp4_file}")
                continue  # Skip non-MP4 files

            # Get the directory and filename without extension
            original_dir = os.path.dirname(mp4_file)
            original_name = os.path.splitext(os.path.basename(mp4_file))[0]

            # Define output path using the original file name
            stack_path = os.path.join(original_dir, f"{original_name}.tiff")

            # Create a temporary folder in the original directory
            temp_dir = os.path.join(original_dir, f"temp_frames_{original_name}")
            os.makedirs(temp_dir, exist_ok=True)

            # Extract frames using FFmpeg
            print(f"Extracting frames from {mp4_file} into {temp_dir}...")
            ffmpeg.input(mp4_file).output(os.path.join(temp_dir, 'frame%04d.png')).run()

            # List extracted frames
            frame_files = sorted([f for f in os.listdir(temp_dir) if f.endswith('.png')])
            print(f"Extracted {len(frame_files)} frames from {mp4_file}")

            if not frame_files:
                raise ValueError(f"No frames extracted from {mp4_file}. Check FFmpeg installation.")

            # Convert to TIFF stack
            tiff_images = []
            for frame in frame_files:
                img_path = os.path.join(temp_dir, frame)
                img = Image.open(img_path).convert("RGB")  # Ensure consistent image mode
                tiff_images.append(np.array(img))

            # Save the TIFF stack in the same location as the original MP4
            print(f"Saving TIFF stack to: {stack_path}")

            Image.fromarray(tiff_images[0]).save(
                stack_path,
                save_all=True,
                append_images=[Image.fromarray(img) for img in tiff_images[1:]],
                compression="tiff_deflate"
            )

            print(f"TIFF stack saved successfully: {stack_path}")

            # Cleanup temporary files
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"Temporary files cleaned up for {mp4_file}")

        except Exception as e:
            print(f"Error occurred with {mp4_file}: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            messagebox.showerror("Error", f"An error occurred with {mp4_file}: {e}")

    messagebox.showinfo("Success", "All MP4 files processed successfully!")


def handle_drag_and_drop(event):
    # Get the dragged file paths
    file_paths = event.data.strip().strip("{}").split()  # Handles multiple files by splitting on spaces

    valid_files = [fp.replace("\\", "/") for fp in file_paths if fp.lower().endswith(".mp4")]

    if valid_files:
        convert_mp4_to_tiff(valid_files)
    else:
        messagebox.showerror("Error", "Please drop valid MP4 files.")


# Create the Tkinter window using TkinterDnD
root = TkinterDnD.Tk()  # This creates a TkinterDnD window instead of a standard Tkinter window
root.title("MP4 to TIFF Converter")

# Set up the window's dimensions and background color
root.geometry("400x400")
root.config(bg="#f0f0f0")

# Create drag-and-drop area (with a simple label)
drag_drop_area = tk.Label(
    root,
    text="Drag and drop MP4 files here",
    font=("Arial", 14),
    bg="#d0d0d0",
    width=30,
    height=10,
    relief="solid",
    anchor="center"
)
drag_drop_area.pack(padx=20, pady=80)

# Bind drag-and-drop event to the drag_drop_area
drag_drop_area.drop_target_register(DND_FILES)
drag_drop_area.dnd_bind('<<Drop>>', handle_drag_and_drop)

# Start the Tkinter event loop
root.mainloop()