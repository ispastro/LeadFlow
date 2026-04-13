import { useState, useEffect } from 'react'
import { api } from '../services/api'

function Dashboard() {
  const [stats, setStats] = useState({
    totalLeads: 0,
    totalConversations: 0,
    conversionRate: 0
  })
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [leadsData, healthData] = await Promise.all([
        api.getLeads(),
        api.getHealth()
      ])
      
      setStats({
        totalLeads: leadsData.leads?.length || 0,
        totalConversations: leadsData.total || 0,
        conversionRate: leadsData.leads?.length > 0 ? 
          ((leadsData.leads.length / leadsData.total) * 100).toFixed(1) : 0
      })
      setHealth(healthData)
    } catch (error) {
      console.error('Failed to load data:', error)
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

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
              <div className="h-4 w-24 bg-neutral-800 rounded skeleton mb-3"></div>
              <div className="h-10 w-20 bg-neutral-800 rounded skeleton mb-3"></div>
              <div className="h-3 w-32 bg-neutral-800 rounded skeleton"></div>
            </div>
          ))}
        </div>

        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
          <div className="h-6 w-32 bg-neutral-800 rounded skeleton mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between py-2">
                <div className="h-4 w-24 bg-neutral-800 rounded skeleton"></div>
                <div className="h-4 w-16 bg-neutral-800 rounded skeleton"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold mb-1 text-white">Overview</h1>
        <p className="text-sm text-neutral-400">Welcome back to LeadFlow</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 hover:border-neutral-700 transition-colors">
          <p className="text-sm text-neutral-400 mb-1">Total Leads</p>
          <p className="text-3xl font-semibold text-white">{stats.totalLeads}</p>
          <p className="text-xs text-neutral-500 mt-2">↑ 12% from last month</p>
        </div>
        
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 hover:border-neutral-700 transition-colors">
          <p className="text-sm text-neutral-400 mb-1">Conversations</p>
          <p className="text-3xl font-semibold text-white">{stats.totalConversations}</p>
          <p className="text-xs text-neutral-500 mt-2">↑ 8% from last month</p>
        </div>
        
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 hover:border-neutral-700 transition-colors">
          <p className="text-sm text-neutral-400 mb-1">Conversion Rate</p>
          <p className="text-3xl font-semibold text-white">{stats.conversionRate}%</p>
          <p className="text-xs text-neutral-500 mt-2">↑ 3% from last month</p>
        </div>
      </div>

      {health && (
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-white">System Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-neutral-800">
              <span className="text-sm text-neutral-400">API Status</span>
              <span className="text-sm font-medium text-green-500">{health.status}</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-neutral-800">
              <span className="text-sm text-neutral-400">Database</span>
              <span className="text-sm font-medium text-green-500">Connected</span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-neutral-400">AI Model</span>
              <span className="text-sm font-medium text-green-500">Active</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
