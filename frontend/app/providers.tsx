'use client'

import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState, useEffect, type ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { UNAUTHORIZED_EVENT } from '@/lib/api'

/**
 * Listens for the global 401 event fired by the API client. When a request is
 * rejected as unauthorized, clears the React Query cache and redirects to
 * /login — unless we're already there (e.g. a wrong-password attempt should
 * surface an inline error, not a redirect).
 */
function AuthSync() {
  const qc = useQueryClient()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    function onUnauthorized() {
      if (pathname === '/login') return
      qc.clear()
      router.replace('/login')
    }
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized)
  }, [qc, router, pathname])

  return null
}

export function Providers({ children }: { children: ReactNode }) {
  // useState ensures each browser tab gets its own QueryClient instance
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Data is considered fresh for 10s before a background refetch
            staleTime: 10_000,
            // Retry failed requests once before showing an error
            retry: 1,
            refetchOnWindowFocus: true,
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>
      <AuthSync />
      {children}
      {/* DevTools only render in development — tree-shaken in production build */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
