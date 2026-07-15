export type LeadStatus = 'Drafting' | 'Awaiting Approval' | 'Syncing'
export type TraceStepName = 'Input' | 'Enrichment' | 'Qualification' | 'Critic Feedback'
export type TraceStepStatus = 'completed' | 'in-progress' | 'pending'

export interface TraceStep {
  id: string
  name: TraceStepName
  timestamp: Date
  status: TraceStepStatus
  data: Record<string, any>
}

export interface EnrichmentData {
  industry: string
  revenue: string
  employees: string
  website?: string
  linkedinUrl?: string
}

export interface Lead {
  id: string
  name: string
  company: string
  qualificationScore: number
  status: LeadStatus
  threadId: string
  enrichmentData: EnrichmentData
  timeline: TraceStep[]
  draftEmail?: string
  createdAt: Date
  lastModified: Date
}

export interface GraphStateResponse {
  threadId: string
  lead: Lead
  timeline: TraceStep[]
  lastUpdate: Date
}
