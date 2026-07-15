'use client'

import { useState } from 'react'
import { Check, X } from 'lucide-react'
import type { Lead } from '@/types/dashboard'
import { approveLead, rejectLead } from '@/lib/dashboard-api'

interface ActionPanelProps {
  lead: Lead
  onClose: () => void
}

export function ActionPanel({ lead, onClose }: ActionPanelProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleApprove = async () => {
    try {
      setIsLoading(true)
      setError(null)
      await approveLead(lead.id)
      console.log(`[v0] Lead ${lead.id} approved successfully`)
      onClose()
    } catch (err) {
      setError('Failed to approve lead')
      console.error('[v0] Error approving lead:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReject = async () => {
    try {
      setIsLoading(true)
      setError(null)
      await rejectLead(lead.id, 'Rejected by supervisor')
      console.log(`[v0] Lead ${lead.id} rejected successfully`)
      onClose()
    } catch (err) {
      setError('Failed to reject lead')
      console.error('[v0] Error rejecting lead:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-foreground">Action Panel</h3>

      {/* AI-Drafted Email */}
      <div className="space-y-2">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">AI-Drafted Email</p>
        <div className="rounded-lg border border-border bg-muted/30 p-4">
          <div className="space-y-2 text-sm text-foreground/80">
            <p className="font-mono text-xs text-muted-foreground">{lead.draftEmail}</p>
          </div>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-3 pt-2">
        <button
          onClick={handleReject}
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-destructive/20 px-4 py-2.5 text-sm font-medium text-destructive transition-colors hover:bg-destructive/30 disabled:opacity-50"
        >
          <X className="h-4 w-4" />
          <span>Reject Lead</span>
        </button>
        <button
          onClick={handleApprove}
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-green-500/20 px-4 py-2.5 text-sm font-medium text-green-400 transition-colors hover:bg-green-500/30 disabled:opacity-50"
        >
          <Check className="h-4 w-4" />
          <span>Approve & Sync</span>
        </button>
      </div>

      {isLoading && (
        <p className="text-xs text-muted-foreground">Processing...</p>
      )}
    </div>
  )
}
