import { useState, useEffect, useRef } from 'react'

function ChatWindow({ apiUrl, sessionId, onClose }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    setMessages([{
      role: 'assistant',
      content: 'Hi! How can I help you today?',
      timestamp: new Date()
    }])
  }, [])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    }])

    setLoading(true)

    try {
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        })
      })

      const data = await response.json()
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="-mb-16 w-[400px] h-[600px] bg-black rounded-xl border border-neutral-800 flex flex-col relative">

      {/* Background effects layer */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl" style={{ zIndex: 0 }}>
        {/* Radial gradients */}
        <div className="absolute top-0 left-0 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-0 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl"></div>
        {/* Grid pattern overlay */}
        <div className="absolute inset-0 grid-pattern opacity-30"></div>
      </div>
      
      {/* Header */}
      <div className="bg-neutral-900 border-b border-neutral-800 px-5 py-4 flex items-center justify-between relative rounded-t-xl" style={{ zIndex: 20 }}>
        <div className="flex items-center gap-3">
          <img src="/leadflow.png" alt="LeadFlow" className="w-8 h-8 rounded-md flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-sm text-white leading-tight" style={{ fontFamily: 'Poppins, sans-serif' }}>
              <span className="font-medium">Lead</span>
              <span className="font-semibold" style={{ letterSpacing: '-0.02em' }}>Flow</span>
            </h3>
            <p className="text-xs text-neutral-400 leading-tight mt-0.5">Your AI Agent</p>
          </div>
        </div>
        <button onClick={onClose} className="text-neutral-400 hover:text-white transition-colors flex-shrink-0">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-6 space-y-4 relative" style={{ zIndex: 10 }}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
            <div className={`max-w-[85%] rounded-xl px-4 py-3 ${
              msg.role === 'user' 
                ? 'bg-white text-black font-medium' 
                : 'bg-neutral-900/80 backdrop-blur-sm text-white border border-neutral-800'
            }`}>
              <p className="text-sm leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start animate-in fade-in duration-300">
            <div className="bg-neutral-900/80 backdrop-blur-sm border border-neutral-800 rounded-xl px-4 py-3">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="p-4 bg-neutral-900/80 backdrop-blur-sm border-t border-neutral-800 relative rounded-b-xl" style={{ zIndex: 20 }}>
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2.5 bg-black border border-neutral-800 rounded-lg focus:outline-none focus:ring-1 focus:ring-neutral-600 focus:border-neutral-600 text-sm text-white placeholder-neutral-500 transition-all"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-2.5 bg-white hover:bg-neutral-100 disabled:bg-neutral-800 disabled:text-neutral-500 text-black rounded-lg transition-all font-medium text-sm disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatWindow
