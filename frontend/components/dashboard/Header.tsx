'use client'

import { LogOut, Wifi, WifiOff } from 'lucide-react'
import { useLeadsPendingApproval, useCurrentUser, useLogout, useHealth } from '@/lib/queries'

export function Header() {
  const { total: pendingCount } = useLeadsPendingApproval()
  const { data: user } = useCurrentUser()
  const logout = useLogout()
  const { data: health, isError: healthError } = useHealth()

  const isOnline = Boolean(health?.status === 'healthy')

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-sm">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Left: brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-xs font-bold">LF</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground leading-tight">LeadFlow RevOps</h1>
            <p className="text-[11px] text-muted-foreground leading-tight">Agent Supervisor Dashboard</p>
          </div>
        </div>

        {/* Right: alerts + user */}
        <div className="flex items-center gap-3">
          {/* Pending approval pill */}
          {pendingCount > 0 && (
            <div className="flex items-center gap-2 rounded-full bg-orange-500/10 border border-orange-500/20 px-3 py-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-orange-400 animate-pulse" />
              <span className="text-xs font-medium text-orange-400">
                {pendingCount} pending approval{pendingCount !== 1 ? 's' : ''}
              </span>
            </div>
          )}

          {/* Backend connection indicator */}
          <div
            title={
              isOnline
                ? `Backend healthy — ${health?.service ?? 'LeadFlow API'}`
                : healthError
                  ? 'Backend unreachable'
                  : 'Checking backend…'
            }
            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium border ${
              isOnline
                ? 'bg-green-500/10 border-green-500/20 text-green-400'
                : healthError
                  ? 'bg-destructive/10 border-destructive/20 text-destructive'
                  : 'bg-muted/60 border-border text-muted-foreground'
            }`}
          >
            {isOnline ? (
              <Wifi className="h-3 w-3" />
            ) : (
              <WifiOff className="h-3 w-3" />
            )}
            <span className="hidden sm:inline">
              {isOnline ? 'Connected' : healthError ? 'Offline' : '…'}
            </span>
          </div>

          {/* User email */}
          {user?.email && (
            <span className="hidden text-xs font-medium text-muted-foreground xl:inline">
              {user.email}
            </span>
          )}

          {/* Sign out */}
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
