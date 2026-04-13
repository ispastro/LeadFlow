import { useState, useEffect } from 'react'
import { api } from '../services/api'
import { useSearchParams } from 'react-router-dom'

function Conversations() {
  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchParams, setSearchParams] = useSearchParams()

  useEffect(() => {
    loadConversations()
  }, [])

  useEffect(() => {
    const convId = searchParams.get('id')
    if (convId) {
      loadConversation(convId)
    }
  }, [searchParams])

  const loadConversations = async () => {
    try {
      const data = await api.getConversations()
      setConversations(data.conversations || [])
    } catch (error) {
      console.error('Failed to load conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadConversation = async (id) => {
    try {
      const data = await api.getConversation(id)
      setSelectedConversation(data)
    } catch (error) {
      console.error('Failed to load conversation:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleConversationClick = (conv) => {
    setSearchParams({ id: conv.id })
  }

  const handleBack = () => {
    setSearchParams({})
    setSelectedConversation(null)
  }

  if (loading) {
    return (
      <div className="max-w-6xl">
        <div className="h-8 w-48 bg-neutral-800 rounded skeleton mb-8"></div>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="bg-neutral-900 border border-neutral-800 rounded-lg p-4">
              <div className="h-4 w-32 bg-neutral-800 rounded skeleton mb-2"></div>
              <div className="h-3 w-48 bg-neutral-800 rounded skeleton"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Detail View
  if (selectedConversation) {
    return (
      <div className="max-w-4xl">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-sm text-neutral-400 hover:text-white mb-6 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to conversations
        </button>

        <div className="mb-6">
          <h1 className="text-2xl font-semibold mb-1 text-white">Conversation</h1>
          <p className="text-sm text-neutral-400">
            {selectedConversation.conversation.session_id}
          </p>
        </div>

        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
          <div className="space-y-4">
            {selectedConversation.messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-white text-black'
                    : 'bg-neutral-800 text-white border border-neutral-700'
                }`}>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // List View
  return (
    <div className="max-w-6xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold mb-1 text-white">Conversations</h1>
        <p className="text-sm text-neutral-400">{conversations.length} total conversations</p>
      </div>

      {conversations.length === 0 ? (
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-12 text-center">
          <p className="text-sm text-neutral-400">No conversations yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => handleConversationClick(conv)}
              className="w-full bg-neutral-900 border border-neutral-800 rounded-lg p-4 hover:border-neutral-700 transition-colors text-left"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white mb-1">
                    {conv.name || conv.email || 'Anonymous'}
                  </p>
                  <p className="text-xs text-neutral-500">
                    {conv.message_count} messages • {formatDate(conv.updated_at)}
                  </p>
                </div>
                <svg className="w-5 h-5 text-neutral-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default Conversations
