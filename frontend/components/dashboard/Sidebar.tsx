'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Users, MessageSquare, BookOpen, BarChart2, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useLeadsPendingApproval } from '@/lib/queries'

const navItems = [
  { label: 'Overview',      href: '/dashboard',               icon: LayoutDashboard },
  { label: 'Leads',         href: '/dashboard/leads',          icon: Users          },
  { label: 'Conversations', href: '/dashboard/conversations',  icon: MessageSquare  },
  { label: 'Knowledge',     href: '/dashboard/knowledge',      icon: BookOpen       },
  { label: 'Analytics',     href: '/dashboard/analytics',      icon: BarChart2      },
  { label: 'Settings',      href: '/dashboard/settings',       icon: Settings       },
]

export function Sidebar() {
  const pathname = usePathname()
  const { total: pendingCount } = useLeadsPendingApproval()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-border bg-card">
      {/* Brand */}
      <div className="flex h-16 items-center gap-3 border-b border-border px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
          <span className="text-xs font-bold text-primary">LF</span>
        </div>
        <span className="text-sm font-semibold text-card-foreground">LeadFlow</span>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 px-4 py-4">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          const isPendingItem = item.href === '/dashboard/leads' && pendingCount > 0

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
            >
              <div className="flex items-center gap-3">
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </div>
              {isPendingItem && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-orange-500/20 text-xs font-medium text-orange-400">
                  {pendingCount}
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 border-t border-border p-4 text-xs text-muted-foreground">
        RevOps Engine v2.0
      </div>
    </aside>
  )
}
