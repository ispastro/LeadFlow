'use client'

import { useState } from 'react'
import { useConversations, useConversation } from '@/lib/queries'
import type { Conversation } from '@/lib/api'
import { MessageSquare, User, Bot, ChevronRight, X } from 'lucide-react'

export default function ConversationsPage() {
  const { data, isPending, error } = useConversations()
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const conversations = data?.conversations ?? []
  const selected = selectedId
    ? conversations.find((c) => c.id === selectedId) ?? null
    : null

  if (isPending) {
    return (
      <div className="space-y-6 px-6 py-6">
        <div className="h-7 w-56 rounded-md bg-muted animate-pulse" />
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex gap-4 px-6 py-4 border-b border-border last:border-0">
              <div className="h-4 w-48 rounded bg-muted animate-pulse" />
              <div className="h-4 w-24 rounded bg-muted animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-6 py-6">
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          Failed to load conversations: {(error as Error).message}
        </div>
      </div>
    )
  }

  return (
    <div className="px-6 py-6">
      <div className="space-y-1 mb-6">
        <h1 className="text-2xl font-bold text-foreground">Conversations</h1>
        <p className="text-sm text-muted-foreground">
          {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.5fr]">
        {/* List */}
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          {conversations.length === 0 ? (
            <div className="px-6 py-12 text-center text-sm text-muted-foreground">
              No conversations yet
            </div>
          ) : (
            conversations.map((conv) => (
              <ConversationRow
                key={conv.id}
                conversation={conv}
                isSelected={selectedId === conv.id}
                onClick={() => setSelectedId(conv.id === selectedId ? null : conv.id)}
              />
            ))
          )}
        </div>

        {/* Detail */}
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          {selected ? (
            <ConversationDetail id={selected} onClose={() => setSelectedId(null)} />
          ) : (
            <div className="flex h-full min-h-[400px] items-center justify-center text-sm text-muted-foreground">
              Select a conversation to view messages
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Conversation row
// ---------------------------------------------------------------------------

function ConversationRow({
  conversation,
  isSelected,
  onClick,
}: {
  conversation: Conversation
  isSelected: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-center gap-3 border-b border-border px-4 py-3 text-left transition-colors last:border-0 ${
        isSelected ? 'bg-primary/5' : 'hover:bg-muted/30'
      }`}
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted">
        <MessageSquare className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="truncate text-sm font-medium text-foreground">
          {conversation.name ?? conversation.email ?? 'Anonymous'}
        </div>
        <div className="truncate text-xs text-muted-foreground">
          {conversation.session_id} · {conversation.message_count} messages
        </div>
      </div>
      <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
    </button>
  )
}

// ---------------------------------------------------------------------------
// Conversation detail (messages)
// ---------------------------------------------------------------------------

function ConversationDetail({ id, onClose }: { id: string; onClose: () => void }) {
  const { data, isPending, error } = useConversation(id)

  if (isPending) {
    return (
      <div className="flex h-full min-h-[400px] items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-muted-foreground/30 border-t-foreground" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="p-4">
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          Failed to load messages: {(error as Error)?.message ?? 'Unknown error'}
        </div>
      </div>
    )
  }

  const { conversation, messages } = data

  return (
    <div className="flex h-full min-h-[400px] flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="min-w-0">
          <div className="truncate text-sm font-medium text-foreground">
            {conversation.name ?? conversation.email ?? 'Anonymous'}
          </div>
          <div className="text-xs text-muted-foreground">
            {new Date(conversation.created_at).toLocaleDateString()} · {conversation.message_count} messages
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-2 ${msg.role === 'user' ? '' : 'flex-row-reverse'}`}
          >
            <div
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
                msg.role === 'user' ? 'bg-primary/10' : 'bg-muted'
              }`}
            >
              {msg.role === 'user' ? (
                <User className="h-3.5 w-3.5 text-primary" />
              ) : (
                <Bot className="h-3.5 w-3.5 text-muted-foreground" />
              )}
            </div>
            <div
              className={`max-w-[75%] rounded-lg px-3 py-2 text-sm ${
                msg.role === 'user'
                  ? 'bg-primary/10 text-foreground'
                  : 'bg-muted text-foreground'
              }`}
            >
              {msg.content}
              <div className="mt-1 text-[10px] text-muted-foreground">
                {new Date(msg.created_at).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {messages.length === 0 && (
          <p className="text-center text-sm text-muted-foreground">No messages</p>
        )}
      </div>
    </div>
  )
}
