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
        <Widget apiUrl={config.apiUrl || 'http://localhost:8000'} />
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
