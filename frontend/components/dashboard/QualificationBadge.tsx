import { cn } from '@/lib/utils'

interface QualificationBadgeProps {
  score?: number | null
  className?: string
}

export function QualificationBadge({ score, className }: QualificationBadgeProps) {
  if (score == null) {
    return <span className="text-xs text-muted-foreground">—</span>
  }

  const config =
    score >= 90 ? { bg: 'bg-red-500/20 text-red-400',    label: 'Critical' } :
    score >= 70 ? { bg: 'bg-green-500/20 text-green-400', label: 'High' }    :
    score >= 50 ? { bg: 'bg-amber-500/20 text-amber-400', label: 'Medium' }  :
                  { bg: 'bg-muted text-muted-foreground', label: 'Low' }

  return (
    <div className={cn(
      'inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium',
      config.bg,
      className,
    )}>
      <div className="h-1.5 w-1.5 rounded-full bg-current" />
      {score} · {config.label}
    </div>
  )
}
