import type { GraphStateResponse, Lead } from '@/types/dashboard'
import { mockLeads, getLeadById } from './mock-data'

/**
 * Fetches the graph state for a specific thread (lead).
 * Currently uses mock data but structure is ready for real API integration.
 * Future: Replace with actual fetch to /api/graph/state/{thread_id}
 */
export async function fetchGraphState(threadId: string): Promise<GraphStateResponse> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 300))

  // In production, this would be:
  // const response = await fetch(`/api/graph/state/${threadId}`)
  // return response.json()

  // For now, find the lead from mock data by threadId
  const lead = mockLeads.find((l) => l.threadId === threadId)

  if (!lead) {
    throw new Error(`Lead not found for thread ${threadId}`)
  }

  return {
    threadId,
    lead,
    timeline: lead.timeline,
    lastUpdate: new Date(),
  }
}

/**
 * Approves and syncs a lead.
 * Future: Replace with actual API call to backend.
 */
export async function approveLead(leadId: string): Promise<{ success: boolean; leadId: string }> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  // In production, this would POST to /api/leads/{leadId}/approve
  console.log(`[Dashboard API] Approving lead: ${leadId}`)

  return {
    success: true,
    leadId,
  }
}

/**
 * Rejects a lead.
 * Future: Replace with actual API call to backend.
 */
export async function rejectLead(leadId: string, reason?: string): Promise<{ success: boolean; leadId: string }> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  // In production, this would POST to /api/leads/{leadId}/reject
  console.log(`[Dashboard API] Rejecting lead: ${leadId}`, reason ? `Reason: ${reason}` : '')

  return {
    success: true,
    leadId,
  }
}

/**
 * Fetches all leads.
 * Future: Replace with TanStack Query hook.
 */
export async function fetchAllLeads(): Promise<Lead[]> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 200))

  // In production, this would fetch from /api/leads
  return mockLeads
}
