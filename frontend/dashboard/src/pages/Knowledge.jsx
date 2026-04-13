import { useState, useEffect } from 'react'
import { api } from '../services/api'

function Knowledge() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingDoc, setEditingDoc] = useState(null)
  const [formData, setFormData] = useState({ content: '', source: '', category: 'general' })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const data = await api.getKnowledge()
      setDocuments(data.documents || [])
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)

    try {
      if (editingDoc) {
        await api.updateKnowledge(editingDoc.id, formData)
      } else {
        await api.createKnowledge(formData)
      }
      
      setFormData({ content: '', source: '', category: 'general' })
      setShowForm(false)
      setEditingDoc(null)
      await loadDocuments()
    } catch (error) {
      console.error('Failed to save document:', error)
      alert('Failed to save document')
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = (doc) => {
    setEditingDoc(doc)
    setFormData({
      content: doc.content,
      source: doc.source,
      category: doc.metadata?.category || 'general'
    })
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await api.deleteKnowledge(id)
      await loadDocuments()
    } catch (error) {
      console.error('Failed to delete document:', error)
      alert('Failed to delete document')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingDoc(null)
    setFormData({ content: '', source: '', category: 'general' })
  }

  if (loading) {
    return (
      <div className="max-w-6xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <div className="h-8 w-48 bg-neutral-800 rounded skeleton mb-2"></div>
            <div className="h-4 w-64 bg-neutral-800 rounded skeleton"></div>
          </div>
          <div className="h-10 w-32 bg-neutral-800 rounded skeleton"></div>
        </div>

        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-neutral-900 border border-neutral-800 rounded-lg p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="h-5 w-32 bg-neutral-800 rounded skeleton"></div>
                    <div className="h-5 w-16 bg-neutral-800 rounded skeleton"></div>
                  </div>
                  <div className="h-4 w-full bg-neutral-800 rounded skeleton mb-2"></div>
                  <div className="h-4 w-3/4 bg-neutral-800 rounded skeleton mb-3"></div>
                  <div className="h-3 w-24 bg-neutral-800 rounded skeleton"></div>
                </div>
                <div className="flex gap-2 ml-4">
                  <div className="h-8 w-12 bg-neutral-800 rounded skeleton"></div>
                  <div className="h-8 w-16 bg-neutral-800 rounded skeleton"></div>
                </div>
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
          <h1 className="text-2xl font-semibold mb-1 text-white">Knowledge Base</h1>
          <p className="text-sm text-neutral-400">Manage your AI's knowledge</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-white text-black text-sm font-medium rounded-md hover:bg-neutral-200 transition-colors"
        >
          Add Document
        </button>
      </div>

      {showForm && (
        <div className="mb-6 bg-neutral-900 border border-neutral-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4 text-white">
            {editingDoc ? 'Edit Document' : 'New Document'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-2">Title</label>
              <input
                type="text"
                value={formData.source}
                onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                className="w-full px-3 py-2 bg-black border border-neutral-800 rounded-md focus:outline-none focus:ring-2 focus:ring-white focus:border-transparent text-sm text-white"
                placeholder="e.g., Pricing Information"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-2">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 bg-black border border-neutral-800 rounded-md focus:outline-none focus:ring-2 focus:ring-white focus:border-transparent text-sm text-white"
              >
                <option value="general">General</option>
                <option value="pricing">Pricing</option>
                <option value="features">Features</option>
                <option value="company">Company</option>
                <option value="faq">FAQ</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-2">Content</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="w-full px-3 py-2 bg-black border border-neutral-800 rounded-md focus:outline-none focus:ring-2 focus:ring-white focus:border-transparent text-sm text-white h-32"
                placeholder="Enter the knowledge content..."
                required
              />
            </div>
            <div className="flex gap-2 pt-2">
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-white text-black text-sm font-medium rounded-md hover:bg-neutral-200 disabled:bg-neutral-700 disabled:text-neutral-400 transition-colors"
              >
                {saving ? 'Saving...' : (editingDoc ? 'Update' : 'Create')}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 bg-neutral-800 text-white text-sm font-medium rounded-md hover:bg-neutral-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {documents.length === 0 ? (
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-12 text-center">
          <p className="text-sm text-neutral-400 mb-2">No documents yet</p>
          <p className="text-xs text-neutral-500 mb-4">Add your first knowledge base document</p>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-white text-black text-sm font-medium rounded-md hover:bg-neutral-200 transition-colors"
          >
            Add Document
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <div key={doc.id} className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 hover:border-neutral-700 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-base font-semibold text-white">{doc.source}</h3>
                    <span className="px-2 py-0.5 text-xs font-medium bg-neutral-800 text-neutral-400 rounded border border-neutral-700">
                      {doc.metadata?.category || 'general'}
                    </span>
                  </div>
                  <p className="text-sm text-neutral-400 line-clamp-2">{doc.content}</p>
                  {doc.created_at && (
                    <p className="text-xs text-neutral-500 mt-2">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => handleEdit(doc)}
                    className="px-3 py-1.5 text-xs font-medium text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-md transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="px-3 py-1.5 text-xs font-medium text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-md transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Knowledge
