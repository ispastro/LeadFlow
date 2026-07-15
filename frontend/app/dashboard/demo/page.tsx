'use client'

import { mockLeads } from '@/lib/mock-data'
import { LeadDetailDrawer } from '@/components/dashboard/LeadDetailDrawer'
import { LeadTable } from '@/components/dashboard/LeadTable'

export default function DemoDashboard() {
  // Find the first "Awaiting Approval" lead to show in drawer by default
  const demoLead = mockLeads.find((l) => l.status === 'Awaiting Approval') || mockLeads[0]

  return (
    <div className="space-y-6 px-6 py-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Demo: Drawer View</h1>
        <p className="text-sm text-muted-foreground">
          This page demonstrates the lead detail drawer with the Graph Trace timeline and Action Panel
        </p>
      </div>

      <LeadTable leads={mockLeads} onSelectLead={() => {}} />

      {/* Drawer opened by default showing the first "Awaiting Approval" lead */}
      <LeadDetailDrawer lead={demoLead} isOpen={true} onClose={() => {}} />
    </div>
  )
}
