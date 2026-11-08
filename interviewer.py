from google import genai
from google.genai import types
import wave

# Const for temporary audio file.
TEMP_AUDIO_FILE = "out.wav"



class Interviewer:
    """
    The interviewer class is an AI agent that interacts with the user. Its job is to
    guide and collaborate with the user as if they were experiencing a real technical
    interview.

    Attributes:
        client: Gemini library.
        chat: Gemini chat with history. Takes in text and/or audio data.
        is_listening: Boolean indicating if the interviewer is listening or not.
        audio_frames: List that holds the transcription data of the user.
    """
    def __init__(self):
        self.client = genai.Client(api_key="", http_options=types.HttpOptions( # The API key is only hard-coded for the hackathon, will be protected once I develop it more after :)
        api_version="v1beta"))
        sys_instructions = ""
        with open("interviewer_system_instructions", 'r') as f:
            sys_instructions = f.read()

        self.chat = self.client.chats.create(
            model="gemini-3.8-flash",
            config=types.GenerateContentConfig(
                system_instruction=sys_instructions,
                response_modalities=["audio"],
            ),
        )

        self.is_listening = False
        self.audio_frames = []

    def create_technical_description(self, code):
        sys_instr = ""
        with open("technical_description_system_instructions.md", "r") as f:
            sys_instr = f.read()
        try:
            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=code,
                config=types.GenerateContentConfig(
                    system_instruction= sys_instr
                )
            )
            return response.text
        except Exception as e:
            print(f"Error with Technical Description: {e}")


    def send_message(self, params):
        try:
            response = self.chat.send_message(message=params)
            return response # Returns just the text of the response.
        except Exception as e:
            print(f"Error with Generation: {e}")


    def text_to_speech(self, text: str, output_file: str = "output.wav"):
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Kore"
                            )
                        )
                    )
                )
            )

            audio_data = response.candidates[0].content.parts[0].inline_data.data

            with wave.open(output_file, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(24000)
                wav_file.writeframes(audio_data)

            return output_file
        except Exception as e:
            print(f"Error with TTS: {e}")

    def checkin(self):
        response = self.send_message(params="Check-in with me")

        return response
