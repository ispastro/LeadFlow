'use client'

import { useState, useRef } from 'react'
import {
  useKnowledge,
  useCreateKnowledge,
  useUpdateKnowledge,
  useDeleteKnowledge,
  useIngestFile,
  useIngestText,
  useIngestStatus,
} from '@/lib/queries'
import type { KnowledgeDocument } from '@/lib/api'
import {
  Plus,
  Trash2,
  X,
  Loader2,
  FileText,
  Upload,
  RefreshCw,
  Database,
  Edit2,
  Check,
  FileUp,
  AlignLeft,
} from 'lucide-react'

type Tab = 'documents' | 'upload-file' | 'upload-text'

export default function KnowledgePage() {
  const { data, isPending, error } = useKnowledge()
  const { data: ingestStatus } = useIngestStatus()
  const create = useCreateKnowledge()
  const update = useUpdateKnowledge()
  const remove = useDeleteKnowledge()
  const ingestFile = useIngestFile()
  const ingestText = useIngestText()

  const [tab, setTab] = useState<Tab>('documents')
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [uploadMsg, setUploadMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const documents: KnowledgeDocument[] = data ?? []

  // ── Create document ─────────────────────────────────────
  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setFormError(null)
    const fd = new FormData(e.currentTarget)
    const title    = (fd.get('title')    as string).trim()
    const content  = (fd.get('content')  as string).trim()
    const category = (fd.get('category') as string) || 'general'
    const source   = (fd.get('source')   as string) || 'manual'
    if (!title || !content) return

    try {
      await create.mutateAsync({ title, content, category, source })
      setShowAddForm(false)
      ;(e.target as HTMLFormElement).reset()
    } catch (err) {
      setFormError((err as Error).message ?? 'Failed to create document')
    }
  }

  // ── Inline edit ─────────────────────────────────────────
  function startEdit(doc: KnowledgeDocument) {
    setEditingId(doc.id)
    setEditContent(doc.content)
  }

  async function submitEdit(doc: KnowledgeDocument) {
    if (!editContent.trim()) return
    try {
      await update.mutateAsync({ id: doc.id, payload: { content: editContent.trim() } })
      setEditingId(null)
    } catch {
      // error handled by mutation state
    }
  }

  // ── File upload ─────────────────────────────────────────
  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadMsg(null)
    try {
      const result = await ingestFile.mutateAsync({ file })
      setUploadMsg({
        type: 'success',
        text: `"${result.title}" indexed — ${result.chunks_indexed} chunk(s), ${result.total_vectors} total vectors`,
      })
    } catch (err) {
      setUploadMsg({ type: 'error', text: (err as Error).message ?? 'Upload failed' })
    }
    e.target.value = ''
  }

  // ── Text ingest ─────────────────────────────────────────
  async function handleTextIngest(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setUploadMsg(null)
    const fd = new FormData(e.currentTarget)
    const title   = (fd.get('ingest-title')   as string).trim()
    const content = (fd.get('ingest-content') as string).trim()
    const category = (fd.get('ingest-category') as string) || 'general'
    if (!title || !content) return
    try {
      const result = await ingestText.mutateAsync({ title, content, category })
      setUploadMsg({
        type: 'success',
        text: `"${result.title}" indexed — ${result.chunks_indexed} chunk(s), ${result.total_vectors} total vectors`,
      })
      ;(e.target as HTMLFormElement).reset()
    } catch (err) {
      setUploadMsg({ type: 'error', text: (err as Error).message ?? 'Ingest failed' })
    }
  }

  // ── Sync to Qdrant ──────────────────────────────────────
  async function handleSync() {
    setSyncing(true)
    setSyncMsg(null)
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
      const headers: Record<string, string> = { 'Content-Type': 'application/json' }
      if (token) headers['Authorization'] = `Bearer ${token}`
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/knowledge/sync`,
        { method: 'POST', headers },
      )
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail ?? 'Sync failed')
      setSyncMsg({ type: 'success', text: data.message ?? `Synced ${data.documents_synced} document(s)` })
    } catch (err) {
      setSyncMsg({ type: 'error', text: (err as Error).message ?? 'Sync failed' })
    } finally {
      setSyncing(false)
    }
  }

  // ── Loading / error states ──────────────────────────────
  if (isPending) {
    return (
      <div className="space-y-6 px-6 py-6">
        <div className="h-7 w-56 rounded-md bg-muted animate-pulse" />
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-4 px-6 py-4 border-b border-border last:border-0">
              <div className="h-4 w-48 rounded bg-muted animate-pulse" />
              <div className="h-4 w-20 rounded bg-muted animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-6 py-6">
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          Failed to load knowledge base: {(error as Error).message}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 px-6 py-6">

      {/* ── Header ──────────────────────────────────────── */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-foreground">Knowledge Base</h1>
          <div className="flex items-center gap-3">
            <p className="text-sm text-muted-foreground">
              {documents.length} document{documents.length !== 1 ? 's' : ''}
            </p>
            {ingestStatus && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-muted/60 px-2.5 py-0.5 text-xs text-muted-foreground">
                <Database className="h-3 w-3" />
                {ingestStatus.total_vectors?.toLocaleString() ?? 0} vectors in Qdrant
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleSync}
            disabled={syncing}
            title="Re-sync all documents to Qdrant"
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:opacity-50"
          >
            {syncing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Sync to Qdrant
          </button>
          <button
            type="button"
            onClick={() => { setShowAddForm((v) => !v); setTab('documents') }}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-muted"
          >
            {showAddForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showAddForm ? 'Cancel' : 'Add Document'}
          </button>
        </div>
      </div>

      {/* Sync feedback */}
      {syncMsg && (
        <div
          className={`rounded-lg border px-4 py-2.5 text-sm ${
            syncMsg.type === 'success'
              ? 'border-green-500/30 bg-green-500/10 text-green-400'
              : 'border-destructive/30 bg-destructive/10 text-destructive'
          }`}
        >
          {syncMsg.text}
        </div>
      )}

      {/* ── Tab bar ─────────────────────────────────────── */}
      <div className="flex gap-1 rounded-lg border border-border bg-muted/30 p-1 w-fit">
        {(
          [
            { value: 'documents',    label: 'Documents',    icon: FileText },
            { value: 'upload-file',  label: 'Upload File',  icon: FileUp   },
            { value: 'upload-text',  label: 'Paste Text',   icon: AlignLeft },
          ] as const
        ).map(({ value, label, icon: Icon }) => (
          <button
            key={value}
            onClick={() => { setTab(value); setShowAddForm(false); setUploadMsg(null) }}
            className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              tab === value
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Icon className="h-3.5 w-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* ── Add document form (Documents tab) ───────────── */}
      {tab === 'documents' && showAddForm && (
        <form
          onSubmit={handleCreate}
          className="space-y-4 rounded-xl border border-border bg-card/80 p-6"
        >
          <p className="text-sm font-medium text-foreground">New Document</p>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="kb-title">Title</Label>
              <Input id="kb-title" name="title" placeholder="Document title" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="kb-category">Category</Label>
              <Input id="kb-category" name="category" placeholder="general" defaultValue="general" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="kb-source">Source</Label>
              <Input id="kb-source" name="source" placeholder="manual" defaultValue="manual" />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="kb-content">Content</Label>
            <textarea
              id="kb-content"
              name="content"
              required
              rows={6}
              placeholder="Document content…"
              className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1 resize-y"
            />
          </div>
          {formError && <ErrorBanner>{formError}</ErrorBanner>}
          <button
            type="submit"
            disabled={create.isPending}
            className="inline-flex h-9 items-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {create.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            {create.isPending ? 'Creating…' : 'Create & Sync'}
          </button>
        </form>
      )}

      {/* ── Upload File tab ──────────────────────────────── */}
      {tab === 'upload-file' && (
        <div className="rounded-xl border border-border bg-card/80 p-6 space-y-4">
          <div>
            <p className="text-sm font-medium text-foreground">Upload a document</p>
            <p className="text-xs text-muted-foreground mt-1">
              Supported: TXT, MD, CSV, PDF, DOCX — max 10 MB. Content is chunked and indexed into
              Qdrant automatically.
            </p>
          </div>
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
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-muted disabled:opacity-50"
          >
            {ingestFile.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Upload className="h-4 w-4" />
            )}
            {ingestFile.isPending ? 'Uploading & indexing…' : 'Choose File'}
          </button>
          {uploadMsg && <FeedbackBanner type={uploadMsg.type}>{uploadMsg.text}</FeedbackBanner>}
        </div>
      )}

      {/* ── Paste Text tab ───────────────────────────────── */}
      {tab === 'upload-text' && (
        <form
          onSubmit={handleTextIngest}
          className="rounded-xl border border-border bg-card/80 p-6 space-y-4"
        >
          <div>
            <p className="text-sm font-medium text-foreground">Ingest plain text</p>
            <p className="text-xs text-muted-foreground mt-1">
              Paste or type content directly. It will be chunked and indexed into Qdrant.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="ingest-title">Title</Label>
              <Input id="ingest-title" name="ingest-title" placeholder="Document title" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ingest-category">Category</Label>
              <Input id="ingest-category" name="ingest-category" placeholder="general" defaultValue="general" />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="ingest-content">Content</Label>
            <textarea
              id="ingest-content"
              name="ingest-content"
              required
              rows={8}
              placeholder="Paste your content here…"
              className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1 resize-y"
            />
          </div>
          {uploadMsg && <FeedbackBanner type={uploadMsg.type}>{uploadMsg.text}</FeedbackBanner>}
          <button
            type="submit"
            disabled={ingestText.isPending}
            className="inline-flex h-9 items-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {ingestText.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            {ingestText.isPending ? 'Indexing…' : 'Index Document'}
          </button>
        </form>
      )}

      {/* ── Document list ────────────────────────────────── */}
      {tab === 'documents' && (
        documents.length === 0 && !showAddForm ? (
          <div className="rounded-lg border border-dashed border-border py-16 text-center space-y-3">
            <FileText className="mx-auto h-10 w-10 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">No documents yet. Add one or upload a file.</p>
          </div>
        ) : (
          <div className="rounded-lg border border-border bg-card overflow-hidden">
            <div className="grid grid-cols-[1fr_100px_80px_110px_72px] gap-4 border-b border-border bg-muted/30 px-4 py-2.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              <span>Title</span>
              <span>Category</span>
              <span>Source</span>
              <span>Updated</span>
              <span />
            </div>

            {documents.map((doc) => (
              <div
                key={doc.id}
                className="border-b border-border last:border-0 hover:bg-muted/10 transition-colors"
              >
                {editingId === doc.id ? (
                  /* Inline edit row */
                  <div className="px-4 py-3 space-y-2">
                    <p className="text-sm font-medium text-foreground">{doc.title}</p>
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      rows={4}
                      className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground outline-none ring-ring focus:ring-1 resize-y"
                    />
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => submitEdit(doc)}
                        disabled={update.isPending}
                        className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground disabled:opacity-50"
                      >
                        {update.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Check className="h-3 w-3" />}
                        Save
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditingId(null)}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  /* Normal row */
                  <div className="grid grid-cols-[1fr_100px_80px_110px_72px] gap-4 items-center px-4 py-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-foreground">{doc.title}</p>
                      <p className="truncate text-xs text-muted-foreground">
                        {doc.content.slice(0, 90)}…
                      </p>
                    </div>
                    <span className="text-xs text-muted-foreground truncate">{doc.category}</span>
                    <span className="text-xs text-muted-foreground truncate">{doc.source}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(doc.updated_at).toLocaleDateString()}
                    </span>
                    <div className="flex items-center justify-end gap-1">
                      <button
                        type="button"
                        onClick={() => startEdit(doc)}
                        title="Edit content"
                        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </button>
                      <button
                        type="button"
                        onClick={() => remove.mutate(doc.id)}
                        disabled={remove.isPending}
                        title="Delete document"
                        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Shared micro-components
// ---------------------------------------------------------------------------

function Label({ htmlFor, children }: { htmlFor: string; children: React.ReactNode }) {
  return (
    <label htmlFor={htmlFor} className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
      {children}
    </label>
  )
}

function Input({ id, name, placeholder, required, defaultValue }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      id={id}
      name={name}
      placeholder={placeholder}
      required={required}
      defaultValue={defaultValue}
      className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1"
    />
  )
}

function ErrorBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
      {children}
    </div>
  )
}

function FeedbackBanner({ type, children }: { type: 'success' | 'error'; children: React.ReactNode }) {
  return (
    <div
      className={`rounded-lg border px-3 py-2.5 text-sm ${
        type === 'success'
          ? 'border-green-500/30 bg-green-500/10 text-green-400'
          : 'border-destructive/30 bg-destructive/10 text-destructive'
      }`}
    >
      {children}
    </div>
  )
}
