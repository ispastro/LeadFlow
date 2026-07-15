import { cn } from '@/lib/utils'

interface QualificationBadgeProps {
  score: number
  className?: string
}

export function QualificationBadge({ score, className }: QualificationBadgeProps) {
  let bgColor = 'bg-red-500/20 text-red-400'
  let label = 'Low'

  if (score >= 86) {
    bgColor = 'bg-green-500/20 text-green-400'
    label = 'High'
  } else if (score >= 51) {
    bgColor = 'bg-amber-500/20 text-amber-400'
    label = 'Medium'
  }

  return (
    <div className={cn('inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium', bgColor, className)}>
      <div className="flex h-2 w-2 rounded-full bg-current" />
      {score}% · {label}
    </div>
  )
}
