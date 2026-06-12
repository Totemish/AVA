import threading
import queue
import time
import sys

from audio import AudioInputNode
from stt import STTNode
from memory import MemoryNode
from llm import LLMNode
from tts import TTSNode

import download_models

def main():
    print("Initializing AVA Real-Time Pipeline...")
    download_models.setup_models()
    
    # Shared queues
    stt_queue = queue.Queue()
    memory_queue = queue.Queue()
    llm_queue = queue.Queue()
    tts_queue = queue.Queue()
    
    # Shared events
    interruption_event = threading.Event()
    ai_speaking_event = threading.Event()
    
    # Initialize nodes
    audio_node = AudioInputNode(stt_queue, interruption_event, ai_speaking_event)
    stt_node = STTNode(stt_queue, memory_queue)
    memory_node = MemoryNode(memory_queue, llm_queue)
    llm_node = LLMNode(llm_queue, tts_queue, interruption_event)
    tts_node = TTSNode(tts_queue, interruption_event, ai_speaking_event)
    
    # Start worker threads
    threads = [
        threading.Thread(target=stt_node.run, daemon=True, name="STT_Thread"),
        threading.Thread(target=memory_node.run, daemon=True, name="Memory_Thread"),
        threading.Thread(target=llm_node.run, daemon=True, name="LLM_Thread"),
        threading.Thread(target=tts_node.run, daemon=True, name="TTS_Thread"),
    ]
    
    for t in threads:
        t.start()
        
    # Start audio recording
    audio_node.start()
    
    print("\n--- AVA is listening. Press Ctrl+C to stop. ---\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down pipeline...")
        audio_node.stop()
        print("Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
