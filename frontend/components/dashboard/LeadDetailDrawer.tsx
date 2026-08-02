'use client'

import { X, User, Building2, CheckCircle2, XCircle, Clock, Tag } from 'lucide-react'
import type { Lead } from '@/lib/api'
import { deriveLeadStatus, deriveTraceSteps, relativeTime } from '@/types/dashboard'
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

  // Pass graphState so trace steps get contextual detail annotations
  const traceSteps = deriveTraceSteps(graphState?.current_node, graphState)

  if (!lead) return null

  const meta = lead.metadata ?? {}

  // Prefer live graph state for enrichment data; fall back to stored metadata
  const enrichment = graphState?.enrichment ?? {
    company_name:     meta.company_name,
    company_size:     meta.company_size,
    company_industry: meta.company_industry,
    lead_role:        meta.lead_role,
    source:           meta.enrichment_source,
  }

  const intentSignals: string[] = graphState?.intent_signals ?? meta.intent_signals ?? []
  const qualReasoning = graphState?.qualification_reasoning
  const capturedAt = lead.captured_at ? relativeTime(lead.captured_at) : null

  return (
    <>
      {/* Backdrop */}
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
        role="dialog"
        aria-modal="true"
        aria-label={`Lead details for ${lead.name ?? lead.email}`}
      >
        {/* Sticky header */}
        <div className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur-sm px-6 py-4">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <User className="h-4 w-4 text-primary" />
              </div>
              <div className="min-w-0">
                <h2 className="text-base font-semibold text-foreground truncate">
                  {lead.name ?? 'Anonymous'}
                </h2>
                <p className="text-xs text-muted-foreground truncate">{lead.email}</p>
                {capturedAt && (
                  <p className="text-xs text-muted-foreground mt-0.5 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    Captured {capturedAt}
                  </p>
                )}
              </div>
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

        <div className="space-y-6 px-6 py-6">

          {/* ── Summary ─────────────────────────────────────────── */}
          <Section title="Summary">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-muted/40 p-3 space-y-1">
                <p className="text-xs text-muted-foreground">Score</p>
                <QualificationBadge score={meta.qualification_score} />
              </div>
              <div className="rounded-lg bg-muted/40 p-3 space-y-1">
                <p className="text-xs text-muted-foreground">Status</p>
                {status && <StatusBadge status={status} />}
              </div>
              {lead.quality && (
                <div className="rounded-lg bg-muted/40 p-3 space-y-1">
                  <p className="text-xs text-muted-foreground">Quality</p>
                  <QualityPill quality={lead.quality} />
                </div>
              )}
              {meta.qualification_tier && (
                <div className="rounded-lg bg-muted/40 p-3 space-y-1">
                  <p className="text-xs text-muted-foreground">Tier</p>
                  <p className="text-sm font-semibold text-foreground capitalize">
                    {meta.qualification_tier}
                  </p>
                </div>
              )}
            </div>

            {qualReasoning && (
              <p className="mt-3 text-xs text-muted-foreground bg-muted/30 rounded-lg p-3 leading-relaxed">
                {qualReasoning}
              </p>
            )}
          </Section>

          {/* ── Intent Signals ──────────────────────────────────── */}
          {intentSignals.length > 0 && (
            <Section title="Intent Signals">
              <div className="flex flex-wrap gap-1.5">
                {intentSignals.map((signal) => (
                  <span
                    key={signal}
                    className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary"
                  >
                    <Tag className="h-3 w-3" />
                    {signal.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </Section>
          )}

          {/* ── Company / Enrichment ────────────────────────────── */}
          {(enrichment.company_name || enrichment.company_industry || enrichment.company_size || enrichment.lead_role) && (
            <Section title="Company Data">
              <div className="flex items-center gap-2 mb-3">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                {enrichment.source && (
                  <span className="text-xs text-muted-foreground">
                    via {enrichment.source}
                  </span>
                )}
              </div>
              <div className="space-y-2">
                {([
                  ['Company',  enrichment.company_name],
                  ['Industry', enrichment.company_industry],
                  ['Size',     enrichment.company_size],
                  ['Role',     enrichment.lead_role],
                ] as [string, string | undefined][]).map(([label, value]) =>
                  value ? (
                    <div
                      key={label}
                      className="flex items-center justify-between rounded-lg bg-muted/30 px-3 py-2"
                    >
                      <span className="text-xs text-muted-foreground">{label}</span>
                      <span className="text-sm font-medium text-foreground">{value}</span>
                    </div>
                  ) : null,
                )}
              </div>
            </Section>
          )}

          {/* ── HITL Outcome ────────────────────────────────────── */}
          {(meta.requires_human_approval || meta.human_approved != null) && (
            <Section title="HITL Outcome">
              {meta.human_approved === true && (
                <div className="flex items-start gap-3 rounded-lg bg-green-500/10 p-3">
                  <CheckCircle2 className="h-4 w-4 text-green-400 shrink-0 mt-0.5" />
                  <div className="space-y-0.5">
                    <p className="text-sm font-medium text-green-400">Approved</p>
                    {meta.human_reviewer && (
                      <p className="text-xs text-muted-foreground">by {meta.human_reviewer}</p>
                    )}
                    {meta.human_notes && (
                      <p className="text-xs text-muted-foreground italic">"{meta.human_notes}"</p>
                    )}
                  </div>
                </div>
              )}
              {meta.human_approved === false && (
                <div className="flex items-start gap-3 rounded-lg bg-destructive/10 p-3">
                  <XCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
                  <div className="space-y-0.5">
                    <p className="text-sm font-medium text-destructive">Rejected</p>
                    {meta.human_reviewer && (
                      <p className="text-xs text-muted-foreground">by {meta.human_reviewer}</p>
                    )}
                    {meta.human_notes && (
                      <p className="text-xs text-muted-foreground italic">"{meta.human_notes}"</p>
                    )}
                  </div>
                </div>
              )}
              {meta.requires_human_approval && meta.human_approved == null && (
                <div className="flex items-center gap-2 rounded-lg bg-orange-500/10 p-3">
                  <span className="h-2 w-2 rounded-full bg-orange-400 animate-pulse" />
                  <p className="text-sm text-orange-400">Awaiting reviewer decision</p>
                </div>
              )}
            </Section>
          )}

          {/* ── Pipeline Trace ──────────────────────────────────── */}
          <GraphTrace steps={traceSteps} currentNode={graphState?.current_node} />

          {/* ── Action Panel (HITL) ─────────────────────────────── */}
          {status === 'Awaiting Approval' && (
            <ActionPanel lead={lead} onClose={onClose} />
          )}

          {/* ── Contextual status banners ───────────────────────── */}
          {status === 'Manual Review' && (
            <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/20 p-4 space-y-1">
              <p className="text-sm font-medium text-yellow-400">Routed to Manual Review</p>
              {graphState?.error && (
                <p className="text-xs text-muted-foreground font-mono">{graphState.error}</p>
              )}
            </div>
          )}
          {status === 'Drafting' && (
            <div className="rounded-lg bg-blue-500/10 border border-blue-500/20 p-4">
              <p className="text-sm text-blue-400">
                Lead is being processed through the pipeline. Refresh in a few seconds.
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

// ---------------------------------------------------------------------------
// Quality pill sub-component
// ---------------------------------------------------------------------------
function QualityPill({ quality }: { quality: string }) {
  const cfg =
    quality === 'HIGH'   ? 'bg-green-500/20 text-green-400'  :
    quality === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400'  :
    quality === 'LOW'    ? 'bg-muted text-muted-foreground'   :
                           'bg-muted text-muted-foreground'
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${cfg}`}>
      {quality.charAt(0) + quality.slice(1).toLowerCase()}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Section wrapper
// ---------------------------------------------------------------------------
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      {children}
    </div>
  )
}
