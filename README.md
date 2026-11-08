I built InterviewAI, an AI agent designed to simulate a technical interview to help
aspiring software engineers practice coding interviews in a realistic environment. Users
can use the integrated code editor to write Python code and can interact with the AI interviewer 
through voice. The interview can perform many tasks, from answering questions and guiding
the user based on their current code, to periodically checking in if the user seems stuck.

For InterviewAI, Python is used entirely for the front and backend. The GUI and code editor is powered by
the Tkinter library, and sound handling, such as microphone recording, audio processing, and 
audio playback is handled by SoundDevice, NumPy, and SciPy. Behind the scenes, the backend
is multithreaded to prevent blocking the user interface. And the interview agent is powered
by Google's Gemini. Thinking, natural speech processing, and code understanding is all performed 
by the Gemini 3.8 Flash model. The TTS is handled by the Gemini 2.5 Flash Preview TTS model. 

In the future development of this project, I want to integrate data streaming so that 
text appears as soon as Gemini thinks of it, and will lead to TTS starting sooner and 
providing a smoother, more seamless experience. I also want to integrate overall interview
feedback once the interview round ends. This will help the user gauge how well they did, both
technically and their communication with the interviewer. I also want to implement 
different levels of difficulty and introduce more topics. Lastly, I would like to add automatic
VAD, which takes away the need for a push-to-talk button and makes the interview appear more
realistic. In the end, I want for InterviewAI to be an accessible and interactive platform
that can help people of all stages of their SDE career build their confidence and
technical interviewing skills.