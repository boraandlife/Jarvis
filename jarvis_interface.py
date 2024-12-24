import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import pygame
from scipy.io import wavfile
import threading

class AudioWaveformApp:
    def __init__(self, master):
        self.master = master
        master.title("Dynamic Audio Waveform")

        # Set background color of the main window
        self.master.configure(bg='black')

        # Make the window borderless
        self.master.overrideredirect(True)

        # Initialize fullscreen state
        self.fullscreen = False

        # Set initial window size and position
        self.update_window_size(800, 400)

        self.canvas = tk.Canvas(master, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Load and display background GIF
        self.original_gif_frames = self.load_gif("background.gif")  # Replace with your GIF path
        self.gif_frames = self.original_gif_frames.copy()  # Initialize gif_frames
        self.gif_index = 0
        self.gif_image_display = None  # Placeholder for the resized GIF image
        self.animate_gif()  # Start the GIF animation

        # Create a frame for buttons
        button_frame = tk.Frame(master, bg='black')
        button_frame.pack(pady=10)

        # Create buttons with red background
        self.play_button = tk.Button(button_frame, text="Play Audio", command=self.load_and_play, bg='red', fg='white')
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.maximize_button = tk.Button(button_frame, text="Maximize", command=self.toggle_maximize, bg='red', fg='white')
        self.maximize_button.pack(side=tk.LEFT, padx=5)

        self.close_button = tk.Button(button_frame, text="Close", command=self.close_app, bg='red', fg='white')
        self.close_button.pack(side=tk.LEFT, padx=5)

        pygame.mixer.init()
        self.samples = None
        self.sample_rate = None
        self.file_path = None
        self.waveform_data = None

        self.is_playing = False
        self.audio_thread = None  # Store the thread reference

        # Bind mouse events for dragging the window
        self.canvas.bind("<Button-1>", self.make_draggable)
        self.canvas.bind("<B1-Motion>", self.drag_window)

        # Bind the configure event to update background image size
        self.master.bind("<Configure>", self.on_resize)

        # Set minimum window size
        self.master.minsize(800, 400)

        # Schedule waveform update
        self.master.after(100, self.update_waveform)

    def load_gif(self, path):
        self.gif_image = Image.open(path)
        frames = []
        try:
            while True:
                frame = self.gif_image.copy()
                frames.append(frame)
                self.gif_image.seek(len(frames))  # Move to the next frame
        except EOFError:
            pass  # End of the GIF

        return frames

    def update_gif_size(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Resize all frames
        self.gif_frames = [frame.resize((width, height), Image.LANCZOS) for frame in self.original_gif_frames]

    def animate_gif(self):
        if self.gif_frames:
            # Resize the current frame for display
            current_frame = self.gif_frames[self.gif_index]
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()

            # Resize only once and create PhotoImage
            resized_frame = current_frame.resize((width, height), Image.LANCZOS)
            self.gif_image_display = ImageTk.PhotoImage(resized_frame)  # Create a single PhotoImage

            # Update the canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.gif_image_display)

            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.master.after(100, self.animate_gif)  # Schedule the next frame

    def on_resize(self, event):
        self.update_gif_size()  # Resize the GIF on window resize
        self.redraw_waveform()  # Redraw waveform on resize

    def update_window_size(self, width, height):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def make_draggable(self, event):
        self.master.x = event.x
        self.master.y = event.y

    def drag_window(self, event):
        x = self.master.winfo_x() - self.master.x + event.x
        y = self.master.winfo_y() - self.master.y + event.y
        self.master.geometry(f"+{x}+{y}")

    def load_and_play(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        if self.file_path:
            self.load_audio(self.file_path)
            self.audio_thread = threading.Thread(target=self.play_audio)
            self.audio_thread.start()  # Play audio in a separate thread
            self.prepare_waveform()  # Prepare the waveform data
            self.animate_waveform()

    def load_audio(self, file_path):
        if file_path.endswith('.wav'):
            self.sample_rate, self.samples = self.read_wav(file_path)

    def read_wav(self, file_path):
        sample_rate, samples = wavfile.read(file_path)
        if samples.ndim > 1:  # If stereo, take one channel
            samples = samples[:, 0]  # Keep one channel
        return sample_rate, samples

    def play_audio(self):
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.play()
        self.is_playing = True

        while self.is_playing:
            if not pygame.mixer.music.get_busy():
                self.is_playing = False

    def prepare_waveform(self):
        if self.samples is not None:
            height = self.canvas.winfo_height()
            self.waveform_data = (self.samples / np.max(np.abs(self.samples))) * (height / 2 - 10)
            print("Waveform data prepared:", self.waveform_data)  # Debugging output

    def animate_waveform(self):
        if self.is_playing:
            self.redraw_waveform()  # Draw the waveform
            self.master.after(100, self.animate_waveform)  # Schedule next update

    def redraw_waveform(self):
        self.canvas.delete("waveform")  # Clear previous waveform
        if self.waveform_data is not None and len(self.waveform_data) > 0:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()

            # Get the current playback position
            current_position = pygame.mixer.music.get_pos() / 1000 * self.sample_rate
            current_position = int(current_position)

            # Draw the waveform
            for i in range(1, width):
                x1 = i - 1
                x2 = i

                sample_index1 = int(current_position + i * len(self.waveform_data) / width)
                sample_index2 = int(current_position + (i + 1) * len(self.waveform_data) / width)

                # Ensure indices are within bounds
                if 0 <= sample_index1 < len(self.waveform_data) and 0 <= sample_index2 < len(self.waveform_data):
                    y1 = height / 2 - self.waveform_data[sample_index1]
                    y2 = height / 2 - self.waveform_data[sample_index2]
                    self.canvas.create_line(x1, y1 + height / 2, x2, y2 + height / 2, fill='cyan', tags="waveform")

    def update_waveform(self):
        self.redraw_waveform()  # Update waveform regularly
        self.master.after(100, self.update_waveform)  # Continue updating

    def toggle_maximize(self):
        try:
            if self.fullscreen:
                self.master.overrideredirect(True)  # Return to borderless
                self.master.attributes("-fullscreen", False)  # Exit fullscreen
                self.update_window_size(800, 400)  # Set back to original size
            else:
                self.master.overrideredirect(False)  # Set to standard window
                self.master.attributes("-fullscreen", True)  # Enter fullscreen
            self.fullscreen = not self.fullscreen  # Toggle the state
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")

    def close_app(self):
        self.is_playing = False  # Stop the audio playback
        pygame.mixer.music.stop()  # Stop pygame music
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()  # Wait for the audio thread to finish
        self.master.quit()  # Close the application

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioWaveformApp(root)
    root.mainloop()
