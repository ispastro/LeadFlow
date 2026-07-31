'use client'

import { ChevronRight } from 'lucide-react'
import type { Lead } from '@/lib/api'
import { QualificationBadge } from './QualificationBadge'
import { StatusBadge } from './StatusBadge'
import { deriveLeadStatus } from '@/types/dashboard'

interface LeadTableProps {
  leads: Lead[]
  onSelectLead: (lead: Lead) => void
}

export function LeadTable({ leads, onSelectLead }: LeadTableProps) {
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="grid grid-cols-[2fr_1.5fr_1.2fr_1.2fr_auto] gap-4 border-b border-border bg-muted/30 px-6 py-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Lead</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Company</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Score</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Status</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground" />
      </div>

      <div className="divide-y divide-border">
        {leads.map((lead) => {
          const status = deriveLeadStatus(lead.metadata)
          const score = lead.metadata?.qualification_score

          return (
            <div
              key={lead.id}
              className="grid grid-cols-[2fr_1.5fr_1.2fr_1.2fr_auto] gap-4 px-6 py-4 transition-colors hover:bg-muted/30"
            >
              <div className="flex flex-col justify-center min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  {lead.name ?? 'Anonymous'}
                </p>
                <p className="text-xs text-muted-foreground truncate">{lead.email}</p>
              </div>

              <div className="flex flex-col justify-center min-w-0">
                <p className="text-sm text-foreground truncate">
                  {lead.metadata?.company_name ?? '—'}
                </p>
                {lead.metadata?.company_industry && (
                  <p className="text-xs text-muted-foreground truncate">
                    {lead.metadata.company_industry}
                  </p>
                )}
              </div>

              <div className="flex items-center">
                <QualificationBadge score={score} />
              </div>

              <div className="flex items-center">
                <StatusBadge status={status} />
              </div>

              <div className="flex items-center justify-end">
                <button
                  onClick={() => onSelectLead(lead)}
                  className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                  aria-label={`View details for ${lead.name ?? lead.email}`}
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {leads.length === 0 && (
        <div className="flex h-32 items-center justify-center">
          <p className="text-sm text-muted-foreground">No leads yet</p>
        </div>
      )}
    </div>
  )
}
