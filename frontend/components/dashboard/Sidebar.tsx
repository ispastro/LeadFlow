'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  BookOpen,
  BarChart2,
  Settings,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useLeadsPendingApproval } from '@/lib/queries'

const navItems = [
  { label: 'Overview',      href: '/dashboard',              icon: LayoutDashboard },
  { label: 'Leads',         href: '/dashboard/leads',         icon: Users          },
  { label: 'Conversations', href: '/dashboard/conversations', icon: MessageSquare  },
  { label: 'Knowledge',     href: '/dashboard/knowledge',     icon: BookOpen       },
  { label: 'Analytics',     href: '/dashboard/analytics',     icon: BarChart2      },
  { label: 'Settings',      href: '/dashboard/settings',      icon: Settings       },
]

export function Sidebar() {
  const pathname = usePathname()
  const { total: pendingCount } = useLeadsPendingApproval()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-border bg-card flex flex-col">
      {/* Brand */}
      <div className="flex h-16 items-center gap-3 border-b border-border px-6 shrink-0">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
          <span className="text-xs font-bold text-primary">LF</span>
        </div>
        <div>
          <span className="text-sm font-semibold text-card-foreground">LeadFlow</span>
          <p className="text-[10px] text-muted-foreground leading-tight">RevOps Engine v2.0</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 px-4 py-4 flex-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive =
            item.href === '/dashboard'
              ? pathname === '/dashboard'
              : pathname.startsWith(item.href)
          const showPendingBadge = item.href === '/dashboard/leads' && pendingCount > 0

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground',
              )}
              title={showPendingBadge ? `${pendingCount} lead${pendingCount !== 1 ? 's' : ''} awaiting approval` : undefined}
            >
              <div className="flex items-center gap-3">
                <Icon className="h-4 w-4 shrink-0" />
                <span>{item.label}</span>
              </div>

              {showPendingBadge && (
                <span className="relative flex items-center justify-center">
                  {/* Pulse ring */}
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-orange-400 opacity-40" />
                  <span className="relative inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-orange-500/20 px-1.5 text-[11px] font-semibold text-orange-400">
                    {pendingCount > 99 ? '99+' : pendingCount}
                  </span>
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="shrink-0 border-t border-border px-6 py-3 text-[11px] text-muted-foreground">
        AI-powered Revenue Operations
      </div>
    </aside>
  )
}
