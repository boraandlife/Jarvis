import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import pygame
from scipy.io import wavfile
from pydub import AudioSegment
import threading


class AudioWaveformApp:
    def __init__(self, master):
        self.master = master
        master.title("Dynamic Audio Waveform")

        # Make the window borderless
        self.master.overrideredirect(True)

        # Initialize fullscreen state
        self.fullscreen = False

        # Set initial window size and position
        self.update_window_size(800, 400)

        self.canvas = tk.Canvas(master)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Load and display background image
        self.load_background_image("background.jpg")  # Replace with your image path

        # Create a frame for buttons
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        self.play_button = tk.Button(button_frame, text="Play Audio", command=self.load_and_play)
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.maximize_button = tk.Button(button_frame, text="Maximize", command=self.toggle_maximize)
        self.maximize_button.pack(side=tk.LEFT, padx=5)

        self.close_button = tk.Button(button_frame, text="Close", command=self.close_app)
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

    def on_resize(self, event):
        self.update_background_image()
        if self.waveform_data is not None:
            self.prepare_waveform()  # Reprepare waveform data on resize

    def update_window_size(self, width, height):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def load_background_image(self, path):
        self.original_image = Image.open(path)
        self.update_background_image()

    def update_background_image(self):
        window_width = self.master.winfo_width()
        window_height = self.master.winfo_height()
        resized_image = self.original_image.resize((window_width, window_height), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_photo)

    def make_draggable(self, event):
        self.master.x = event.x
        self.master.y = event.y

    def drag_window(self, event):
        x = self.master.winfo_x() - self.master.x + event.x
        y = self.master.winfo_y() - self.master.y + event.y
        self.master.geometry(f"+{x}+{y}")

    def load_and_play(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        if self.file_path:
            self.load_audio(self.file_path)
            self.audio_thread = threading.Thread(target=self.play_audio)
            self.audio_thread.start()  # Play audio in a separate thread
            self.prepare_waveform()  # Prepare the waveform data
            self.animate_waveform()

    def load_audio(self, file_path):
        if file_path.endswith('.wav'):
            self.sample_rate, self.samples = self.read_wav(file_path)
        elif file_path.endswith('.mp3'):
            self.sample_rate, self.samples = self.read_mp3(file_path)

    def read_wav(self, file_path):
        sample_rate, samples = wavfile.read(file_path)
        if samples.ndim > 1:  # If stereo, take one channel
            samples = samples[:, 0]
        return sample_rate, samples

    def read_mp3(self, file_path):
        audio = AudioSegment.from_mp3(file_path)
        audio = audio.set_channels(1)  # Convert to mono
        samples = np.array(audio.get_array_of_samples())
        return audio.frame_rate, samples

    def play_audio(self):
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.play()
        self.is_playing = True

        while self.is_playing:
            if not pygame.mixer.music.get_busy():
                self.is_playing = False

    def prepare_waveform(self):
        if self.samples is not None:
            # Scale samples to fit the canvas height and prepare static waveform data
            height = self.canvas.winfo_height()
            self.waveform_data = (self.samples / np.max(np.abs(self.samples))) * (height / 2 - 10)

    def animate_waveform(self):
        if self.is_playing:
            self.canvas.delete("waveform")
            self.draw_waveform()  # Draw the waveform
            self.master.after(100, self.animate_waveform)  # Schedule next update

    def draw_waveform(self):
        if self.waveform_data is None or len(self.waveform_data) == 0:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Get the current playback position
        current_position = pygame.mixer.music.get_pos() / 1000 * self.sample_rate
        current_position = int(current_position)

        # Draw the waveform
        for i in range(1, width):
            x1 = i - 1
            x2 = i

            sample_index1 = current_position + int(i * len(self.waveform_data) / width)
            sample_index2 = current_position + int((i + 1) * len(self.waveform_data) / width)

            # Make sure we don't go out of bounds
            if 0 <= sample_index1 < len(self.waveform_data) and 0 <= sample_index2 < len(self.waveform_data):
                y1 = height / 2 - self.waveform_data[sample_index1]
                y2 = height / 2 - self.waveform_data[sample_index2]
                self.canvas.create_line(x1, y1 + height / 2, x2, y2 + height / 2, fill='cyan', tags="waveform")

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
