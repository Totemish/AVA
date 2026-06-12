from faster_whisper import WhisperModel
import config

class STTNode:
    def __init__(self, stt_queue, memory_queue):
        self.stt_queue = stt_queue
        self.memory_queue = memory_queue
        # Initialize faster-whisper for CPU
        print(f"Loading Whisper model {config.WHISPER_MODEL}...")
        self.model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
        print("Whisper model loaded.")

    def run(self):
        while True:
            audio_data = self.stt_queue.get()
            if audio_data is None:
                break # Exit signal
            
            print("Transcribing audio...")
            # faster-whisper can take a numpy array
            segments, info = self.model.transcribe(audio_data, beam_size=5, language="en")
            
            transcription = "".join([segment.text for segment in segments]).strip()
            
            if transcription:
                print(f"User: {transcription}")
                self.memory_queue.put(transcription)
