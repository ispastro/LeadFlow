import { useState, useEffect } from 'react'
import { api } from '../services/api'

function Leads() {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadLeads()
  }, [])

  const loadLeads = async () => {
    try {
      const data = await api.getLeads()
      setLeads(data.leads || [])
    } catch (error) {
      console.error('Failed to load leads:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="max-w-6xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <div className="h-8 w-32 bg-neutral-800 rounded skeleton mb-2"></div>
            <div className="h-4 w-48 bg-neutral-800 rounded skeleton"></div>
          </div>
          <div className="h-10 w-24 bg-neutral-800 rounded skeleton"></div>
        </div>

        <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-hidden">
          <div className="border-b border-neutral-800 p-4">
            <div className="grid grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-4 bg-neutral-800 rounded skeleton"></div>
              ))}
            </div>
          </div>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="p-4 border-b border-neutral-800">
              <div className="grid grid-cols-4 gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-neutral-800 rounded-full skeleton"></div>
                  <div className="h-4 w-24 bg-neutral-800 rounded skeleton"></div>
                </div>
                <div className="h-4 bg-neutral-800 rounded skeleton"></div>
                <div className="h-4 w-20 bg-neutral-800 rounded skeleton"></div>
                <div className="h-4 w-24 bg-neutral-800 rounded skeleton"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold mb-1 text-white">Leads</h1>
          <p className="text-sm text-neutral-400">{leads.length} total leads</p>
        </div>
        <button className="px-4 py-2 bg-white text-black text-sm font-medium rounded-md hover:bg-neutral-200 transition-colors">
          Export
        </button>
      </div>

      {leads.length === 0 ? (
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-12 text-center">
          <p className="text-sm text-neutral-400">No leads yet</p>
          <p className="text-xs text-neutral-500 mt-1">Leads will appear here once visitors chat with your AI</p>
        </div>
      ) : (
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="border-b border-neutral-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-400">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-400">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-400">Intent</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-400">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-800">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-neutral-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center text-black text-xs font-medium">
                        {(lead.name || lead.email).charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm font-medium text-white">{lead.name || 'Anonymous'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-400">{lead.email}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${
                      lead.intent === 'HIGH_INTEREST' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                      lead.intent === 'READY_TO_BUY' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
                      'bg-neutral-800 text-neutral-400 border border-neutral-700'
                    }`}>
                      {lead.intent || 'Unknown'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-500">{formatDate(lead.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Leads
