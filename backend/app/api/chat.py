from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.chat import ChatRequest, ChatResponse
from app.core.rag import rag_service
from app.core.state_machine import state_machine, ConversationStage
from app.db import conversations as conv_db
from app.db import messages as msg_db
from app.db import leads as leads_db
from app.utils.text_processing import extract_name
from app.services.email_service import email_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """State machine driven chat endpoint"""
    import time
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"📨 Message: {request.message[:50]}...")
        
        # 1. Load conversation state
        conversation = conv_db.get_or_create_conversation(request.session_id)
        conversation_id = conversation['id']
        current_stage = ConversationStage(conversation['stage'])
        email_captured = conversation['email_captured']
        
        print(f"📊 Stage: {current_stage.value} | Email: {email_captured}")
        
        # 2. Get conversation history
        history = msg_db.get_conversation_history(conversation_id, limit=4)
        message_count = msg_db.count_user_messages(conversation_id)
        
        # 3. Save user message
        msg_db.create_message(conversation_id, 'user', request.message)
        
        # 4. State transition logic
        new_stage, extracted_email = state_machine.transition(
            current_stage=current_stage,
            message=request.message,
            email_captured=email_captured,
            message_count=message_count
        )
        
        print(f"🔄 Transition: {current_stage.value} → {new_stage.value}")
        
        # 5. Handle email capture
        if extracted_email and not email_captured:
            name = extract_name(request.message)
            
            # Determine intent trigger by analyzing conversation history
            intent_trigger = 'other'
            all_messages = msg_db.get_conversation_history(conversation_id, limit=10)
            
            # Check what topics were discussed
            conversation_text = ' '.join([m['content'].lower() for m in all_messages])
            
            if any(word in conversation_text for word in ['price', 'pricing', 'cost', 'plan', 'subscription', 'pay']):
                intent_trigger = 'pricing'
            elif any(word in conversation_text for word in ['demo', 'trial', 'test', 'try']):
                intent_trigger = 'demo'
            elif any(word in conversation_text for word in ['integrate', 'integration', 'api', 'connect', 'hubspot', 'salesforce']):
                intent_trigger = 'integration'
            elif new_stage == ConversationStage.DISCOVERY:
                intent_trigger = 'unprompted'
            
            lead_id = leads_db.create_lead(
                conversation_id=conversation_id,
                email=extracted_email,
                name=name,
                intent=intent_trigger,
                metadata={'stage': new_stage.value}
            )
            
            email_captured = True
            new_stage = ConversationStage.CAPTURED
            
            # Background email notification
            background_tasks.add_task(
                email_service.send_lead_notification,
                lead_email=extracted_email,
                lead_name=name,
                intent=intent_trigger,
                quality='MEDIUM',
                conversation_id=conversation_id,
                lead_id=lead_id
            )
            
            print(f"✅ Lead captured: {extracted_email}")
        
        # 6. Update conversation stage
        conv_db.update_conversation_stage(
            conversation_id, 
            new_stage.value, 
            email_captured
        )
        
        # 7. Generate RAG response
        system_instructions = state_machine.get_system_instructions(new_stage)
        
        t_rag = time.time()
        ai_response = rag_service.generate_response(
            user_message=request.message,
            conversation_history=history[:-1],
            additional_instructions=system_instructions
        )
        print(f"✅ RAG response [{(time.time()-t_rag)*1000:.0f}ms]")
        
        # 8. Append email ask if needed
        if state_machine.should_append_email_ask(new_stage) and not email_captured:
            ai_response += state_machine.get_email_ask_text()
        
        # 9. Handle CAPTURED confirmation
        if new_stage == ConversationStage.CAPTURED:
            ai_response = state_machine.get_capture_confirmation(extracted_email)
        
        # 10. Save AI message
        msg_db.create_message(conversation_id, 'assistant', ai_response)
        conv_db.update_conversation_timestamp(conversation_id)
        
        total_time = (time.time() - start_time) * 1000
        print(f"⏱️  TOTAL: {total_time:.0f}ms")
        print(f"{'='*60}\n")
        
        return ChatResponse(
            response=ai_response,
            session_id=request.session_id,
            should_capture_lead=new_stage == ConversationStage.EMAIL_REQUESTED,
            lead_captured=email_captured,
            conversation_state=new_stage.value
        )
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
