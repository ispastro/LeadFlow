import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryOptions,
} from '@tanstack/react-query'
import * as api from './api'
import { setToken, clearToken, isAuthenticated } from './auth'
import { useRouter } from 'next/navigation'

// ---------------------------------------------------------------------------
// Query keys — single source of truth
// ---------------------------------------------------------------------------
export const keys = {
  me:               ['auth', 'me']                      as const,
  leads:            ['leads']                           as const,
  graphState:       (sid: string) => ['graph', sid]    as const,
  analytics:        (days: number) => ['analytics', days] as const,
  conversations:    ['conversations']                   as const,
  conversation:     (id: string) => ['conversation', id] as const,
  knowledge:        ['knowledge']                       as const,
  health:           ['health']                          as const,
}

// ---------------------------------------------------------------------------
// Auth — current user, login, logout
// ---------------------------------------------------------------------------

/**
 * Validates the stored token against the server and exposes the signed-in user.
 * `enabled` only when a token is present so the login page (no token yet)
 * doesn't fire a guaranteed 401. `retry: false` so a single 401 fails fast —
 * the global handler in api.ts already cleared the token + will redirect.
 */
export function useCurrentUser() {
  return useQuery({
    queryKey: keys.me,
    queryFn: api.getMe,
    enabled: isAuthenticated(),
    retry: false,
    staleTime: 5 * 60_000,
  })
}

export function useLogin() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      api.login(email, password),
    onSuccess: (data, { email }) => {
      setToken(data.access_token)
      // Prime the current-user cache so AuthGuard/Header don't re-fetch.
      qc.setQueryData(keys.me, { email })
      // Drop any cache left over from a previous (possibly different) session.
      qc.removeQueries({ predicate: (q) => q.queryKey[0] !== 'auth' })
    },
  })
}

export function useLogout() {
  const qc = useQueryClient()
  const router = useRouter()
  return useMutation({
    mutationFn: () => api.logout(),
    onSettled: () => {
      clearToken()
      qc.clear()
      router.replace('/login')
    },
  })
}

// ---------------------------------------------------------------------------
// Leads
// ---------------------------------------------------------------------------

export function useLeads() {
  return useQuery({
    queryKey: keys.leads,
    queryFn: api.fetchLeads,
    // Poll every 15s so pending HITL leads update without a manual refresh
    refetchInterval: 15_000,
    staleTime: 10_000,
  })
}

export function useLeadsPendingApproval() {
  const { data, ...rest } = useLeads()
  const pending = data?.leads.filter(
    (l) => l.metadata?.requires_human_approval && l.metadata?.human_approved == null,
  ) ?? []
  return { pending, total: pending.length, ...rest }
}

// ---------------------------------------------------------------------------
// Graph state
// ---------------------------------------------------------------------------

export function useGraphState(
  sessionId: string | null,
  opts?: Partial<UseQueryOptions<api.GraphStateResponse>>,
) {
  return useQuery({
    queryKey: keys.graphState(sessionId ?? ''),
    queryFn: () => api.fetchGraphState(sessionId!),
    enabled: !!sessionId,
    refetchInterval: sessionId ? 10_000 : false,
    ...opts,
  })
}

// ---------------------------------------------------------------------------
// HITL approval mutation
// ---------------------------------------------------------------------------

export function useApproveLead() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      sessionId,
      payload,
    }: {
      sessionId: string
      payload: api.ApprovalRequest
    }) => api.approveLead(sessionId, payload),
    onSuccess: (_data, { sessionId }) => {
      // Invalidate the leads list and the specific graph state
      qc.invalidateQueries({ queryKey: keys.leads })
      qc.invalidateQueries({ queryKey: keys.graphState(sessionId) })
    },
  })
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export function useAnalytics(days = 30) {
  return useQuery({
    queryKey: keys.analytics(days),
    queryFn: () => api.fetchAnalytics(days),
    staleTime: 60_000,
  })
}

// ---------------------------------------------------------------------------
// Conversations
// ---------------------------------------------------------------------------

export function useConversations() {
  return useQuery({
    queryKey: keys.conversations,
    queryFn: api.fetchConversations,
    staleTime: 30_000,
  })
}

export function useConversation(id: string | null) {
  return useQuery({
    queryKey: keys.conversation(id ?? ''),
    queryFn: () => api.fetchConversation(id!),
    enabled: !!id,
  })
}

// ---------------------------------------------------------------------------
// Knowledge base
// ---------------------------------------------------------------------------

export function useKnowledge() {
  return useQuery({
    queryKey: keys.knowledge,
    queryFn: api.fetchKnowledge,
    staleTime: 60_000,
  })
}

export function useCreateKnowledge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.createKnowledge,
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.knowledge }),
  })
}

export function useUpdateKnowledge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<api.KnowledgeDocument> }) =>
      api.updateKnowledge(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.knowledge }),
  })
}

export function useDeleteKnowledge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.deleteKnowledge,
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.knowledge }),
  })
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export function useHealth() {
  return useQuery({
    queryKey: keys.health,
    queryFn: api.fetchHealth,
    staleTime: 30_000,
    retry: false,
  })
}

// ---------------------------------------------------------------------------
// Ingestion
// ---------------------------------------------------------------------------

export const ingestKeys = {
  status: ['ingest', 'status'] as const,
}

export function useIngestStatus() {
  return useQuery({
    queryKey: ingestKeys.status,
    queryFn: api.fetchIngestStatus,
    staleTime: 60_000,
    retry: false,
  })
}

export function useIngestFile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ file, title, category }: { file: File; title?: string; category?: string }) =>
      api.ingestFile(file, title, category),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ingestKeys.status })
      qc.invalidateQueries({ queryKey: keys.knowledge })
    },
  })
}

export function useIngestText() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.ingestText,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ingestKeys.status })
      qc.invalidateQueries({ queryKey: keys.knowledge })
    },
  })
}
