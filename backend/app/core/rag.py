from typing import List, Dict
from app.core.embeddings import embedding_service
from app.db.pg_direct import test_vector_search_direct
from app.services.groq_client import groq_service


class RAGService:
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 3,
        similarity_threshold: float = 0.5
    ) -> List[Dict]:
        """Retrieve relevant documents from knowledge base"""
        query_embedding = embedding_service.embed_text(query)
        docs = test_vector_search_direct(query_embedding, top_k=top_k)
        return docs
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        additional_instructions: str = ""
    ) -> str:
        """Generate AI response using RAG"""
        context_docs = self.retrieve_context(user_message)
        
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
        
        response = groq_service.chat_completion(messages, temperature=0.3)
        
        return response


# Singleton instance
rag_service = RAGService()
