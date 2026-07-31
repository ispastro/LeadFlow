'use client'

import { useState } from 'react'
import { Check, X, Loader2 } from 'lucide-react'
import type { Lead } from '@/lib/api'
import { useApproveLead } from '@/lib/queries'

interface ActionPanelProps {
  lead: Lead
  onClose: () => void
}

export function ActionPanel({ lead, onClose }: ActionPanelProps) {
  const [notes, setNotes] = useState('')
  const { mutate: approve, isPending, error } = useApproveLead()

  const handleDecision = (approved: boolean) => {
    // The backend approve endpoint uses session_id = conversation_id
    approve(
      {
        sessionId: lead.conversation_id,
        payload: { approved, notes: notes || undefined },
      },
      { onSuccess: () => onClose() },
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-foreground">Action Required</h3>

      <div className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Qualification Summary
        </p>
        <div className="rounded-lg border border-border bg-muted/30 p-4 space-y-1 text-sm">
          <p><span className="text-muted-foreground">Score:</span> <span className="font-medium text-foreground">{lead.metadata?.qualification_score ?? '—'}/100</span></p>
          <p><span className="text-muted-foreground">Tier:</span> <span className="font-medium text-foreground capitalize">{lead.metadata?.qualification_tier ?? '—'}</span></p>
          {lead.metadata?.intent_signals?.length ? (
            <div className="flex flex-wrap gap-1 pt-1">
              {lead.metadata.intent_signals.map((s) => (
                <span key={s} className="px-1.5 py-0.5 text-xs bg-muted text-muted-foreground rounded border border-border">
                  {s.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      </div>

      {/* Reviewer notes */}
      <div className="space-y-2">
        <label htmlFor="reviewer-notes" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Notes <span className="normal-case">(optional)</span>
        </label>
        <textarea
          id="reviewer-notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          placeholder="Add context for the team..."
          className="w-full rounded-lg border border-border bg-muted/30 px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring resize-none"
        />
      </div>

      {error && (
        <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
          {(error as Error).message}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 pt-2">
        <button
          onClick={() => handleDecision(false)}
          disabled={isPending}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-destructive/20 px-4 py-2.5 text-sm font-medium text-destructive transition-colors hover:bg-destructive/30 disabled:opacity-50"
        >
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <X className="h-4 w-4" />}
          Reject
        </button>
        <button
          onClick={() => handleDecision(true)}
          disabled={isPending}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-green-500/20 px-4 py-2.5 text-sm font-medium text-green-400 transition-colors hover:bg-green-500/30 disabled:opacity-50"
        >
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
          Approve
        </button>
      </div>
    </div>
  )
}
