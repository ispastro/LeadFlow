import { useState, useEffect } from 'react'
import StreamingText from './StreamingText'

function DemoChat() {
  const [messages, setMessages] = useState([])
  const [isTyping, setIsTyping] = useState(false)
  const [searchingText, setSearchingText] = useState('')
  const [leadsCount, setLeadsCount] = useState(3)
  const [animatingMessageIndex, setAnimatingMessageIndex] = useState(null)

  // Simulate live activity
  useEffect(() => {
    const interval = setInterval(() => {
      setLeadsCount(prev => prev + 1)
    }, 120000) // Every 2 minutes
    return () => clearInterval(interval)
  }, [])

  // Pre-loaded realistic conversation
  useEffect(() => {
    const preloadedConversation = [
      {
        role: 'user',
        content: "Do you integrate with HubSpot?",
        timestamp: new Date(Date.now() - 180000)
      },
      {
        role: 'assistant',
        content: "Yes! LeadFlow integrates seamlessly with HubSpot. Leads sync automatically to your CRM in real-time with full conversation history and intent scores.",
        timestamp: new Date(Date.now() - 175000),
        searchText: "Checking integrations..."
      },
      {
        role: 'user',
        content: "What's the pricing? Sounds expensive.",
        timestamp: new Date(Date.now() - 120000)
      },
      {
        role: 'assistant',
        content: "Professional plan is $149/month for 10K conversations. That's $0.015 per conversation — 95% cheaper than paid ads. Plus it works 24/7, so you never miss a lead.",
        timestamp: new Date(Date.now() - 115000),
        searchText: "Searching pricing..."
      }
    ]

    // Animate messages in sequence
    let currentIndex = 0
    const animateNextMessage = () => {
      if (currentIndex >= preloadedConversation.length) return

      const msg = preloadedConversation[currentIndex]
      
      if (msg.role === 'assistant') {
        // Show searching text
        if (msg.searchText) {
          setSearchingText(msg.searchText)
          setTimeout(() => setSearchingText(''), 500)
        }
        
        // Show typing indicator
        setIsTyping(true)
        setTimeout(() => {
          setIsTyping(false)
          setMessages(prev => [...prev, msg])
          setAnimatingMessageIndex(currentIndex)
          
          // Clear animation after streaming completes
          setTimeout(() => {
            setAnimatingMessageIndex(null)
            currentIndex++
            setTimeout(animateNextMessage, 300)
          }, msg.content.length * 15)
        }, 700)
      } else {
        setMessages(prev => [...prev, msg])
        currentIndex++
        setTimeout(animateNextMessage, 300)
      }
    }

    setTimeout(animateNextMessage, 1000)
  }, [])

  return (
    <div className="w-full max-w-lg mx-auto bg-black rounded-2xl border border-neutral-800 overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="bg-neutral-900 border-b border-neutral-800 px-5 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img src="/leadflow.png" alt="LeadFlow" className="w-8 h-8 rounded-lg" />
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-sm text-white">
                LeadFlow AI
              </h3>
              {/* Live badge */}
              <div className="flex items-center gap-1.5 px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                <span className="text-[10px] font-medium text-emerald-400">Live</span>
              </div>
            </div>
            <p className="text-[11px] text-neutral-400 mt-1">
              {leadsCount} leads in last hour
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="h-[420px] overflow-y-auto px-5 py-5 space-y-4 bg-gradient-to-b from-black via-black to-neutral-950 scrollbar-hide">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
            <div className="flex flex-col gap-1.5 max-w-[80%]">
              {/* Search indicator */}
              {msg.role === 'assistant' && msg.searchText && animatingMessageIndex === idx && (
                <div className="text-xs text-neutral-500 italic ml-1 flex items-center gap-1.5 animate-in fade-in duration-200">
                  <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {msg.searchText}
                </div>
              )}
              
              <div className={`rounded-2xl px-4 py-3 ${
                msg.role === 'user' 
                  ? 'bg-white text-black font-medium shadow-lg' 
                  : 'bg-neutral-900/90 backdrop-blur-sm text-white border border-neutral-800/80'
              }`}>
                <p className="text-sm leading-relaxed">
                  {msg.role === 'assistant' && animatingMessageIndex === idx ? (
                    <StreamingText text={msg.content} isAnimating={true} speed={20} />
                  ) : (
                    msg.content
                  )}
                </p>
              </div>
            </div>
          </div>
        ))}
        
        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start animate-in fade-in duration-300">
            <div className="bg-neutral-900/90 backdrop-blur-sm border border-neutral-800/80 rounded-2xl px-4 py-3">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-neutral-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-neutral-800 p-4 bg-neutral-900/80">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Ask me anything about LeadFlow..."
            className="flex-1 px-4 py-2.5 bg-black border border-neutral-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-neutral-600 text-sm text-white placeholder-neutral-500 transition-all"
            disabled
          />
          <button
            disabled
            className="px-4 py-2.5 bg-neutral-800 text-neutral-500 rounded-xl text-sm flex items-center justify-center cursor-not-allowed"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default DemoChat
