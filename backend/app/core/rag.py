from typing import List, Dict
from app.core.embeddings import embedding_service
from app.services.groq_client import groq_service
from app.services.qdrant_service import qdrant_service


class RAGService:
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 2,
        similarity_threshold: float = 0.5
    ) -> List[Dict]:
        """Retrieve relevant documents from Qdrant"""
        import time
        
        t1 = time.time()
        query_embedding = embedding_service.embed_text(query)
        print(f"  ➡️ Embedding [{(time.time()-t1)*1000:.0f}ms]")
        
        t2 = time.time()
        docs = qdrant_service.search(
            query_vector=query_embedding,
            top_k=top_k,
            score_threshold=similarity_threshold
        )
        print(f"  ➡️ Qdrant search [{(time.time()-t2)*1000:.0f}ms] - Found {len(docs)} docs")
        
        return docs
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        additional_instructions: str = ""
    ) -> str:
        """Generate AI response using RAG"""
        import time
        t_start = time.time()
        
        context_docs = self.retrieve_context(user_message)
        t_context = time.time()
        print(f"  ➡️ Context retrieval total [{(t_context-t_start)*1000:.0f}ms]")
        
        if context_docs:
            context = "\n\n".join([
                f"[Source: {doc.get('metadata', {}).get('source', 'Unknown')}]\n{doc['content']}"
                for doc in context_docs
            ])
        else:
            context = "No specific context found in knowledge base."
        
        # Build system prompt with lead capture instructions integrated
        lead_capture_note = ""
        if "MUST ask for their contact information" in additional_instructions:
            lead_capture_note = "\n\nIMPORTANT LEAD CAPTURE: After answering the user's question, you MUST ask for their email address to proceed. Use a natural transition like: 'To get you started, what's your email address?' or 'Great! I'll need your email to send you the details.'"
        
        system_prompt = f"""You are a helpful AI sales and support agent.

CRITICAL INSTRUCTIONS:
1. You MUST answer ONLY using the information in the context below
2. DO NOT make up prices, features, or any information
3. If the context doesn't contain the answer, say "I don't have that information"
4. NEVER invent pricing - use ONLY what's in the context{lead_capture_note}

=== CONTEXT (USE ONLY THIS INFORMATION) ===
{context}
=== END OF CONTEXT ===

Rules:
- Answer based STRICTLY on the context above
- Be helpful and professional
- If asked about pricing, use ONLY the prices from the context
- Do not add information not in the context
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        t_llm = time.time()
        response = groq_service.chat_completion(messages, temperature=0.3)
        print(f"  ➡️ LLM call (Groq) [{(time.time()-t_llm)*1000:.0f}ms]")
        
        return response


# Singleton instance
rag_service = RAGService()
