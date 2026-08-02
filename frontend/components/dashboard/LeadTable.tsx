'use client'

import { ChevronRight } from 'lucide-react'
import type { Lead } from '@/lib/api'
import { QualificationBadge } from './QualificationBadge'
import { StatusBadge } from './StatusBadge'
import { deriveLeadStatus, relativeTime } from '@/types/dashboard'

interface LeadTableProps {
  leads: Lead[]
  onSelectLead: (lead: Lead) => void
}

export function LeadTable({ leads, onSelectLead }: LeadTableProps) {
  if (leads.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card">
        <div className="flex h-32 items-center justify-center">
          <p className="text-sm text-muted-foreground">No leads yet</p>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      {/* Table header */}
      <div className="grid grid-cols-[2fr_1.5fr_1.1fr_1.1fr_90px_auto] gap-4 border-b border-border bg-muted/30 px-6 py-3">
        {['Lead', 'Company', 'Score', 'Status', 'Quality', ''].map((h) => (
          <div key={h} className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            {h}
          </div>
        ))}
      </div>

      {/* Rows */}
      <div className="divide-y divide-border">
        {leads.map((lead) => {
          const status  = deriveLeadStatus(lead.metadata)
          const score   = lead.metadata?.qualification_score
          const quality = lead.quality?.toUpperCase()

          return (
            <div
              key={lead.id}
              className="grid grid-cols-[2fr_1.5fr_1.1fr_1.1fr_90px_auto] gap-4 px-6 py-4 transition-colors hover:bg-muted/20 cursor-pointer"
              onClick={() => onSelectLead(lead)}
              role="row"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && onSelectLead(lead)}
            >
              {/* Lead name + email + captured time */}
              <div className="flex flex-col justify-center min-w-0">
                <p className="text-sm font-medium text-foreground truncate">
                  {lead.name ?? 'Anonymous'}
                </p>
                <p className="text-xs text-muted-foreground truncate">{lead.email}</p>
                {lead.captured_at && (
                  <p className="text-[10px] text-muted-foreground/60 mt-0.5">
                    {relativeTime(lead.captured_at)}
                  </p>
                )}
              </div>

              {/* Company */}
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

              {/* Score */}
              <div className="flex items-center">
                <QualificationBadge score={score} />
              </div>

              {/* Status */}
              <div className="flex items-center">
                <StatusBadge status={status} />
              </div>

              {/* Quality */}
              <div className="flex items-center">
                <QualityBadge quality={quality} />
              </div>

              {/* Chevron */}
              <div className="flex items-center justify-end">
                <span className="inline-flex h-7 w-7 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-muted hover:text-foreground">
                  <ChevronRight className="h-4 w-4" />
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Quality badge
// ---------------------------------------------------------------------------
function QualityBadge({ quality }: { quality?: string }) {
  if (!quality) return <span className="text-xs text-muted-foreground">—</span>

  const cfg =
    quality === 'HIGH'   ? 'bg-green-500/15 text-green-400'  :
    quality === 'MEDIUM' ? 'bg-amber-500/15 text-amber-400'  :
    quality === 'LOW'    ? 'bg-muted text-muted-foreground'   :
                           'bg-muted text-muted-foreground'

  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${cfg}`}>
      {quality.charAt(0) + quality.slice(1).toLowerCase()}
    </span>
  )
}
