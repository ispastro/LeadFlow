import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError('Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#171717_1px,transparent_1px),linear-gradient(to_bottom,#171717_1px,transparent_1px)] bg-[size:50px_50px] opacity-30"></div>
      
      {/* Radial gradient overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.05),transparent_50%)]"></div>

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-white mb-2" style={{ fontFamily: 'Poppins, sans-serif' }}>
            <span style={{ fontWeight: 500 }}>Lead</span>
            <span style={{ fontWeight: 600, letterSpacing: '-0.02em' }}>Flow</span>
          </h1>
          <p className="text-sm text-neutral-400">Sign in to your dashboard</p>
        </div>

        <div className="bg-black/40 backdrop-blur-sm border border-neutral-800/50 rounded-lg p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-neutral-900/50 border border-neutral-800 rounded-md focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-transparent text-white placeholder-neutral-500"
                placeholder="admin@leadflow.com"
                required
                autoFocus
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-400 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-neutral-900/50 border border-neutral-800 rounded-md focus:outline-none focus:ring-2 focus:ring-white/20 focus:border-transparent text-white placeholder-neutral-500"
                placeholder="••••••••"
                required
              />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-md p-3">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-3 bg-white text-black font-medium rounded-md hover:bg-neutral-200 disabled:bg-neutral-700 disabled:text-neutral-400 transition-colors"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-neutral-800/50">
            <p className="text-xs text-neutral-500 text-center">
              Default: admin@leadflow.com / admin123
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
