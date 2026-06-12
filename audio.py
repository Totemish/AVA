import numpy as np
import sounddevice as sd
import torch
import time
import threading
import config

class AudioInputNode:
    def __init__(self, stt_queue, interruption_event, ai_speaking_event):
        self.stt_queue = stt_queue
        self.interruption_event = interruption_event
        self.ai_speaking_event = ai_speaking_event
        
        # Load VAD model via official silero-vad package
        print("Loading Silero VAD model...", flush=True)
        from silero_vad import load_silero_vad
        self.vad_model = load_silero_vad(onnx=True)
        print("Silero VAD loaded.", flush=True)
        
        self.audio_buffer = []
        self.is_recording = False
        self.silence_start_time = None
        self._running = False

    def _apply_vad(self, audio_chunk):
        """Run VAD on a chunk of audio. Returns speech probability."""
        tensor = torch.from_numpy(audio_chunk)
        prob = self.vad_model(tensor, config.SAMPLE_RATE).item()
        return prob

    def _listen_loop(self):
        """Blocking loop that reads audio in chunks and processes VAD."""
        try:
            with sd.InputStream(
                device=config.AUDIO_INPUT_DEVICE,
                samplerate=config.SAMPLE_RATE,
                channels=1,
                blocksize=config.CHUNK_SIZE,
                dtype='float32'
            ) as stream:
                print("[Audio] Stream opened successfully. Listening...", flush=True)
                
                while self._running:
                    data, overflowed = stream.read(config.CHUNK_SIZE)
                    if overflowed:
                        print("[Audio] Warning: input overflow", flush=True)
                    
                    audio_chunk = data[:, 0] * config.AUDIO_GAIN
                    audio_chunk = np.clip(audio_chunk, -1.0, 1.0)
                    
                    max_amp = np.max(np.abs(audio_chunk))
                    
                    try:
                        prob = self._apply_vad(audio_chunk)
                    except Exception as e:
                        print(f"[Audio] VAD error: {e}", flush=True)
                        self.vad_model.reset_states()
                        continue
                    
                    is_speech = prob > config.VAD_THRESHOLD

                    # Print live status every ~1 second
                    if not hasattr(self, '_debug_counter'):
                        self._debug_counter = 0
                    self._debug_counter += 1
                    if self._debug_counter % 31 == 0:
                        status = "SPEECH" if is_speech else "silence"
                        print(f"[Audio] amp={max_amp:.4f} vad={prob:.4f} [{status}]", flush=True)

                    # Interruption handling
                    if is_speech and self.ai_speaking_event.is_set():
                        self.interruption_event.set()

                    if is_speech:
                        if not self.is_recording:
                            self.is_recording = True
                            self.audio_buffer = []
                            print("\n[VAD] Speech detected! Recording...", flush=True)
                        self.silence_start_time = None
                        self.audio_buffer.append(audio_chunk)
                    else:
                        if self.is_recording:
                            self.audio_buffer.append(audio_chunk)
                            if self.silence_start_time is None:
                                self.silence_start_time = time.time()
                            
                            silence_duration = (time.time() - self.silence_start_time) * 1000
                            if silence_duration > config.MIN_SILENCE_DURATION_MS:
                                self.is_recording = False
                                audio_data = np.concatenate(self.audio_buffer)
                                self.vad_model.reset_states()
                                
                                if len(audio_data) > config.SAMPLE_RATE * 0.5:
                                    print(f"[VAD] End of speech. Sending {len(audio_data)/config.SAMPLE_RATE:.1f}s of audio to STT...", flush=True)
                                    self.stt_queue.put(audio_data)
                                else:
                                    print("[VAD] Speech too short, ignoring.", flush=True)

        except Exception as e:
            print(f"[Audio] FATAL ERROR in listen loop: {e}", flush=True)
            import traceback
            traceback.print_exc()

    def start(self):
        print("Starting Audio Input Node...", flush=True)
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="Audio_Thread")
        self._thread.start()

    def stop(self):
        self._running = False
        if hasattr(self, '_thread'):
            self._thread.join(timeout=2)
