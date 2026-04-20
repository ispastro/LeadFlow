from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.chat import ChatRequest, ChatResponse
from app.core.rag import rag_service
from app.core.lead_capture import lead_capture_service
from app.core.conversation import conversation_service, ConversationState
from app.db import conversations as conv_db
from app.db import messages as msg_db
from app.db import leads as leads_db
from app.utils.text_processing import extract_email, extract_name
from app.services.email_service import email_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """Main chat endpoint"""
    import time
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"📨 Chat request: {request.message[:50]}...")
        
        t1 = time.time()
        conversation = conv_db.get_or_create_conversation(request.session_id)
        conversation_id = conversation['id']
        print(f"✅ Conversation ID: {conversation_id} [{(time.time()-t1)*1000:.0f}ms]")
        
        # Batch database reads together
        t2 = time.time()
        lead_already_captured = leads_db.lead_exists(conversation_id)
        message_count = msg_db.count_user_messages(conversation_id)
        history = msg_db.get_conversation_history(conversation_id, limit=4)  # Reduced from 6 to 4
        print(f"✅ Batch DB reads (lead+count+history) [{(time.time()-t2)*1000:.0f}ms]")
        
        t3 = time.time()
        msg_db.create_message(conversation_id, 'user', request.message)
        print(f"✅ Message saved [{(time.time()-t3)*1000:.0f}ms]")
        
        # Quick intent detection without LLM (saves 740ms)
        t4 = time.time()
        email_in_message = extract_email(request.message)
        name_in_message = extract_name(request.message)
        
        # Simple rule-based intent (no LLM call)
        intent_keywords = ['price', 'pricing', 'cost', 'buy', 'purchase', 'demo', 'trial', 'contact', 'sales']
        has_high_intent = any(keyword in request.message.lower() for keyword in intent_keywords)
        
        intent_data = {
            'intent': 'HIGH_INTEREST' if has_high_intent else 'INFORMATION_SEEKING',
            'quality': 'MEDIUM',
            'reason': 'Fast detection'
        }
        print(f"✅ Intent detected (fast): {intent_data.get('intent')} [{(time.time()-t4)*1000:.0f}ms]")
        
        state = conversation_service.get_state(
            message_count,
            lead_already_captured,
            intent_data
        )
        
        email_in_message = email_in_message or extract_email(request.message)
        name_in_message = name_in_message or extract_name(request.message)
        
        if (email_in_message or request.user_email) and not lead_already_captured:
            email = email_in_message or request.user_email
            name = name_in_message or request.user_name
            
            lead_id = leads_db.create_lead(
                conversation_id=conversation_id,
                email=email,
                name=name,
                intent=intent_data.get('intent'),
                metadata={'quality': intent_data.get('quality')}
            )
            lead_already_captured = True
            state = ConversationState.CAPTURED
            
            # Send email notification in background
            background_tasks.add_task(
                email_service.send_lead_notification,
                lead_email=email,
                lead_name=name,
                intent=intent_data.get('intent'),
                quality=intent_data.get('quality'),
                conversation_id=conversation_id,
                lead_id=lead_id
            )
        
        t5 = time.time()
        ai_response = rag_service.generate_response(
            user_message=request.message,
            conversation_history=history[:-1],
            additional_instructions=conversation_service.get_state_instructions(state)
        )
        print(f"✅ AI response generated [{(time.time()-t5)*1000:.0f}ms]")
        
        t6 = time.time()
        msg_db.create_message(conversation_id, 'assistant', ai_response)
        conv_db.update_conversation_timestamp(conversation_id)
        print(f"✅ Response saved [{(time.time()-t6)*1000:.0f}ms]")
        
        should_capture = lead_capture_service.should_capture_lead(
            message_count + 1,
            intent_data,
            lead_already_captured
        )
        
        total_time = (time.time() - start_time) * 1000
        print(f"⏱️  TOTAL: {total_time:.0f}ms (DB: ~{(time.time()-start_time-(time.time()-t4)-(time.time()-t5))*1000:.0f}ms, LLM: ~{(time.time()-t4)+(time.time()-t5):.0f}ms)")
        print(f"{'='*60}\n")
        
        return ChatResponse(
            response=ai_response,
            session_id=request.session_id,
            should_capture_lead=should_capture and not lead_already_captured,
            lead_captured=lead_already_captured,
            conversation_state=state.value
        )
        
    except Exception as e:
        print(f"❌ ERROR in chat endpoint: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full traceback
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
