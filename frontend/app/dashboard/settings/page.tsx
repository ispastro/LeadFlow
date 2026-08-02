'use client'

import { useState, useRef } from 'react'
import {
  useCurrentUser,
  useHealth,
  useIngestStatus,
  useIngestFile,
  useServiceInfo,
} from '@/lib/queries'
import {
  Upload,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Database,
  Server,
  Activity,
  ShieldCheck,
} from 'lucide-react'

export default function SettingsPage() {
  const { data: user } = useCurrentUser()
  const health = useHealth()
  const serviceInfo = useServiceInfo()
  const ingestStatus = useIngestStatus()
  const ingestFile = useIngestFile()
  const fileRef = useRef<HTMLInputElement>(null)
  const [uploadMsg, setUploadMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadMsg(null)
    try {
      const result = await ingestFile.mutateAsync({ file })
      setUploadMsg({
        type: 'success',
        text: `"${result.title}" uploaded — ${result.chunks_indexed} chunk(s) indexed (${result.total_vectors} total vectors)`,
      })
    } catch (err) {
      setUploadMsg({ type: 'error', text: (err as Error).message ?? 'Upload failed' })
    }
    e.target.value = ''
  }

  const isHealthy = health.data?.status === 'healthy'

  return (
    <div className="space-y-8 px-6 py-6 max-w-3xl">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground">System information and configuration</p>
      </div>

      {/* Account */}
      <Section title="Account" icon={<ShieldCheck className="h-4 w-4" />}>
        <Row label="Email" value={user?.email ?? '—'} />
        <Row label="Role" value="Admin" />
      </Section>

      {/* Backend health */}
      <Section title="Backend Connection" icon={<Activity className="h-4 w-4" />}>
        <Row
          label="Status"
          value={
            health.data
              ? `${health.data.status}`
              : health.isPending
                ? 'Checking…'
                : 'Unreachable'
          }
          icon={
            isHealthy ? (
              <CheckCircle2 className="h-4 w-4 text-green-400" />
            ) : health.isPending ? null : (
              <AlertCircle className="h-4 w-4 text-destructive" />
            )
          }
          valueColor={isHealthy ? 'text-green-400' : health.isError ? 'text-destructive' : undefined}
        />
        {health.data?.service && (
          <Row label="Service" value={health.data.service} />
        )}
        <Row
          label="API URL"
          value={process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}
          mono
        />
      </Section>

      {/* Service info */}
      <Section title="Application" icon={<Server className="h-4 w-4" />}>
        <Row
          label="Name"
          value={serviceInfo.data?.service ?? 'LeadFlow RevOps Engine'}
        />
        <Row
          label="Version"
          value={serviceInfo.data?.version ?? '—'}
        />
        <Row
          label="Graph Endpoint"
          value={serviceInfo.data?.graph_endpoint ?? '/api/graph/invoke'}
          mono
        />
        <Row
          label="HITL Score Threshold"
          value="≥ 90 / 100"
        />
        <Row
          label="Qualification Tiers"
          value="hot (≥70) · warm (50-69) · cold (<50)"
        />
      </Section>

      {/* Vector store */}
      <Section title="Vector Store (Qdrant)" icon={<Database className="h-4 w-4" />}>
        {ingestStatus.data ? (
          <>
            <Row
              label="Collection"
              value={ingestStatus.data.collection ?? '—'}
              icon={<Database className="h-4 w-4 text-muted-foreground" />}
            />
            <Row
              label="Total vectors"
              value={ingestStatus.data.total_vectors?.toLocaleString() ?? '0'}
            />
            <Row
              label="Vector size"
              value={`${ingestStatus.data.vector_size ?? 384} dimensions`}
            />
            <Row
              label="Collection status"
              value={String(ingestStatus.data.status ?? '—')}
            />
          </>
        ) : ingestStatus.isPending ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            Could not load vector store status — check Qdrant credentials
          </div>
        )}
      </Section>

      {/* File ingestion */}
      <Section title="Ingest Knowledge" icon={<Upload className="h-4 w-4" />}>
        <p className="text-sm text-muted-foreground">
          Upload a document to index directly into Qdrant. Supported: TXT, MD, CSV, PDF, DOCX (max 10 MB).
          For full knowledge management, use the{' '}
          <a href="/dashboard/knowledge" className="text-primary hover:underline">
            Knowledge Base
          </a>{' '}
          page.
        </p>

        <input
          ref={fileRef}
          type="file"
          accept=".txt,.md,.csv,.pdf,.docx"
          className="hidden"
          onChange={handleFileChange}
        />

        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={ingestFile.isPending}
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-muted disabled:opacity-50"
        >
          {ingestFile.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Upload className="h-4 w-4" />
          )}
          {ingestFile.isPending ? 'Uploading…' : 'Upload File'}
        </button>

        {uploadMsg && (
          <div
            className={`rounded-lg border px-3 py-2.5 text-sm ${
              uploadMsg.type === 'success'
                ? 'border-green-500/30 bg-green-500/10 text-green-400'
                : 'border-destructive/30 bg-destructive/10 text-destructive'
            }`}
          >
            {uploadMsg.text}
          </div>
        )}
      </Section>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Shared sub-components
// ---------------------------------------------------------------------------

function Section({
  title,
  icon,
  children,
}: {
  title: string
  icon?: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-5 space-y-4">
      <h2 className="flex items-center gap-2 text-sm font-semibold text-foreground">
        {icon && <span className="text-muted-foreground">{icon}</span>}
        {title}
      </h2>
      <div className="space-y-3">{children}</div>
    </div>
  )
}

function Row({
  label,
  value,
  icon,
  mono,
  valueColor,
}: {
  label: string
  value: string
  icon?: React.ReactNode
  mono?: boolean
  valueColor?: string
}) {
  return (
    <div className="flex items-center justify-between gap-4 text-sm">
      <span className="flex items-center gap-2 text-muted-foreground shrink-0">
        {icon}
        {label}
      </span>
      <span
        className={`font-medium text-right truncate ${valueColor ?? 'text-foreground'} ${mono ? 'font-mono text-xs' : ''}`}
      >
        {value}
      </span>
    </div>
  )
}
