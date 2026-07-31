'use client'

import { LogOut } from 'lucide-react'
import { useLeadsPendingApproval, useCurrentUser, useLogout } from '@/lib/queries'

export function Header() {
  const { total: pendingCount } = useLeadsPendingApproval()
  const { data: user } = useCurrentUser()
  const logout = useLogout()

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-sm">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-xs font-bold">LF</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground">LeadFlow RevOps</h1>
            <p className="text-xs text-muted-foreground">Agent Supervisor Dashboard</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {pendingCount > 0 && (
            <div className="flex items-center gap-2 rounded-full bg-orange-500/10 border border-orange-500/20 px-3 py-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-orange-400 animate-pulse" />
              <span className="text-xs font-medium text-orange-400">
                {pendingCount} pending approval
              </span>
            </div>
          )}

          {user?.email && (
            <span className="hidden text-xs font-medium text-muted-foreground sm:inline">
              {user.email}
            </span>
          )}

          <button
            type="button"
            onClick={() => logout.mutate()}
            disabled={logout.isPending}
            title="Sign out"
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:opacity-50"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Sign out</span>
          </button>
        </div>
      </div>
    </header>
  )
}
