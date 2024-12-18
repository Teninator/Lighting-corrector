import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Functions for white balance and lighting correction
def auto_white_balance(image):
    """Applies white balance correction using the Gray World algorithm."""
    result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(result)
    a_mean = np.mean(a)
    b_mean = np.mean(b)
    a -= np.uint8(a_mean - 128)
    b -= np.uint8(b_mean - 128)
    result = cv2.merge((l, a, b))
    return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

def fix_lighting(image):
    """Adjusts brightness and contrast using CLAHE."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    lab_clahe = cv2.merge((l_clahe, a, b))
    return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

def process_image(image_path):
    """Processes a single image file."""
    image = cv2.imread(image_path)
    if image is None:
        messagebox.showerror("Error", "Failed to read the image file.")
        return None, None
    corrected_image = auto_white_balance(image)
    corrected_image = fix_lighting(corrected_image)
    return image, corrected_image

def resize_to_fit(image, max_width, max_height):
    """Resizes an image to fit within the given dimensions, maintaining aspect ratio."""
    height, width = image.shape[:2]
    scale = min(max_width / width, max_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized

# GUI Functions
def browse_file():
    """Opens file dialog to select an image or video."""
    file_path = filedialog.askopenfilename(
        filetypes=[("Image and Video Files", "*.jpg *.jpeg *.png *.mp4")]
    )
    if not file_path:
        return
    
    if file_path.endswith(('.jpg', '.jpeg', '.png')):
        handle_image(file_path)
    elif file_path.endswith('.mp4'):
        handle_video(file_path)

def handle_image(file_path):
    """Handles processing and displaying an image."""
    global original_img, corrected_img
    
    original, corrected = process_image(file_path)
    if original is None or corrected is None:
        return

    # Resize images to fit the display panels
    display_width, display_height = 400, 400
    original_resized = resize_to_fit(original, display_width, display_height)
    corrected_resized = resize_to_fit(corrected, display_width, display_height)
    
    # Convert images to RGB format and update the canvases
    original_resized = cv2.cvtColor(original_resized, cv2.COLOR_BGR2RGB)
    corrected_resized = cv2.cvtColor(corrected_resized, cv2.COLOR_BGR2RGB)
    original_img = ImageTk.PhotoImage(Image.fromarray(original_resized))
    corrected_img = ImageTk.PhotoImage(Image.fromarray(corrected_resized))
    
    canvas_original.create_image(0, 0, anchor=tk.NW, image=original_img)
    canvas_corrected.create_image(0, 0, anchor=tk.NW, image=corrected_img)

def handle_video(file_path):
    """Handles processing and saving a video."""
    output_path = filedialog.asksaveasfilename(
        defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")]
    )
    if not output_path:
        return
    
    success = process_video(file_path, output_path)
    if success:
        messagebox.showinfo("Success", f"Video saved to {output_path}")
    else:
        messagebox.showerror("Error", "Failed to process the video.")

def process_video(video_path, output_path):
    """Processes a video file and saves the corrected version."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Error", "Failed to read the video file.")
        return False
    
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        corrected_frame = auto_white_balance(frame)
        corrected_frame = fix_lighting(corrected_frame)
        out.write(corrected_frame)
    
    cap.release()
    out.release()
    return True

# Main GUI
root = tk.Tk()
root.title("White Balance and Lighting Correction")
root.geometry("850x500")

# Panels for displaying images
canvas_original = tk.Canvas(root, width=400, height=400, bg="gray")
canvas_original.grid(row=0, column=0, padx=10, pady=10)
canvas_corrected = tk.Canvas(root, width=400, height=400, bg="gray")
canvas_corrected.grid(row=0, column=1, padx=10, pady=10)

# Buttons
browse_button = tk.Button(root, text="Browse Image/Video", command=browse_file, width=30)
browse_button.grid(row=1, column=0, columnspan=2, pady=20)

# Run the GUI
root.mainloop()
