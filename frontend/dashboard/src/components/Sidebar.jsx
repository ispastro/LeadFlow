import { Link, useLocation } from 'react-router-dom'

function Sidebar() {
  const location = useLocation()

  const links = [
    { path: '/', label: 'Overview' },
    { path: '/leads', label: 'Leads' },
    { path: '/conversations', label: 'Conversations' },
    { path: '/knowledge', label: 'Knowledge' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/settings', label: 'Settings' }
  ]

  return (
    <div className="w-64 h-screen fixed left-0 top-0 bg-black border-r border-neutral-800">
      <div className="h-16 flex items-center px-6 border-b border-neutral-800">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-white rounded-md flex items-center justify-center">
            <span className="text-black text-xs font-bold">L</span>
          </div>
          <span className="font-semibold text-sm text-white">LeadFlow</span>
        </div>
      </div>

      <nav className="p-4">
        {links.map(link => (
          <Link
            key={link.path}
            to={link.path}
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
  )
}

export default Sidebar
