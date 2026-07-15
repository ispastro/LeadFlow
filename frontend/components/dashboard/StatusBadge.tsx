import { cn } from '@/lib/utils'
import type { LeadStatus } from '@/types/dashboard'

interface StatusBadgeProps {
  status: LeadStatus
  className?: string
}

const statusConfig: Record<LeadStatus, { bg: string; text: string; label: string }> = {
  Drafting: {
    bg: 'bg-blue-500/20',
    text: 'text-blue-400',
    label: 'Drafting',
  },
  'Awaiting Approval': {
    bg: 'bg-orange-500/20',
    text: 'text-orange-400',
    label: 'Awaiting Approval',
  },
  Syncing: {
    bg: 'bg-purple-500/20',
    text: 'text-purple-400',
    label: 'Syncing',
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium',
        config.bg,
        config.text,
        className,
      )}
    >
      <div className="h-1.5 w-1.5 rounded-full bg-current" />
      {config.label}
    </span>
  )
}
