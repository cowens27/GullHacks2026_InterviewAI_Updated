import tkinter as tk
from tkinter import ttk, scrolledtext
import customtkinter as ctk
import interviewer
import threading
import sounddevice as sd
import numpy as np
import wave

import scipy.io.wavfile as wav
import io

from google.genai import types

agent = interviewer.Interviewer()

BG = "#0B1120"
PANEL = "#111827"
EDITOR = "#1E293B"
BORDER = "#263244"
ACCENT = "#3B82F6"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"


window = ctk.CTk()
window.configure(bg=BG)

SAMPLE_RATE = 16000

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


UI_FONT = ("Courier New", 14)
HEADING_FONT = ("Segoe UI", 18, "bold")
CODE_FONT = ("Cascadia Code", 14)
AGENT_FONT = ("Cascadia Code", 9)
style = ttk.Style()
style.theme_use("clam")
style.configure("Blue.TLabelframe", background=BG, bordercolor=BORDER, lightcolor=BG, font=UI_FONT, darkcolor=BG)
style.configure("Custom.TLabelframe.Label", background=BG, foreground=BG)
class UI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.window = window
        self.window.configure()
        self.window.title("InterviewAI - Ace Your Technical Interviews")
        self.window.geometry("1200x800")
        self.resizable(True, True)

        # Header for settings
        self.mgmt_frame = ctk.CTkFrame(self.window, height=80, corner_radius=14)
        self.mgmt_frame.pack(side="top", fill="x", padx=10, pady=10)
        # User side
        self.user_frame = ttk.LabelFrame(self.window, text="Candidate Code (Python)", style="Blue.TLabelframe", )
        self.user_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        # Agent side
        self.agent_frame = ttk.LabelFrame(self.window, text="Interview & Chat Log", style="Blue.TLabelframe")
        self.agent_frame.pack(fill=tk.BOTH, expand=True)
        # User input
        self.user_text = ctk.CTkTextbox(self.user_frame, height=400, width=600, undo=True, font=CODE_FONT, bg_color=PANEL)
        self.user_text.pack(side="left", expand=True, padx=10, pady=10)
        # Chat log
        self.agent_text = ctk.CTkTextbox(self.agent_frame, height=400, width=200, wrap="word", font=AGENT_FONT, bg_color=PANEL)
        self.agent_text.pack(side="top", expand=True, padx=10, pady=10 )

        # This places the description label on the header.

        # Put the starting code in the user's box.
        with open("starting_code", "r") as f:
            temp = f.read()
            self.user_text.insert(tk.END, temp)
            response = agent.create_technical_description(temp)
            self.description = ctk.CTkLabel(self.mgmt_frame, anchor="w", justify="left", text=response, font=(HEADING_FONT, 8), corner_radius=14)
            self.description.pack(side="top", expand=True, padx=10, pady=10)


        self.push_to_talk = ctk.CTkButton(self.agent_frame, text="Push to talk", font=UI_FONT, bg_color=BG)
        self.push_to_talk.pack(side="bottom", expand=True)

        self.push_to_talk.bind("<ButtonPress-1>", self.push_to_talk_pushed)
        self.push_to_talk.bind("<ButtonRelease-1>", self.push_to_talk_released)

        self.bind("<KeyPress-Alt_L>", self.push_to_talk_pushed)
        self.bind("<KeyRelease-Alt_L>", self.push_to_talk_released)

        self.bind("<KeyPress-Alt_R>", self.push_to_talk_pushed)
        self.bind("<KeyRelease-Alt_R>", self.push_to_talk_released)



        self.timer_duration = 90_000
        self.timer_id = None
        self.user_text.bind("<Return>", self.reset_timer, add="+")
        self.start_timer()


        # Intro message for the interviewee.
        self.introduction()

    def start_timer(self):
        self.timer_id = self.window.after(self.timer_duration, self.timer_expired)

    def reset_timer(self, event=None):
        if self.timer_id is not None:
            self.window.after_cancel(self.timer_id)

        self.start_timer()

    def timer_expired(self):
        self.timer_id = None
        print("Checkin-after duration reached")
        # self.on_inactivity()
        threading.Thread(target=self.on_inactivity, daemon=True).start()
        self.start_timer()

    def on_inactivity(self):
        # dummy = self.get_dummy_wave()
        self.timer_duration *= 2
        response = agent.checkin()
        temp = response.text.strip()
        threading.Thread(target=self.speak_and_play, args=(temp,), daemon=True).start()
        temp:str = response.text.strip()
        self.agent_text.insert(tk.END, "Interviewer: " + temp + "\n\n")

    def callback(self, indata, frames, time, status):
        if agent.is_listening:
            agent.audio_frames.append(indata.copy())

    def record_audio_loop(self):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16', callback=self.callback):
            while agent.is_listening:
                sd.sleep(50)

    def agent_turn(self, code_context):
        if not agent.audio_frames:
            return

        audio_data = np.concatenate(agent.audio_frames, axis=0)
        if len(audio_data) < SAMPLE_RATE * 0.3:
            return

        wav_io = io.BytesIO()
        wav.write(wav_io, SAMPLE_RATE, audio_data)
        wav_bytes = wav_io.getvalue()

        try:
            audio_part = types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav")
            response = agent.send_message(params=[audio_part, code_context])
            ai_text = response.text.strip()
            # print(ai_text)
            self.agent_text.insert(tk.END, "Interviewer: " + ai_text + "\n\n")
            threading.Thread(target=self.speak_and_play, args=(ai_text,), daemon=True).start()
            # agent.text_to_speech(ai_text)

        except Exception as e:
            return

    def speak_and_play(self, text):
        try:
            file_path = agent.text_to_speech(text)
            if file_path:
                self.play_audio(file_path)
        except Exception as e:
            print(f"Audio error: {e}")

    def push_to_talk_pushed(self, event):
        self.push_to_talk.configure(text="Listening...")
        print("Pressed")
        self.reset_timer()
        if agent.is_listening:
            return

        agent.is_listening = True
        agent.audio_frames = []

        threading.Thread(target=self.record_audio_loop, daemon=True).start()

    def push_to_talk_released(self, event):
        self.push_to_talk.configure(text="Push to talk")
        print("Released")
        self.reset_timer()
        current_code = self.user_text.get("1.0", tk.END).strip()
        code_context = (
            f"[Current Candidate Code in Editor]:\n"
            f"'''python\n{current_code}\n'''\n"
            f"Please listen to my attached voice question and respond to it."
        )
        print(code_context)
        if not agent.is_listening:
            return

        agent.is_listening = False

        threading.Thread(target=lambda: self.agent_turn(code_context), daemon=True).start()

    def play_audio(self, file_path: str):
        sample_rate, audio_data = wav.read(file_path)

        sd.play(audio_data, sample_rate)
        sd.wait()

    def log(self, sender, text):
        self.agent_text.config(state=tk.NORMAL)
        self.agent_text.insert(tk.END, f"{sender}: {text}\n\n")
        self.agent_text.see(tk.END)
        self.agent_text.config(state=tk.DISABLED)

    def introduction(self):
        response = agent.send_message("Introduce yourself briefly")
        temp = response.text.strip()
        threading.Thread(target=self.speak_and_play, args=(temp,), daemon=True).start()
        self.agent_text.insert(tk.END, "Interviewer: " + temp + "\n\n")



def main():
    ui = UI()
    ui.window.mainloop()

if __name__ == "__main__":
    main()