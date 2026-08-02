'use client'

import { useState } from 'react'
import { useConversations, useConversation } from '@/lib/queries'
import type { Conversation } from '@/lib/api'
import { MessageSquare, User, Bot, ChevronRight, X, Tag } from 'lucide-react'
import { relativeTime } from '@/types/dashboard'

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
              <div className="h-10 w-10 rounded-full bg-muted animate-pulse shrink-0" />
              <div className="flex-1 space-y-2 py-1">
                <div className="h-4 w-48 rounded bg-muted animate-pulse" />
                <div className="h-3 w-32 rounded bg-muted animate-pulse" />
              </div>
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

      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        {/* ── List ───────────────────────────────────────── */}
        <div className="rounded-lg border border-border bg-card overflow-hidden self-start">
          {conversations.length === 0 ? (
            <div className="px-6 py-12 text-center text-sm text-muted-foreground">
              No conversations yet
            </div>
          ) : (
            <div className="divide-y divide-border">
              {conversations.map((conv) => (
                <ConversationRow
                  key={conv.id}
                  conversation={conv}
                  isSelected={selectedId === conv.id}
                  onClick={() => setSelectedId(conv.id === selectedId ? null : conv.id)}
                />
              ))}
            </div>
          )}
        </div>

        {/* ── Detail ─────────────────────────────────────── */}
        <div className="rounded-lg border border-border bg-card overflow-hidden min-h-[500px]">
          {selected ? (
            <ConversationDetail
              id={selected.id}
              conversation={selected}
              onClose={() => setSelectedId(null)}
            />
          ) : (
            <div className="flex h-full min-h-[500px] flex-col items-center justify-center gap-2 text-muted-foreground">
              <MessageSquare className="h-8 w-8 opacity-30" />
              <p className="text-sm">Select a conversation to view messages</p>
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
  const hasLead = Boolean(conversation.email)
  const displayName = conversation.name ?? conversation.email ?? 'Anonymous'
  const updatedAt = conversation.updated_at ? relativeTime(conversation.updated_at) : null

  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-center gap-3 px-4 py-3 text-left transition-colors ${
        isSelected ? 'bg-primary/5 ring-1 ring-inset ring-primary/20' : 'hover:bg-muted/30'
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${
          hasLead ? 'bg-primary/15' : 'bg-muted'
        }`}
      >
        <MessageSquare
          className={`h-4 w-4 ${hasLead ? 'text-primary' : 'text-muted-foreground'}`}
        />
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <span className="truncate text-sm font-medium text-foreground">{displayName}</span>
          {updatedAt && (
            <span className="shrink-0 text-[10px] text-muted-foreground">{updatedAt}</span>
          )}
        </div>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="truncate text-xs text-muted-foreground">
            {conversation.message_count} message{conversation.message_count !== 1 ? 's' : ''}
          </span>
          {hasLead && (
            <span className="inline-flex items-center gap-1 rounded-full bg-green-500/15 px-1.5 py-0.5 text-[10px] font-medium text-green-400 shrink-0">
              <Tag className="h-2.5 w-2.5" />
              Lead
            </span>
          )}
        </div>
      </div>

      <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground/50" />
    </button>
  )
}

// ---------------------------------------------------------------------------
// Conversation detail (messages + lead info)
// ---------------------------------------------------------------------------

function ConversationDetail({
  id,
  conversation,
  onClose,
}: {
  id: string
  conversation: Conversation
  onClose: () => void
}) {
  const { data, isPending, error } = useConversation(id)

  if (isPending) {
    return (
      <div className="flex h-full min-h-[500px] items-center justify-center">
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

  const { messages } = data
  const hasLead = Boolean(conversation.email)

  return (
    <div className="flex h-full min-h-[500px] flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-foreground truncate">
              {conversation.name ?? conversation.email ?? 'Anonymous'}
            </span>
            {hasLead && (
              <a
                href="/dashboard/leads"
                className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary hover:bg-primary/20 transition-colors shrink-0"
                title="View in Leads"
              >
                <Tag className="h-3 w-3" />
                View Lead
              </a>
            )}
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-xs text-muted-foreground">
              {new Date(conversation.created_at).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </span>
            <span className="text-muted-foreground/40">·</span>
            <span className="text-xs text-muted-foreground">
              {messages.length} message{messages.length !== 1 ? 's' : ''}
            </span>
            {conversation.email && (
              <>
                <span className="text-muted-foreground/40">·</span>
                <span className="text-xs text-muted-foreground truncate">{conversation.email}</span>
              </>
            )}
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground ml-3 shrink-0"
          aria-label="Close conversation"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg, i) => {
          const isUser = msg.role === 'user'
          return (
            <div key={msg.id ?? `msg-${i}`} className={`flex gap-2.5 ${isUser ? '' : 'flex-row-reverse'}`}>
              <div
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
                  isUser ? 'bg-primary/10' : 'bg-muted'
                }`}
              >
                {isUser ? (
                  <User className="h-3.5 w-3.5 text-primary" />
                ) : (
                  <Bot className="h-3.5 w-3.5 text-muted-foreground" />
                )}
              </div>
              <div
                className={`max-w-[75%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed ${
                  isUser
                    ? 'bg-primary/10 text-foreground rounded-tl-sm'
                    : 'bg-muted text-foreground rounded-tr-sm'
                }`}
              >
                {msg.content}
                <div className="mt-1.5 text-[10px] text-muted-foreground">
                  {new Date(msg.created_at).toLocaleTimeString(undefined, {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            </div>
          )
        })}
        {messages.length === 0 && (
          <p className="text-center text-sm text-muted-foreground py-8">No messages</p>
        )}
      </div>
    </div>
  )
}
