import { useState, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import ChatBubble from './components/ChatBubble'

function Widget({ apiUrl = 'http://localhost:8000' }) {
  const [isOpen, setIsOpen] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`)

  // Listen for open chat event
  useEffect(() => {
    const handleOpenChat = () => setIsOpen(true)
    window.addEventListener('leadflow-open-chat', handleOpenChat)
    return () => window.removeEventListener('leadflow-open-chat', handleOpenChat)
  }, [])

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