import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Leads from './pages/Leads'
import Conversations from './pages/Conversations'
import Knowledge from './pages/Knowledge'
import Settings from './pages/Settings'
import Analytics from './pages/Analytics'

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-black relative">
        <Sidebar />
        <main className="ml-64 flex-1 p-12 relative z-10">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/leads" element={<Leads />} />
            <Route path="/conversations" element={<Conversations />} />
            <Route path="/knowledge" element={<Knowledge />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
