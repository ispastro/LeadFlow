'use client'

import { X } from 'lucide-react'
import type { Lead } from '@/types/dashboard'
import { GraphTrace } from './GraphTrace'
import { ActionPanel } from './ActionPanel'

interface LeadDetailDrawerProps {
  lead: Lead | null
  isOpen: boolean
  onClose: () => void
}

export function LeadDetailDrawer({ lead, isOpen, onClose }: LeadDetailDrawerProps) {
  if (!lead) return null

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 transition-opacity"
          onClick={onClose}
          role="presentation"
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed right-0 top-0 z-50 h-screen w-full max-w-md transform border-l border-border bg-background transition-transform duration-300 ease-in-out overflow-y-auto ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="sticky top-0 border-b border-border bg-background/95 backdrop-blur-sm px-6 py-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-foreground">{lead.name}</h2>
              <p className="text-sm text-muted-foreground">{lead.company}</p>
            </div>
            <button
              onClick={onClose}
              className="inline-flex h-8 w-8 items-center justify-center rounded-lg hover:bg-muted transition-colors"
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-8 px-6 py-6">
          {/* Lead Summary */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Summary</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">Score</p>
                <p className="mt-1 text-lg font-semibold text-foreground">{lead.qualificationScore}%</p>
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">Status</p>
                <p className="mt-1 text-sm font-medium text-foreground">{lead.status}</p>
              </div>
            </div>
          </div>

          {/* Enrichment Data */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Company Data</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between rounded-lg bg-muted/30 px-3 py-2">
                <span className="text-xs text-muted-foreground">Industry</span>
                <span className="text-sm font-medium text-foreground">{lead.enrichmentData.industry}</span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-muted/30 px-3 py-2">
                <span className="text-xs text-muted-foreground">Revenue</span>
                <span className="text-sm font-medium text-foreground">{lead.enrichmentData.revenue}</span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-muted/30 px-3 py-2">
                <span className="text-xs text-muted-foreground">Employees</span>
                <span className="text-sm font-medium text-foreground">{lead.enrichmentData.employees}</span>
              </div>
            </div>
          </div>

          {/* Graph Trace Timeline */}
          <GraphTrace steps={lead.timeline} />

          {/* Action Panel - Only show if Awaiting Approval */}
          {lead.status === 'Awaiting Approval' && <ActionPanel lead={lead} onClose={onClose} />}

          {/* Status Info for other states */}
          {lead.status === 'Drafting' && (
            <div className="rounded-lg bg-blue-500/10 p-4">
              <p className="text-sm text-blue-400">This lead is currently being drafted and is not ready for approval.</p>
            </div>
          )}
          {lead.status === 'Syncing' && (
            <div className="rounded-lg bg-purple-500/10 p-4">
              <p className="text-sm text-purple-400">This lead is currently being synced to your CRM.</p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
