// Re-export backend-aligned types from lib/api.ts as the canonical source
export type {
  Lead,
  LeadMetadata,
  LeadsResponse,
  GraphStateResponse,
  AnalyticsResponse,
  AnalyticsOverview,
  Conversation,
  Message,
  KnowledgeDocument,
  IngestResponse,
  IngestStatusResponse,
  ApprovalRequest,
  ApprovalResponse,
} from '@/lib/api'

// ---------------------------------------------------------------------------
// UI-only types (not directly from backend)
// ---------------------------------------------------------------------------

export type LeadStatus =
  | 'Drafting'
  | 'Awaiting Approval'
  | 'Approved'
  | 'Rejected'
  | 'Manual Review'
  | 'Syncing'

export type LeadQuality = 'HIGH' | 'MEDIUM' | 'LOW'

export type TraceStepStatus = 'completed' | 'in-progress' | 'pending'

export type TraceStepName =
  | 'input_node'
  | 'enrichment_node'
  | 'qualification_node'
  | 'drafting_node'
  | 'critic_node'
  | 'hitl_node'
  | 'deliver_node'
  | 'manual_review_node'

export interface TraceStep {
  name: TraceStepName | string
  status: TraceStepStatus
  /** Optional contextual data to render inside the step card */
  detail?: string
}

// ---------------------------------------------------------------------------
// Derive display status from backend lead metadata
// ---------------------------------------------------------------------------
export function deriveLeadStatus(
  metadata: import('@/lib/api').LeadMetadata,
): LeadStatus {
  if (metadata.is_manual_review) return 'Manual Review'
  if (metadata.requires_human_approval) {
    if (metadata.human_approved === true) return 'Approved'
    if (metadata.human_approved === false) return 'Rejected'
    return 'Awaiting Approval'
  }
  if (metadata.qualification_score == null) return 'Drafting'
  return 'Syncing'
}

// ---------------------------------------------------------------------------
// Derive lead quality label from backend quality string
// ---------------------------------------------------------------------------
export function deriveQualityLabel(quality?: string | null): string {
  switch ((quality ?? '').toUpperCase()) {
    case 'HIGH':   return 'High'
    case 'MEDIUM': return 'Medium'
    case 'LOW':    return 'Low'
    default:       return quality ?? '—'
  }
}

// ---------------------------------------------------------------------------
// Map backend current_node to ordered trace steps with optional detail
// ---------------------------------------------------------------------------
export const GRAPH_NODES: TraceStepName[] = [
  'input_node',
  'enrichment_node',
  'qualification_node',
  'hitl_node',
  'drafting_node',
  'critic_node',
  'deliver_node',
  'manual_review_node',
]

export function deriveTraceSteps(
  currentNode: string | undefined,
  graphState?: import('@/lib/api').GraphStateResponse | null,
): TraceStep[] {
  const currentIndex = GRAPH_NODES.indexOf(currentNode as TraceStepName)

  return GRAPH_NODES.map((name, i) => {
    const status: TraceStepStatus =
      currentIndex === -1
        ? 'pending'
        : i < currentIndex
          ? 'completed'
          : i === currentIndex
            ? 'in-progress'
            : 'pending'

    // Attach contextual detail for key nodes
    let detail: string | undefined
    if (graphState) {
      if (name === 'qualification_node' && graphState.qualification_score != null) {
        detail = `Score ${graphState.qualification_score}/100 · ${graphState.qualification_tier ?? ''}`
      } else if (name === 'enrichment_node' && graphState.enrichment?.company_name) {
        detail = graphState.enrichment.company_name
      } else if (name === 'critic_node') {
        if (graphState.critic_approved === true) detail = 'Approved'
        else if (graphState.critic_approved === false)
          detail = `Rejected (${graphState.critic_revision_count} revision${graphState.critic_revision_count !== 1 ? 's' : ''})`
      } else if (name === 'hitl_node' && graphState.requires_human_approval) {
        if (graphState.human_approved === true) detail = `Approved by ${graphState.human_reviewer ?? 'reviewer'}`
        else if (graphState.human_approved === false) detail = `Rejected by ${graphState.human_reviewer ?? 'reviewer'}`
        else detail = 'Awaiting human decision'
      }
    }

    return { name, status, detail }
  })
}

// ---------------------------------------------------------------------------
// Format relative time (e.g. "3 minutes ago")
// ---------------------------------------------------------------------------
export function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const seconds = Math.floor(diff / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}
