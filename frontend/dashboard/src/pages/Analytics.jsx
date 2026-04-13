import { useState, useEffect } from 'react'
import { api } from '../services/api'

function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    loadAnalytics()
  }, [days])

  const loadAnalytics = async () => {
    setLoading(true)
    try {
      const analyticsData = await api.getAnalytics(days)
      setData(analyticsData)
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-6xl">
        <div className="mb-8">
          <div className="h-8 w-48 bg-neutral-800 rounded skeleton mb-2"></div>
          <div className="h-4 w-64 bg-neutral-800 rounded skeleton"></div>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
              <div className="h-4 w-24 bg-neutral-800 rounded skeleton mb-3"></div>
              <div className="h-10 w-20 bg-neutral-800 rounded skeleton"></div>
            </div>
          ))}
        </div>

        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 mb-8">
          <div className="h-6 w-32 bg-neutral-800 rounded skeleton mb-6"></div>
          <div className="h-64 bg-neutral-800 rounded skeleton"></div>
        </div>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="max-w-6xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold mb-1 text-white">Analytics</h1>
          <p className="text-sm text-neutral-400">Performance metrics and insights</p>
        </div>
        
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-4 py-2 bg-neutral-900 border border-neutral-800 rounded-lg text-white text-sm focus:outline-none focus:ring-1 focus:ring-neutral-600"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 hover:border-neutral-700 transition-colors">
          <p className="text-sm text-neutral-400 mb-1">Conversations</p>
          <p className="text-3xl font-semibold text-white">{data.overview.total_conversations}</p>
        </div>
        
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 hover:border-neutral-700 transition-colors">
          <p className="text-sm text-neutral-400 mb-1">Leads Captured</p>
          <p className="text-3xl font-semibold text-white">{data.overview.total_leads}</p>
        </div>
        
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 hover:border-neutral-700 transition-colors">
          <p className="text-sm text-neutral-400 mb-1">Conversion Rate</p>
          <p className="text-3xl font-semibold text-white">{data.overview.conversion_rate}%</p>
        </div>
        
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 hover:border-neutral-700 transition-colors">
          <p className="text-sm text-neutral-400 mb-1">Avg Messages</p>
          <p className="text-3xl font-semibold text-white">{data.overview.avg_messages_per_conversation}</p>
        </div>
      </div>

      {/* Time Series Chart Placeholder */}
      <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 mb-8">
        <h2 className="text-lg font-semibold mb-6 text-white">Activity Over Time</h2>
        <div className="h-64 flex items-center justify-center text-neutral-500 text-sm">
          Chart coming soon
        </div>
      </div>

      {/* Lead Quality & Intent */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-white">Lead Quality</h2>
          <div className="space-y-3">
            {data.lead_quality.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b border-neutral-800 last:border-0">
                <span className="text-sm text-neutral-400">{item.quality}</span>
                <span className="text-sm font-medium text-white">{item.count}</span>
              </div>
            ))}
            {data.lead_quality.length === 0 && (
              <p className="text-sm text-neutral-500 text-center py-4">No data yet</p>
            )}
          </div>
        </div>

        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-white">Intent Breakdown</h2>
          <div className="space-y-3">
            {data.intent_breakdown.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b border-neutral-800 last:border-0">
                <span className="text-sm text-neutral-400">{item.intent.replace(/_/g, ' ')}</span>
                <span className="text-sm font-medium text-white">{item.count}</span>
              </div>
            ))}
            {data.intent_breakdown.length === 0 && (
              <p className="text-sm text-neutral-500 text-center py-4">No data yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics
