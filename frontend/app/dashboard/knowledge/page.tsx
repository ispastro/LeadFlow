'use client'

import { useState } from 'react'
import { useKnowledge, useCreateKnowledge, useDeleteKnowledge } from '@/lib/queries'
import type { KnowledgeDocument } from '@/lib/api'
import { Plus, Trash2, X, Loader2, FileText } from 'lucide-react'

export default function KnowledgePage() {
  const { data, isPending, error } = useKnowledge()
  const create = useCreateKnowledge()
  const remove = useDeleteKnowledge()
  const [showForm, setShowForm] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const documents: KnowledgeDocument[] = data ?? []

  async function handleCreate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setFormError(null)
    const fd = new FormData(e.currentTarget)
    const title = fd.get('title') as string
    const content = fd.get('content') as string
    const category = fd.get('category') as string || 'general'
    const source = (fd.get('source') as string) || 'manual'

    if (!title.trim() || !content.trim()) return

    try {
      await create.mutateAsync({ title: title.trim(), content: content.trim(), category, source })
      setShowForm(false)
      e.currentTarget.reset()
    } catch (err) {
      setFormError((err as Error).message ?? 'Failed to create document')
    }
  }

  async function handleDelete(id: string) {
    try {
      await remove.mutateAsync(id)
    } catch {
      // Mutation error is handled by react-query state
    }
  }

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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-foreground">Knowledge Base</h1>
          <p className="text-sm text-muted-foreground">
            {documents.length} document{documents.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-muted"
        >
          {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showForm ? 'Cancel' : 'Add Document'}
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <form onSubmit={handleCreate} className="space-y-4 rounded-xl border border-border bg-card/80 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="kb-title" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Title
              </label>
              <input
                id="kb-title"
                name="title"
                required
                placeholder="Document title"
                className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="kb-category" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Category
                </label>
                <input
                  id="kb-category"
                  name="category"
                  placeholder="general"
                  defaultValue="general"
                  className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1"
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="kb-source" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Source
                </label>
                <input
                  id="kb-source"
                  name="source"
                  placeholder="manual"
                  defaultValue="manual"
                  className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1"
                />
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <label htmlFor="kb-content" className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Content
            </label>
            <textarea
              id="kb-content"
              name="content"
              required
              rows={6}
              placeholder="Document content…"
              className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1 resize-none"
            />
          </div>
          {formError && (
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {formError}
            </div>
          )}
          <button
            type="submit"
            disabled={create.isPending}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {create.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {create.isPending ? 'Creating…' : 'Create Document'}
          </button>
        </form>
      )}

      {/* Document list */}
      {documents.length === 0 && !showForm ? (
        <div className="rounded-lg border border-dashed border-border py-16 text-center">
          <FileText className="mx-auto h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 text-sm text-muted-foreground">No documents yet. Add one to get started.</p>
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          {/* Header row */}
          <div className="grid grid-cols-[1fr_100px_80px_100px_40px] gap-4 border-b border-border bg-muted/30 px-4 py-2.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            <span>Title</span>
            <span>Category</span>
            <span>Source</span>
            <span>Updated</span>
            <span></span>
          </div>
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="grid grid-cols-[1fr_100px_80px_100px_40px] gap-4 items-center border-b border-border px-4 py-3 last:border-0 hover:bg-muted/20 transition-colors"
            >
              <div className="min-w-0">
                <div className="truncate text-sm font-medium text-foreground">{doc.title}</div>
                <div className="truncate text-xs text-muted-foreground">
                  {doc.content.slice(0, 80)}…
                </div>
              </div>
              <span className="text-xs text-muted-foreground">{doc.category}</span>
              <span className="text-xs text-muted-foreground">{doc.source}</span>
              <span className="text-xs text-muted-foreground">
                {new Date(doc.updated_at).toLocaleDateString()}
              </span>
              <button
                type="button"
                onClick={() => handleDelete(doc.id)}
                disabled={remove.isPending}
                title="Delete document"
                className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
