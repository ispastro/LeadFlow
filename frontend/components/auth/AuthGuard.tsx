'use client'

import { type ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/lib/auth'
import { useCurrentUser } from '@/lib/queries'

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter()
  const hasToken = isAuthenticated()
  const { isLoading, isError } = useCurrentUser()

  // No token at all → straight to login. A token that fails server validation
  // (401) is cleared + redirected by the global handler, but guard against it
  // here too so a broken session never flashes protected UI.
  if (!hasToken || isError) {
    if (typeof window !== 'undefined') router.replace('/login')
    return <FullScreenSpinner />
  }

  if (isLoading) return <FullScreenSpinner />

  return <>{children}</>
}

function FullScreenSpinner() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-muted-foreground/30 border-t-foreground" />
    </div>
  )
}
