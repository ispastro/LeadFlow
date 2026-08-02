'use client'

import { useState } from 'react'
import { MessageSquare, Users, TrendingUp, Clock } from 'lucide-react'
import type { Lead } from '@/lib/api'
import { useLeads, useAnalytics, useLeadsPendingApproval } from '@/lib/queries'
import { LeadTable } from '@/components/dashboard/LeadTable'
import { LeadDetailDrawer } from '@/components/dashboard/LeadDetailDrawer'

export default function DashboardPage() {
  const { data: leadsData, isPending: leadsPending, error: leadsError } = useLeads()
  const { data: analytics, isPending: analyticsPending } = useAnalytics(30)
  const { total: pendingCount } = useLeadsPendingApproval()
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const handleSelectLead = (lead: Lead) => {
    setSelectedLead(lead)
    setIsDrawerOpen(true)
  }

  const leads = leadsData?.leads ?? []
  const overview = analytics?.overview

  if (leadsPending) {
    return (
      <div className="space-y-6 px-6 py-6">
        <div className="space-y-1">
          <div className="h-7 w-40 rounded-md bg-muted animate-pulse" />
          <div className="h-4 w-64 rounded-md bg-muted animate-pulse" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 rounded-lg border border-border bg-card animate-pulse" />
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

  if (leadsError) {
    return (
      <div className="px-6 py-6">
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          Failed to load leads: {(leadsError as Error).message}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 px-6 py-6">
      {/* Page header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-foreground">Overview</h1>
        <p className="text-sm text-muted-foreground">
          Live pipeline — last 30 days
        </p>
      </div>

      {/* KPI bar */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          icon={<Users className="h-5 w-5" />}
          label="Total Leads"
          value={analyticsPending ? '…' : String(overview?.total_leads ?? leads.length)}
          sub="captured in pipeline"
          accent="blue"
        />
        <KPICard
          icon={<MessageSquare className="h-5 w-5" />}
          label="Conversations"
          value={analyticsPending ? '…' : String(overview?.total_conversations ?? '—')}
          sub="unique sessions"
          accent="purple"
        />
        <KPICard
          icon={<TrendingUp className="h-5 w-5" />}
          label="Conversion Rate"
          value={
            analyticsPending
              ? '…'
              : overview
                ? `${(overview.conversion_rate * 100).toFixed(1)}%`
                : '—'
          }
          sub="visitor → lead"
          accent="green"
        />
        <KPICard
          icon={<Clock className="h-5 w-5" />}
          label="Pending Approval"
          value={String(pendingCount)}
          sub="awaiting HITL review"
          accent={pendingCount > 0 ? 'orange' : 'default'}
          pulse={pendingCount > 0}
        />
      </div>

      {/* Lead table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">
            Recent Leads
          </h2>
          <a
            href="/dashboard/leads"
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            View all →
          </a>
        </div>
        <LeadTable
          leads={leads.slice(0, 10)}
          onSelectLead={handleSelectLead}
        />
      </div>

      <LeadDetailDrawer
        lead={selectedLead}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  )
}

// ---------------------------------------------------------------------------
// KPI Card
// ---------------------------------------------------------------------------

type Accent = 'blue' | 'purple' | 'green' | 'orange' | 'default'

const accentClasses: Record<Accent, { icon: string; value: string }> = {
  blue:    { icon: 'text-blue-400',   value: 'text-blue-400'   },
  purple:  { icon: 'text-purple-400', value: 'text-purple-400' },
  green:   { icon: 'text-green-400',  value: 'text-green-400'  },
  orange:  { icon: 'text-orange-400', value: 'text-orange-400' },
  default: { icon: 'text-muted-foreground', value: 'text-foreground' },
}

function KPICard({
  icon,
  label,
  value,
  sub,
  accent = 'default',
  pulse = false,
}: {
  icon: React.ReactNode
  label: string
  value: string
  sub: string
  accent?: Accent
  pulse?: boolean
}) {
  const cls = accentClasses[accent]
  return (
    <div className="rounded-lg border border-border bg-card p-4 space-y-3">
      <div className={`flex items-center gap-2 ${cls.icon}`}>
        {icon}
        <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </span>
        {pulse && (
          <span className="ml-auto h-2 w-2 rounded-full bg-orange-400 animate-pulse" />
        )}
      </div>
      <div className={`text-2xl font-bold ${cls.value}`}>{value}</div>
      <p className="text-xs text-muted-foreground">{sub}</p>
    </div>
  )
}
