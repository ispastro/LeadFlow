'use client'

import { useState } from 'react'
import { useAnalytics } from '@/lib/queries'
import { TrendingUp, MessageSquare, Users, Target } from 'lucide-react'

const DAY_OPTIONS = [
  { label: '7 days', value: 7 },
  { label: '30 days', value: 30 },
  { label: '90 days', value: 90 },
]

export default function AnalyticsPage() {
  const [days, setDays] = useState(30)
  const { data, isPending, error } = useAnalytics(days)

  if (isPending) {
    return (
      <div className="space-y-6 px-6 py-6">
        <div className="h-7 w-56 rounded-md bg-muted animate-pulse" />
        <div className="flex gap-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-8 w-20 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
        <div className="grid gap-4 sm:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 rounded-lg border border-border bg-card" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-6 py-6">
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          Failed to load analytics: {(error as Error).message}
        </div>
      </div>
    )
  }

  const overview = data?.overview
  const leadQuality = data?.lead_quality ?? []
  const intentBreakdown = data?.intent_breakdown ?? []
  const timeSeries = data?.time_series

  return (
    <div className="space-y-6 px-6 py-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-foreground">Analytics</h1>
          <p className="text-sm text-muted-foreground">Pipeline performance overview</p>
        </div>
        <div className="flex gap-1 rounded-lg border border-border bg-muted/30 p-1">
          {DAY_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setDays(opt.value)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                days === opt.value
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* KPI cards */}
      {overview && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KPICard
            icon={<MessageSquare className="h-5 w-5" />}
            label="Conversations"
            value={overview.total_conversations}
          />
          <KPICard
            icon={<Users className="h-5 w-5" />}
            label="Leads Captured"
            value={overview.total_leads}
          />
          <KPICard
            icon={<TrendingUp className="h-5 w-5" />}
            label="Conversion Rate"
            value={`${(overview.conversion_rate * 100).toFixed(1)}%`}
          />
          <KPICard
            icon={<Target className="h-5 w-5" />}
            label="Avg. Messages"
            value={overview.avg_messages_per_conversation.toFixed(1)}
          />
        </div>
      )}

      {/* Lead Quality + Intent Breakdown */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Section title="Lead Quality Distribution">
          {leadQuality.length === 0 ? (
            <Empty label="No quality data yet" />
          ) : (
            <div className="space-y-3">
              {leadQuality.map((item) => {
                const max = Math.max(...leadQuality.map((q) => q.count), 1)
                return (
                  <BarRow key={item.quality} label={item.quality} value={item.count} max={max} />
                )
              })}
            </div>
          )}
        </Section>

        <Section title="Intent Breakdown">
          {intentBreakdown.length === 0 ? (
            <Empty label="No intent data yet" />
          ) : (
            <div className="space-y-3">
              {intentBreakdown.map((item) => {
                const max = Math.max(...intentBreakdown.map((i) => i.count), 1)
                return (
                  <BarRow key={item.intent} label={item.intent} value={item.count} max={max} />
                )
              })}
            </div>
          )}
        </Section>
      </div>

      {/* Time Series */}
      {timeSeries && (
        <Section title="Daily Activity">
          {timeSeries.conversations.length === 0 && timeSeries.leads.length === 0 ? (
            <Empty label="No time series data yet" />
          ) : (
            <div className="overflow-x-auto">
              <div className="flex items-end gap-1 min-h-[160px] pb-6">
                {timeSeries.conversations.map((entry, i) => {
                  const leadsEntry = timeSeries.leads.find((l) => l.date === entry.date)
                  const convCount = entry.count
                  const leadCount = leadsEntry?.count ?? 0
                  const maxCount = Math.max(...timeSeries.conversations.map((c) => c.count), 1)
                  return (
                    <div key={entry.date} className="flex flex-col items-center gap-1 flex-1 min-w-[24px]">
                      <div className="flex items-end gap-px h-[120px]">
                        <div
                          title={`${convCount} conversations`}
                          className="w-2.5 rounded-t-sm bg-primary/60 transition-all"
                          style={{ height: `${(convCount / maxCount) * 100}%` }}
                        />
                        <div
                          title={`${leadCount} leads`}
                          className="w-2.5 rounded-t-sm bg-green-500/60 transition-all"
                          style={{ height: `${(leadCount / maxCount) * 100}%` }}
                        />
                      </div>
                      <span className="text-[9px] text-muted-foreground whitespace-nowrap -rotate-45 origin-top-left translate-x-1">
                        {new Date(entry.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                  )
                })}
              </div>
              <div className="flex gap-4 justify-center pt-2">
                <Legend color="bg-primary/60" label="Conversations" />
                <Legend color="bg-green-500/60" label="Leads" />
              </div>
            </div>
          )}
        </Section>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Shared sub-components
// ---------------------------------------------------------------------------

function KPICard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4 space-y-2">
      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}
        <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
      </div>
      <div className="text-2xl font-bold text-foreground">{value}</div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4 space-y-4">
      <h2 className="text-sm font-semibold text-foreground">{title}</h2>
      {children}
    </div>
  )
}

function BarRow({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = Math.max((value / max) * 100, 2) // min 2% so zero values still show
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium text-foreground">{value}</span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div
          className="h-2 rounded-full bg-primary/70 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
      <div className={`h-2.5 w-2.5 rounded-sm ${color}`} />
      {label}
    </div>
  )
}

function Empty({ label }: { label: string }) {
  return <p className="text-sm text-muted-foreground text-center py-4">{label}</p>
}
