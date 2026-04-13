from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.core.rag import rag_service
from app.core.lead_capture import lead_capture_service
from app.core.conversation import conversation_service, ConversationState
from app.db import conversations as conv_db
from app.db import messages as msg_db
from app.db import leads as leads_db
from app.utils.text_processing import extract_email, extract_name

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        print(f"[DEBUG] Received chat request: {request.message}")
        
        conversation = conv_db.get_or_create_conversation(request.session_id)
        conversation_id = conversation['id']
        print(f"[DEBUG] Conversation ID: {conversation_id}")
        
        lead_already_captured = leads_db.lead_exists(conversation_id)
        message_count = msg_db.count_user_messages(conversation_id)
        
        msg_db.create_message(conversation_id, 'user', request.message)
        
        intent_data = lead_capture_service.detect_intent(request.message)
        print(f"[DEBUG] Intent detected: {intent_data}")
        
        state = conversation_service.get_state(
            message_count,
            lead_already_captured,
            intent_data
        )
        
        email_in_message = extract_email(request.message)
        name_in_message = extract_name(request.message)
        
        if (email_in_message or request.user_email) and not lead_already_captured:
            email = email_in_message or request.user_email
            name = name_in_message or request.user_name
            
            leads_db.create_lead(
                conversation_id=conversation_id,
                email=email,
                name=name,
                intent=intent_data.get('intent'),
                metadata={'quality': intent_data.get('quality')}
            )
            lead_already_captured = True
            state = ConversationState.CAPTURED
        
        history = msg_db.get_conversation_history(conversation_id, limit=6)
        print(f"[DEBUG] Generating AI response...")
        
        ai_response = rag_service.generate_response(
            user_message=request.message,
            conversation_history=history[:-1],
            additional_instructions=conversation_service.get_state_instructions(state)
        )
        print(f"[DEBUG] AI response generated: {ai_response[:100]}...")
        
        msg_db.create_message(conversation_id, 'assistant', ai_response)
        conv_db.update_conversation_timestamp(conversation_id)
        
        should_capture = lead_capture_service.should_capture_lead(
            message_count + 1,
            intent_data,
            lead_already_captured
        )
        
        return ChatResponse(
            response=ai_response,
            session_id=request.session_id,
            should_capture_lead=should_capture and not lead_already_captured,
            lead_captured=lead_already_captured,
            conversation_state=state.value
        )
        
    except Exception as e:
        print(f"[ERROR] Chat endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
