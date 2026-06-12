import requests
import json
import config
import re

class LLMNode:
    def __init__(self, llm_queue, tts_queue, interruption_event):
        self.llm_queue = llm_queue
        self.tts_queue = tts_queue
        self.interruption_event = interruption_event
        
        self.system_prompt = (
            "You are a highly capable, concise, and helpful AI assistant named Ava. "
            "You speak in short, natural sentences suitable for a voice conversation. "
            "Do NOT use markdown, code blocks, or complex formatting. Keep answers brief."
        )

    def run(self):
        while True:
            item = self.llm_queue.get()
            if item is None:
                break
                
            # If an interruption happened before we even started generating, skip
            if self.interruption_event.is_set():
                continue
                
            context, transcription = item
            
            prompt = f"Previous context: {context}\nUser: {transcription}\nAva:"
            
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "system": self.system_prompt,
                "stream": True,
                "options": {
                    "num_ctx": 2048,
                    "num_predict": 100
                }
            }
            
            try:
                response = requests.post(f"{config.OLLAMA_HOST}/api/generate", json=payload, stream=True)
                response.raise_for_status()
                
                current_sentence = ""
                for line in response.iter_lines():
                    if self.interruption_event.is_set():
                        print("[LLM] Interrupted! Stopping generation.")
                        break
                        
                    if line:
                        data = json.loads(line)
                        token = data.get("response", "")
                        current_sentence += token
                        
                        # Chunk on sentence boundaries
                        if any(char in current_sentence for char in ['.', '!', '?', '\n']):
                            # Split cleanly if there are multiple sentences
                            parts = re.split(r'([.!?\n]+)', current_sentence)
                            chunk_to_send = ""
                            for i in range(len(parts) - 1):
                                chunk_to_send += parts[i]
                            
                            # It's possible parts is short, meaning no delimiter at the end
                            if chunk_to_send.strip():
                                self.tts_queue.put(chunk_to_send.strip())
                                print(f"[LLM Chunk]: {chunk_to_send.strip()}")
                                
                            current_sentence = parts[-1] if parts else ""
                        
                        if data.get("done"):
                            if current_sentence.strip():
                                self.tts_queue.put(current_sentence.strip())
                                print(f"[LLM Chunk]: {current_sentence.strip()}")
                            break

            except Exception as e:
                print(f"LLM Error: {e}")
