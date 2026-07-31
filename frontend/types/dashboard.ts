// Re-export backend-aligned types from lib/api.ts as the canonical source
export type { Lead, LeadMetadata, LeadsResponse, GraphStateResponse, AnalyticsResponse } from '@/lib/api'

// ---------------------------------------------------------------------------
// UI-only types (not directly from backend)
// ---------------------------------------------------------------------------

export type LeadStatus = 'Drafting' | 'Awaiting Approval' | 'Approved' | 'Rejected' | 'Manual Review' | 'Syncing'

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
}

// Derive display status from backend lead metadata
export function deriveLeadStatus(metadata: import('@/lib/api').LeadMetadata): LeadStatus {
  if (metadata.is_manual_review) return 'Manual Review'
  if (metadata.requires_human_approval) {
    if (metadata.human_approved === true)  return 'Approved'
    if (metadata.human_approved === false) return 'Rejected'
    return 'Awaiting Approval'
  }
  if (metadata.qualification_score == null) return 'Drafting'
  return 'Syncing'
}

// Map backend current_node to ordered trace steps
export const GRAPH_NODES: TraceStepName[] = [
  'input_node',
  'enrichment_node',
  'qualification_node',
  'drafting_node',
  'critic_node',
  'hitl_node',
  'deliver_node',
  'manual_review_node',
]

export function deriveTraceSteps(currentNode: string | undefined): TraceStep[] {
  const currentIndex = GRAPH_NODES.indexOf(currentNode as TraceStepName)
  return GRAPH_NODES.map((name, i) => ({
    name,
    status:
      currentIndex === -1 ? 'pending'
      : i < currentIndex  ? 'completed'
      : i === currentIndex ? 'in-progress'
      : 'pending',
  }))
}
