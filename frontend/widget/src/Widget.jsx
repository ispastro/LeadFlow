import { useState, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import ChatBubble from './components/ChatBubble'

function Widget({ apiUrl = 'http://localhost:8000' }) {
  const [isOpen, setIsOpen] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`)

  useEffect(() => {
    const handleOpenChat = () => {
      setIsOpen(true)
      // Shift demo chat to left when modal opens
      const demoChat = document.getElementById('demo-chat-container')
      if (demoChat) {
        demoChat.style.transform = 'translateX(-200px)'
      }
    }
    
    const handleCloseChat = () => {
      // Reset demo chat position when modal closes
      const demoChat = document.getElementById('demo-chat-container')
      if (demoChat) {
        demoChat.style.transform = 'translateX(0)'
      }
    }
    
    window.addEventListener('leadflow-open-chat', handleOpenChat)
    
    // Also listen for direct close
    if (!isOpen) {
      handleCloseChat()
    }
    
    return () => window.removeEventListener('leadflow-open-chat', handleOpenChat)
  }, [isOpen])

  return (
    <div className="fixed bottom-5 right-5 z-[9999] font-sans">
      {isOpen && (
        <ChatWindow 
          apiUrl={apiUrl}
          sessionId={sessionId}
          onClose={() => setIsOpen(false)}
        />
      )}
      <ChatBubble 
        isOpen={isOpen}
        onClick={() => setIsOpen(!isOpen)}
      />
    </div>
  )
}

export default Widget