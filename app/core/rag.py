from typing import List, Dict
from app.core.embeddings import embedding_service
from app.services.supabase_client import supabase
from app.services.groq_client import groq_service


class RAGService:
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 3,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """Retrieve relevant documents from knowledge base"""
        # Generate query embedding
        query_embedding = embedding_service.embed_text(query)
        
        # Search in Supabase using pgvector
        result = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_count': top_k,
                'match_threshold': similarity_threshold
            }
        ).execute()
        
        return result.data if result.data else []
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        system_prompt: str = None
    ) -> str:
        """Generate AI response using RAG"""
        # Retrieve relevant context
        context_docs = self.retrieve_context(user_message)
        
        # Build context string
        if context_docs:
            context = "\n\n".join([
                f"[Source: {doc.get('metadata', {}).get('source', 'Unknown')}]\n{doc['content']}"
                for doc in context_docs
            ])
        else:
            context = "No specific context found in knowledge base."
        
        # Build system prompt with context
        if not system_prompt:
            system_prompt = f"""You are a helpful AI sales and support agent. 
Use the following context to answer questions accurately.

Context:
{context}

Instructions:
- Answer based on the context provided
- Be helpful, professional, and concise
- If you don't know something, say so
- Guide users toward providing their contact information naturally
"""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        response = groq_service.chat_completion(messages)
        
        return response


# Singleton instance
rag_service = RAGService()
