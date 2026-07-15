'use client'

import { CheckCircle2, Clock, Circle } from 'lucide-react'
import type { TraceStep } from '@/types/dashboard'

interface GraphTraceProps {
  steps: TraceStep[]
}

export function GraphTrace({ steps }: GraphTraceProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-400" />
      case 'in-progress':
        return <Clock className="h-5 w-5 animate-spin text-blue-400" />
      case 'pending':
        return <Circle className="h-5 w-5 text-muted-foreground" />
      default:
        return <Circle className="h-5 w-5 text-muted-foreground" />
    }
  }

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20'
      case 'in-progress':
        return 'bg-blue-500/20'
      case 'pending':
        return 'bg-muted'
      default:
        return 'bg-muted'
    }
  }

  const getLineColor = (currentIndex: number, nextStepStatus: string) => {
    if (currentIndex === 0 && nextStepStatus === 'pending') {
      return 'bg-muted'
    }
    return 'bg-gradient-to-b from-green-500/30 to-muted'
  }

  return (
    <div className="space-y-1">
      <h3 className="text-sm font-semibold text-foreground">Graph Trace</h3>
      <div className="relative space-y-2 pt-2">
        {steps.map((step, index) => {
          const nextStep = steps[index + 1]
          const isLast = index === steps.length - 1

          return (
            <div key={step.id} className="relative">
              {/* Timeline line */}
              {!isLast && (
                <div
                  className={cn(
                    'absolute left-2.5 top-10 h-8 w-0.5',
                    getLineColor(index, nextStep?.status || 'pending'),
                  )}
                />
              )}

              {/* Step node */}
              <div className="flex gap-4">
                <div className={cn('relative flex h-5 w-5 items-center justify-center rounded-full')}>
                  {getStatusIcon(step.status)}
                </div>

                {/* Step content */}
                <div className="flex-1 pb-2">
                  <div className="rounded-lg bg-muted/50 p-3">
                    <p className="text-sm font-medium text-foreground">{step.name}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {step.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </p>
                    {Object.keys(step.data).length > 0 && (
                      <div className="mt-2 space-y-1">
                        {Object.entries(step.data).map(([key, value]) => (
                          <p key={key} className="text-xs text-muted-foreground">
                            <span className="font-mono text-xs text-foreground/70">{key}:</span> {String(value)}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ')
}
