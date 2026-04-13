import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'

function Sidebar() {
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)

  const links = [
    { path: '/', label: 'Overview' },
    { path: '/leads', label: 'Leads' },
    { path: '/conversations', label: 'Conversations' },
    { path: '/knowledge', label: 'Knowledge' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/settings', label: 'Settings' }
  ]

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 w-10 h-10 bg-neutral-900 border border-neutral-800 rounded-md flex items-center justify-center text-white"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {isOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed left-0 top-0 h-screen bg-black border-r border-neutral-800 z-40 transition-transform duration-300
        w-64
        lg:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="h-16 flex items-center px-6 border-b border-neutral-800">
          <div className="flex items-center gap-2">
            <img src="/leadflow.png" alt="LeadFlow" className="w-6 h-6 rounded-md" />
            <span className="font-semibold text-sm text-white" style={{ fontFamily: 'Poppins, sans-serif' }}>
              <span className="font-medium">Lead</span>
              <span className="font-semibold" style={{ letterSpacing: '-0.02em' }}>Flow</span>
            </span>
          </div>
        </div>

        <nav className="p-4">
          {links.map(link => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setIsOpen(false)}
              className={`block px-3 py-2 text-sm rounded-md mb-1 transition-colors ${
                location.pathname === link.path
                  ? 'bg-neutral-800 text-white font-medium'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </>
  )
}

export default Sidebar
