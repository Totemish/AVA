import sounddevice as sd
import numpy as np
from piper.voice import PiperVoice
import queue
import config
import json

class TTSNode:
    def __init__(self, tts_queue, interruption_event, ai_speaking_event):
        self.tts_queue = tts_queue
        self.interruption_event = interruption_event
        self.ai_speaking_event = ai_speaking_event
        
        print("Loading Piper TTS model...")
        self.voice = PiperVoice.load(config.PIPER_MODEL_FILE, config.PIPER_MODEL_CONFIG)
        
        # Load config to get sample rate
        with open(config.PIPER_MODEL_CONFIG, 'r', encoding='utf-8') as f:
            voice_config = json.load(f)
            self.sample_rate = voice_config.get('audio', {}).get('sample_rate', 22050)
            
        print(f"Piper TTS loaded. Sample rate: {self.sample_rate}")

    def run(self):
        while True:
            text_chunk = self.tts_queue.get()
            if text_chunk is None:
                break
                
            if self.interruption_event.is_set():
                continue # Skip if interrupted
                
            # Synthesize audio using the correct Piper API
            # voice.synthesize() yields AudioChunk objects per sentence
            self.ai_speaking_event.set()
            
            try:
                stream = sd.OutputStream(samplerate=self.sample_rate, channels=1, dtype='int16')
                stream.start()
                
                for audio_chunk in self.voice.synthesize(text_chunk):
                    if self.interruption_event.is_set():
                        print("[TTS] Interrupted! Stopping playback.", flush=True)
                        break
                    
                    # AudioChunk has audio_int16_array (numpy array of int16)
                    audio_array = audio_chunk.audio_int16_array
                    if audio_array is not None and len(audio_array) > 0:
                        stream.write(audio_array)
                    
                stream.stop()
                stream.close()
            except Exception as e:
                print(f"[TTS] Error: {e}", flush=True)
            finally:
                self.ai_speaking_event.clear()
                
                if self.interruption_event.is_set():
                    # Consume the rest of the tts queue and clear the interruption flag
                    while not self.tts_queue.empty():
                        try:
                            self.tts_queue.get_nowait()
                        except queue.Empty:
                            break
                    self.interruption_event.clear()
