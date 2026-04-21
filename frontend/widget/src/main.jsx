import React from 'react'
import ReactDOM from 'react-dom/client'
import Widget from './Widget'
import './index.css'

window.LeadFlowWidget = {
  init: function(config = {}) {
    const container = document.createElement('div')
    container.id = 'leadflow-widget-container'
    document.body.appendChild(container)

    const root = ReactDOM.createRoot(container)
    root.render(
      <React.StrictMode>
        <Widget apiUrl={config.apiUrl || import.meta.env.VITE_API_URL || 'http://localhost:8000'} />
      </React.StrictMode>
    )
  },
  open: function() {
    // Trigger chat window to open
    const event = new CustomEvent('leadflow-open-chat')
    window.dispatchEvent(event)
  }
}

// Auto-initialize in dev mode
if (import.meta.env.DEV) {
  window.LeadFlowWidget.init()
}

// Auto-initialize in production too
if (typeof window !== 'undefined') {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      if (!document.getElementById('leadflow-widget-container')) {
        window.LeadFlowWidget.init()
      }
    })
  } else {
    // DOM already loaded
    if (!document.getElementById('leadflow-widget-container')) {
      window.LeadFlowWidget.init()
    }
  }
}
