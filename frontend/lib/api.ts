import { getToken, clearToken } from '@/lib/auth'

export const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

/** Fired on the window whenever a 401 is received, so listeners can redirect to /login. */
export const UNAUTHORIZED_EVENT = 'auth:unauthorized'

/**
 * Error thrown for any non-2xx API response. Carries the HTTP status and a
 * human-readable detail so callers (forms, toast, banner) can branch on it.
 */
export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function getAuthHeaders(): HeadersInit {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...init?.headers,
    },
  })

  if (!res.ok) {
    // On an expired/invalid token, clear it and notify listeners so the app
    // can bounce to /login once. We still throw so the calling query/mutation
    // sees a failure too.
    if (res.status === 401 && typeof window !== 'undefined') {
      clearToken()
      window.dispatchEvent(new CustomEvent(UNAUTHORIZED_EVENT))
    }

    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new ApiError(res.status, detail?.detail ?? `Request failed: ${res.status}`)
  }

  // Some endpoints (e.g. DELETE) return no body; avoid a JSON parse error.
  if (res.status === 204) return undefined as T
  const text = await res.text()
  return (text ? JSON.parse(text) : undefined) as T
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface LoginResponse {
  access_token: string
  token_type: string
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export async function getMe(): Promise<{ email: string }> {
  return request<{ email: string }>('/api/auth/me')
}

/** Server logout is a no-op (the backend just drops the client-held JWT); safe to best-effort. */
export async function logout(): Promise<void> {
  try {
    await request<void>('/api/auth/logout', { method: 'POST' })
  } catch {
    // The server may already consider the session invalid; client-side cleanup still runs.
  }
}

// ---------------------------------------------------------------------------
// Leads
// ---------------------------------------------------------------------------

export interface LeadMetadata {
  qualification_score?: number
  qualification_tier?: 'hot' | 'warm' | 'cold'
  intent_signals?: string[]
  recommended_action?: string
  company_name?: string
  company_size?: string
  company_industry?: string
  lead_role?: string
  enrichment_source?: string
  requires_human_approval?: boolean
  human_approved?: boolean | null
  human_reviewer?: string
  human_notes?: string
  is_manual_review?: boolean
}

export interface Lead {
  id: string
  conversation_id: string
  business_id?: string
  email: string
  name?: string
  intent?: string
  quality?: string
  captured_via?: string
  metadata: LeadMetadata
  captured_at?: string
}

export interface LeadsResponse {
  leads: Lead[]
  total: number
}

export async function fetchLeads(): Promise<LeadsResponse> {
  return request<LeadsResponse>('/api/leads')
}

// ---------------------------------------------------------------------------
// Graph
// ---------------------------------------------------------------------------

export interface GraphInvokeRequest {
  session_id: string
  message: string
  lead_email?: string
  lead_name?: string
}

export interface GraphInvokeResponse {
  session_id: string
  response: string
  status: 'complete' | 'pending_approval' | 'manual_review'
  conversation_state?: string
  qualification_score?: number
  qualification_tier?: string
  lead_captured: boolean
  requires_human_approval: boolean
  is_manual_review: boolean
  elapsed_ms: number
}

export interface GraphStateResponse {
  session_id: string
  current_node?: string
  legacy_stage?: string
  lead_email?: string
  lead_name?: string
  qualification_score?: number
  qualification_tier?: string
  qualification_reasoning?: string
  intent_signals?: string[]
  enrichment: {
    company_name?: string
    company_size?: string
    company_industry?: string
    lead_role?: string
    source?: string
  }
  critic_approved?: boolean
  critic_revision_count: number
  requires_human_approval: boolean
  human_approved?: boolean | null
  is_manual_review: boolean
  error?: string
}

export async function fetchGraphState(sessionId: string): Promise<GraphStateResponse> {
  return request<GraphStateResponse>(`/api/graph/state/${sessionId}`)
}

export async function invokeGraph(body: GraphInvokeRequest): Promise<GraphInvokeResponse> {
  return request<GraphInvokeResponse>('/api/graph/invoke', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export interface ApprovalRequest {
  approved: boolean
  reviewer?: string
  notes?: string
}

export interface ApprovalResponse {
  session_id: string
  approved: boolean
  status: string
  final_response?: string
}

export async function approveLead(
  sessionId: string,
  payload: ApprovalRequest,
): Promise<ApprovalResponse> {
  return request<ApprovalResponse>(`/api/graph/approve/${sessionId}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export interface AnalyticsOverview {
  total_conversations: number
  total_leads: number
  conversion_rate: number
  avg_messages_per_conversation: number
}

export interface AnalyticsResponse {
  overview: AnalyticsOverview
  lead_quality: { quality: string; count: number }[]
  intent_breakdown: { intent: string; count: number }[]
  time_series: {
    conversations: { date: string; count: number }[]
    leads: { date: string; count: number }[]
  }
  period_days: number
}

export async function fetchAnalytics(days = 30): Promise<AnalyticsResponse> {
  return request<AnalyticsResponse>(`/api/analytics?days=${days}`)
}

// ---------------------------------------------------------------------------
// Conversations
// ---------------------------------------------------------------------------

export interface Conversation {
  id: string
  session_id: string
  created_at: string
  updated_at: string
  message_count: number
  email?: string
  name?: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export async function fetchConversations(): Promise<{ conversations: Conversation[]; total: number }> {
  return request('/api/conversations')
}

export async function fetchConversation(id: string): Promise<{ conversation: Conversation; messages: Message[] }> {
  return request(`/api/conversations/${id}`)
}

// ---------------------------------------------------------------------------
// Knowledge
// ---------------------------------------------------------------------------

export interface KnowledgeDocument {
  id: string
  business_id: string
  title: string
  content: string
  category: string
  source: string
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

export async function fetchKnowledge(): Promise<KnowledgeDocument[]> {
  const data = await request<KnowledgeDocument[] | { documents: KnowledgeDocument[] }>('/api/knowledge')
  return Array.isArray(data) ? data : data.documents ?? []
}

export async function createKnowledge(payload: {
  title: string
  content: string
  category: string
  source?: string
}): Promise<KnowledgeDocument> {
  return request('/api/knowledge', { method: 'POST', body: JSON.stringify(payload) })
}

export async function updateKnowledge(id: string, payload: Partial<KnowledgeDocument>): Promise<KnowledgeDocument> {
  return request(`/api/knowledge/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
}

export async function deleteKnowledge(id: string): Promise<void> {
  return request(`/api/knowledge/${id}`, { method: 'DELETE' })
}

// ---------------------------------------------------------------------------
// Ingestion
// ---------------------------------------------------------------------------

export interface IngestResponse {
  document_id: string
  title: string
  category: string
  chunks_indexed: number
  total_vectors: number
  message: string
}

export interface IngestStatusResponse {
  collection: string
  total_vectors: number
  vector_size: number
  status: string
}

export async function fetchIngestStatus(): Promise<IngestStatusResponse> {
  return request<IngestStatusResponse>('/api/ingest/status')
}

export async function ingestFile(file: File, title?: string, category?: string): Promise<IngestResponse> {
  const form = new FormData()
  form.append('file', file)
  if (title) form.append('title', title)
  if (category) form.append('category', category)

  const token = getToken()
  const res = await fetch(`${BASE_URL}/api/ingest/file`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  })

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }))
    throw new ApiError(res.status, detail?.detail ?? `Upload failed: ${res.status}`)
  }
  return res.json()
}

export async function ingestText(payload: {
  title: string
  content: string
  category?: string
  source?: string
}): Promise<IngestResponse> {
  return request<IngestResponse>('/api/ingest/text', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${BASE_URL}/health`)
  return res.json()
}
