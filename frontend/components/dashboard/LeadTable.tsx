'use client'

import { ChevronRight } from 'lucide-react'
import type { Lead } from '@/types/dashboard'
import { QualificationBadge } from './QualificationBadge'
import { StatusBadge } from './StatusBadge'

interface LeadTableProps {
  leads: Lead[]
  onSelectLead: (lead: Lead) => void
}

export function LeadTable({ leads, onSelectLead }: LeadTableProps) {
  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      {/* Table Header */}
      <div className="grid grid-cols-[2fr_1.5fr_1.2fr_1.2fr_auto] gap-4 border-b border-border bg-muted/30 px-6 py-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Lead Name</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Company</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Score</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Status</div>
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Action</div>
      </div>

      {/* Table Body */}
      <div className="divide-y divide-border">
        {leads.map((lead) => (
          <div
            key={lead.id}
            className="grid grid-cols-[2fr_1.5fr_1.2fr_1.2fr_auto] gap-4 px-6 py-4 transition-colors hover:bg-muted/30"
          >
            {/* Lead Name */}
            <div className="flex flex-col justify-center">
              <p className="text-sm font-medium text-foreground">{lead.name}</p>
              <p className="text-xs text-muted-foreground">{lead.enrichmentData.industry}</p>
            </div>

            {/* Company */}
            <div className="flex flex-col justify-center">
              <p className="text-sm text-foreground">{lead.company}</p>
            </div>

            {/* Score Badge */}
            <div className="flex items-center">
              <QualificationBadge score={lead.qualificationScore} />
            </div>

            {/* Status Badge */}
            <div className="flex items-center">
              <StatusBadge status={lead.status} />
            </div>

            {/* Details Button */}
            <div className="flex items-center justify-end">
              <button
                onClick={() => onSelectLead(lead)}
                className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                aria-label={`View details for ${lead.name}`}
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {leads.length === 0 && (
        <div className="flex h-32 items-center justify-center">
          <p className="text-sm text-muted-foreground">No leads found</p>
        </div>
      )}
    </div>
  )
}
