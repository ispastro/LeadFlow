function ChatBubble({ isOpen, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-14 h-14 rounded-full bg-white hover:bg-neutral-100 text-black transition-all duration-200 flex items-center justify-center border border-neutral-200 hover:border-neutral-300"
      aria-label="Toggle chat"
    >
      {isOpen ? (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      )}
    </button>
  )
}

export default ChatBubble
