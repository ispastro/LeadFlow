'use client'

import { useState } from 'react'
import type { Lead } from '@/lib/api'
import { useLeads } from '@/lib/queries'
import { LeadTable } from '@/components/dashboard/LeadTable'
import { LeadDetailDrawer } from '@/components/dashboard/LeadDetailDrawer'

export default function DashboardPage() {
  const { data, isPending, error } = useLeads()
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const handleSelectLead = (lead: Lead) => {
    setSelectedLead(lead)
    setIsDrawerOpen(true)
  }

  if (isPending) {
    return (
      <div className="space-y-6 px-6 py-6">
        <div className="space-y-1">
          <div className="h-7 w-40 rounded-md bg-muted animate-pulse" />
          <div className="h-4 w-64 rounded-md bg-muted animate-pulse" />
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

  const leads = data?.leads ?? []

  return (
    <div className="space-y-6 px-6 py-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Active Leads</h1>
        <p className="text-sm text-muted-foreground">
          {leads.length} lead{leads.length !== 1 ? 's' : ''} in the qualification pipeline
        </p>
      </div>

      <LeadTable leads={leads} onSelectLead={handleSelectLead} />

      <LeadDetailDrawer
        lead={selectedLead}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  )
}
