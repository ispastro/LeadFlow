const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  async getLeads() {
    const response = await fetch(`${API_URL}/api/leads`)
    if (!response.ok) throw new Error('Failed to fetch leads')
    return response.json()
  },

  async getHealth() {
    const response = await fetch(`${API_URL}/health`)
    if (!response.ok) throw new Error('Failed to fetch health')
    return response.json()
  },

  async getKnowledge() {
    const response = await fetch(`${API_URL}/api/knowledge`)
    if (!response.ok) throw new Error('Failed to fetch knowledge')
    return response.json()
  },

  async createKnowledge(data) {
    const response = await fetch(`${API_URL}/api/knowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to create document')
    return response.json()
  },

  async updateKnowledge(id, data) {
    const response = await fetch(`${API_URL}/api/knowledge/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to update document')
    return response.json()
  },

  async deleteKnowledge(id) {
    const response = await fetch(`${API_URL}/api/knowledge/${id}`, {
      method: 'DELETE'
    })
    if (!response.ok) throw new Error('Failed to delete document')
    return response.json()
  },

  async getAnalytics(days = 30) {
    const response = await fetch(`${API_URL}/api/analytics?days=${days}`)
    if (!response.ok) throw new Error('Failed to fetch analytics')
    return response.json()
  }
}
