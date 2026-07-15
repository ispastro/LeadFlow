'use client'

import { useState } from 'react'
import { mockLeads } from '@/lib/mock-data'
import type { Lead } from '@/types/dashboard'
import { LeadTable } from '@/components/dashboard/LeadTable'
import { LeadDetailDrawer } from '@/components/dashboard/LeadDetailDrawer'

export default function DashboardPage() {
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const handleSelectLead = (lead: Lead) => {
    setSelectedLead(lead)
    setIsDrawerOpen(true)
  }

  const handleCloseDrawer = () => {
    setIsDrawerOpen(false)
    // Keep the selected lead in state in case they reopen
  }

  return (
    <div className="space-y-6 px-6 py-6">
      {/* Page Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Active Leads</h1>
        <p className="text-sm text-muted-foreground">
          Manage and review {mockLeads.length} leads in the qualification pipeline
        </p>
      </div>

      {/* Leads Table */}
      <LeadTable leads={mockLeads} onSelectLead={handleSelectLead} />

      {/* Lead Detail Drawer */}
      <LeadDetailDrawer
        lead={selectedLead}
        isOpen={isDrawerOpen}
        onClose={handleCloseDrawer}
      />
    </div>
  )
}
