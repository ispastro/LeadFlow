function Conversations() {
  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-semibold mb-4 text-white">Conversations</h1>
      <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-12 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-neutral-800 flex items-center justify-center">
          <svg className="w-8 h-8 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">Coming Soon</h3>
        <p className="text-sm text-neutral-400">View and manage all customer conversations here.</p>
      </div>
    </div>
  )
}

export default Conversations
