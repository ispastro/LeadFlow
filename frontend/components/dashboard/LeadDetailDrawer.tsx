'use client'

import { X } from 'lucide-react'
import type { Lead } from '@/lib/api'
import { deriveLeadStatus, deriveTraceSteps } from '@/types/dashboard'
import { useGraphState } from '@/lib/queries'
import { GraphTrace } from './GraphTrace'
import { ActionPanel } from './ActionPanel'
import { StatusBadge } from './StatusBadge'
import { QualificationBadge } from './QualificationBadge'

interface LeadDetailDrawerProps {
  lead: Lead | null
  isOpen: boolean
  onClose: () => void
}

export function LeadDetailDrawer({ lead, isOpen, onClose }: LeadDetailDrawerProps) {
  const { data: graphState } = useGraphState(lead?.conversation_id ?? null)
  const status = lead ? deriveLeadStatus(lead.metadata) : null
  const traceSteps = deriveTraceSteps(graphState?.current_node)

  if (!lead) return null

  const enrichment = graphState?.enrichment ?? {
    company_name: lead.metadata?.company_name,
    company_size: lead.metadata?.company_size,
    company_industry: lead.metadata?.company_industry,
    lead_role: lead.metadata?.lead_role,
  }

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 transition-opacity"
          onClick={onClose}
          role="presentation"
        />
      )}

      <div
        className={`fixed right-0 top-0 z-50 h-screen w-full max-w-md transform border-l border-border bg-background transition-transform duration-300 ease-in-out overflow-y-auto ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="sticky top-0 border-b border-border bg-background/95 backdrop-blur-sm px-6 py-4">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <h2 className="text-lg font-semibold text-foreground truncate">
                {lead.name ?? 'Anonymous'}
              </h2>
              <p className="text-sm text-muted-foreground truncate">{lead.email}</p>
            </div>
            <button
              onClick={onClose}
              className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg hover:bg-muted transition-colors"
              aria-label="Close drawer"
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>
        </div>

        <div className="space-y-8 px-6 py-6">
          {/* Summary */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Summary</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground mb-1">Score</p>
                <QualificationBadge score={lead.metadata?.qualification_score} />
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground mb-1">Status</p>
                {status && <StatusBadge status={status} />}
              </div>
            </div>
            {graphState?.qualification_reasoning && (
              <p className="text-xs text-muted-foreground bg-muted/30 rounded-lg p-3">
                {graphState.qualification_reasoning}
              </p>
            )}
          </div>

          {/* Enrichment */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Company Data</h3>
            <div className="space-y-2">
              {[
                ['Company',  enrichment.company_name],
                ['Industry', enrichment.company_industry],
                ['Size',     enrichment.company_size],
                ['Role',     enrichment.lead_role],
              ].map(([label, value]) =>
                value ? (
                  <div key={label} className="flex items-center justify-between rounded-lg bg-muted/30 px-3 py-2">
                    <span className="text-xs text-muted-foreground">{label}</span>
                    <span className="text-sm font-medium text-foreground">{value}</span>
                  </div>
                ) : null,
              )}
            </div>
          </div>

          {/* Graph trace */}
          <GraphTrace steps={traceSteps} currentNode={graphState?.current_node} />

          {/* HITL action panel */}
          {status === 'Awaiting Approval' && (
            <ActionPanel lead={lead} onClose={onClose} />
          )}

          {status === 'Drafting' && (
            <div className="rounded-lg bg-blue-500/10 p-4">
              <p className="text-sm text-blue-400">This lead is still being processed through the pipeline.</p>
            </div>
          )}
          {status === 'Syncing' && (
            <div className="rounded-lg bg-purple-500/10 p-4">
              <p className="text-sm text-purple-400">Lead approved — syncing to CRM.</p>
            </div>
          )}
          {status === 'Manual Review' && (
            <div className="rounded-lg bg-yellow-500/10 p-4">
              <p className="text-sm text-yellow-400">Routed to manual review. Check LangSmith for the error trace.</p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
