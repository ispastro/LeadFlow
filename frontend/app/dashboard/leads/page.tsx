'use client'

import { useMemo, useState } from 'react'
import type { Lead } from '@/lib/api'
import { useLeads } from '@/lib/queries'
import { LeadTable } from '@/components/dashboard/LeadTable'
import { LeadDetailDrawer } from '@/components/dashboard/LeadDetailDrawer'
import { Search } from 'lucide-react'

type StatusFilter = 'all' | 'pending' | 'manual_review' | 'approved'

const STATUS_TABS: { label: string; value: StatusFilter }[] = [
  { label: 'All', value: 'all' },
  { label: 'Pending Approval', value: 'pending' },
  { label: 'Manual Review', value: 'manual_review' },
  { label: 'Approved', value: 'approved' },
]

export default function LeadsPage() {
  const { data, isPending, error } = useLeads()
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')

  const leads = data?.leads ?? []

  const filtered = useMemo(() => {
    let result = leads

    // Status filter
    if (statusFilter === 'pending') {
      result = result.filter((l) => l.metadata?.requires_human_approval && l.metadata.human_approved == null)
    } else if (statusFilter === 'manual_review') {
      result = result.filter((l) => l.metadata?.is_manual_review)
    } else if (statusFilter === 'approved') {
      result = result.filter((l) => l.metadata?.human_approved === true)
    }

    // Search filter (email or name, case-insensitive)
    if (search.trim()) {
      const q = search.toLowerCase()
      result = result.filter(
        (l) =>
          l.email?.toLowerCase().includes(q) ||
          l.name?.toLowerCase().includes(q),
      )
    }

    return result
  }, [leads, search, statusFilter])

  const handleSelectLead = (lead: Lead) => {
    setSelectedLead(lead)
    setIsDrawerOpen(true)
  }

  if (isPending) {
    return (
      <div className="space-y-6 px-6 py-6">
        <div className="space-y-1">
          <div className="h-7 w-48 rounded-md bg-muted animate-pulse" />
          <div className="h-4 w-64 rounded-md bg-muted animate-pulse" />
        </div>
        <div className="h-10 w-72 rounded-lg bg-muted animate-pulse" />
        <div className="flex gap-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-8 w-24 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex gap-4 px-6 py-4 border-b border-border last:border-0">
              <div className="h-4 w-40 rounded bg-muted animate-pulse" />
              <div className="h-4 w-32 rounded bg-muted animate-pulse" />
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
          Failed to load leads: {(error as Error).message}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 px-6 py-6">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Leads</h1>
        <p className="text-sm text-muted-foreground">
          {leads.length} lead{leads.length !== 1 ? 's' : ''} total · {filtered.length} shown
        </p>
      </div>

      {/* Search + Filter */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full max-w-xs">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search by name or email…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-border bg-background pl-9 pr-3 py-2 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1"
          />
        </div>

        <div className="flex gap-1 rounded-lg border border-border bg-muted/30 p-1">
          {STATUS_TABS.map((tab) => (
            <button
              key={tab.value}
              onClick={() => setStatusFilter(tab.value)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                statusFilter === tab.value
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <LeadTable leads={filtered} onSelectLead={handleSelectLead} />

      {/* Drawer */}
      <LeadDetailDrawer
        lead={selectedLead}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  )
}
