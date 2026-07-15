'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Users, FileText, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Active Leads',
    href: '/dashboard/leads',
    icon: Users,
  },
  {
    label: 'Audit Logs',
    href: '/dashboard/audit',
    icon: FileText,
  },
  {
    label: 'System Settings',
    href: '/dashboard/settings',
    icon: Settings,
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-border bg-card pt-0">
      {/* Logo / Brand */}
      <div className="flex h-16 items-center gap-3 border-b border-border px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
          <div className="text-sm font-bold text-primary">☑️</div>
        </div>
        <span className="text-sm font-semibold text-card-foreground">SuperDash</span>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 px-4 py-4">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground',
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 border-t border-border bg-card/50 p-4 text-xs text-muted-foreground">
        <p>v0.1.0 • Sandbox</p>
      </div>
    </aside>
  )
}
