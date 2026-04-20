const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

export const api = {
  async login(email, password) {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    if (!response.ok) throw new Error('Invalid credentials')
    return response.json()
  },

  async getMe() {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      headers: getAuthHeaders()
    })
    if (!response.ok) throw new Error('Unauthorized')
    return response.json()
  },

  async getLeads() {
    const response = await fetch(`${API_URL}/api/leads`, {
      headers: getAuthHeaders()
    })
    if (!response.ok) throw new Error('Failed to fetch leads')
    return response.json()
  },

  async getHealth() {
    const response = await fetch(`${API_URL}/health`)
    if (!response.ok) throw new Error('Failed to fetch health')
    return response.json()
  },

  async getKnowledge() {
    const response = await fetch(`${API_URL}/api/knowledge`, {
      headers: getAuthHeaders()
    })
    if (!response.ok) throw new Error('Failed to fetch knowledge')
    return response.json()
  },

  async createKnowledge(data) {
    const response = await fetch(`${API_URL}/api/knowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to create document')
    return response.json()
  },

  async updateKnowledge(id, data) {
    const response = await fetch(`${API_URL}/api/knowledge/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data)
    })
    if (!response.ok) throw new Error('Failed to update document')
    return response.json()
  },

  async deleteKnowledge(id) {
    const response = await fetch(`${API_URL}/api/knowledge/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    if (!response.ok) throw new Error('Failed to delete document')
    return response.json()
  },

  async getAnalytics(days = 30) {
    const response = await fetch(`${API_URL}/api/analytics?days=${days}`, {
      headers: getAuthHeaders()
    })
    if (!response.ok) throw new Error('Failed to fetch analytics')
    return response.json()
  },

  async getConversations() {
    const response = await fetch(`${API_URL}/api/conversations`, {
      headers: getAuthHeaders()
    })
    if (!response.ok) throw new Error('Failed to fetch conversations')
    return response.json()
  },

  async getConversation(id) {
    const response = await fetch(`${API_URL}/api/conversations/${id}`, {
      headers: getAuthHeaders()
    })
    if (!response.ok) throw new Error('Failed to fetch conversation')
    return response.json()
  }
}
