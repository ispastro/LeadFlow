'use client'

import { useState, useRef } from 'react'
import { useCurrentUser, useHealth, useIngestStatus, useIngestFile } from '@/lib/queries'
import { Upload, Loader2, CheckCircle2, AlertCircle, Database, Server } from 'lucide-react'

export default function SettingsPage() {
  const { data: user } = useCurrentUser()
  const health = useHealth()
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
      setUploadMsg({ type: 'success', text: `"${result.title}" uploaded — ${result.chunks_indexed} chunks indexed (${result.total_vectors} total vectors)` })
    } catch (err) {
      setUploadMsg({ type: 'error', text: (err as Error).message ?? 'Upload failed' })
    }

    // Reset the file input so the same file can be re-uploaded
    e.target.value = ''
  }

  return (
    <div className="space-y-8 px-6 py-6 max-w-3xl">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground">System information and configuration</p>
      </div>

      {/* Account */}
      <Section title="Account">
        <div className="grid gap-3 text-sm">
          <Row label="Email" value={user?.email ?? '—'} />
        </div>
      </Section>

      {/* Backend health */}
      <Section title="Backend Connection">
        <div className="grid gap-3 text-sm">
          <Row
            label="Status"
            value={
              health.data
                ? `${health.data.status} · ${health.data.service}`
                : health.isPending
                  ? 'Checking…'
                  : 'Unreachable'
            }
            icon={
              health.data ? (
                <CheckCircle2 className="h-4 w-4 text-green-400" />
              ) : (
                <AlertCircle className="h-4 w-4 text-destructive" />
              )
            }
          />
          <Row label="API URL" value={process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'} />
        </div>
      </Section>

      {/* Vector store */}
      <Section title="Vector Store (Qdrant)">
        {ingestStatus.data ? (
          <div className="grid gap-3 text-sm">
            <Row label="Collection" value={ingestStatus.data.collection} icon={<Database className="h-4 w-4 text-muted-foreground" />} />
            <Row label="Total vectors" value={String(ingestStatus.data.total_vectors)} />
            <Row label="Vector size" value={String(ingestStatus.data.vector_size)} />
            <Row label="Status" value={ingestStatus.data.status} />
          </div>
        ) : ingestStatus.isPending ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            Could not load vector store status
          </div>
        )}
      </Section>

      {/* File ingestion */}
      <Section title="Ingest Knowledge">
        <p className="text-sm text-muted-foreground mb-3">
          Upload a document to index into the knowledge base. Supported formats: TXT, MD, CSV, PDF, DOCX (max 10 MB).
        </p>

        <input ref={fileRef} type="file" accept=".txt,.md,.csv,.pdf,.docx" className="hidden" onChange={handleFileChange} />

        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={ingestFile.isPending}
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-muted disabled:opacity-50"
        >
          {ingestFile.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
          {ingestFile.isPending ? 'Uploading…' : 'Upload File'}
        </button>

        {uploadMsg && (
          <div
            className={`mt-3 rounded-lg border px-3 py-2 text-sm ${
              uploadMsg.type === 'success'
                ? 'border-green-500/30 bg-green-500/10 text-green-400'
                : 'border-destructive/30 bg-destructive/10 text-destructive'
            }`}
          >
            {uploadMsg.text}
          </div>
        )}
      </Section>

      {/* About */}
      <Section title="About">
        <div className="grid gap-3 text-sm">
          <Row label="App" value="LeadFlow RevOps Engine" icon={<Server className="h-4 w-4 text-muted-foreground" />} />
          <Row label="Version" value="2.0" />
        </div>
      </Section>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Shared sub-components
// ---------------------------------------------------------------------------

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-card p-5 space-y-4">
      <h2 className="text-sm font-semibold text-foreground">{title}</h2>
      {children}
    </div>
  )
}

function Row({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center gap-2 text-muted-foreground">
        {icon}
        {label}
      </span>
      <span className="font-medium text-foreground">{value}</span>
    </div>
  )
}
