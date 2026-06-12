import chromadb
from chromadb.utils import embedding_functions
import config
import uuid

class MemoryNode:
    def __init__(self, memory_queue, llm_queue):
        self.memory_queue = memory_queue
        self.llm_queue = llm_queue
        
        print("Initializing ChromaDB...")
        self.client = chromadb.PersistentClient(path=config.CHROMA_DB_DIR)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=config.EMBEDDING_MODEL)
        
        self.collection = self.client.get_or_create_collection(
            name="conversations",
            embedding_function=self.ef
        )
        print("ChromaDB initialized.")

    def run(self):
        while True:
            transcription = self.memory_queue.get()
            if transcription is None:
                break
                
            # Query past context
            results = self.collection.query(
                query_texts=[transcription],
                n_results=3
            )
            
            context = ""
            if results['documents'] and results['documents'][0]:
                context = " ".join(results['documents'][0])
                
            # Store the new utterance
            self.collection.add(
                documents=[transcription],
                ids=[str(uuid.uuid4())]
            )
            
            # Send to LLM
            self.llm_queue.put((context, transcription))
