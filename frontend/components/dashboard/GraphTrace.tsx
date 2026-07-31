'use client'

import { CheckCircle2, Clock, Circle } from 'lucide-react'
import type { TraceStep } from '@/types/dashboard'
import { cn } from '@/lib/utils'

interface GraphTraceProps {
  steps: TraceStep[]
  currentNode?: string
}

const NODE_LABELS: Record<string, string> = {
  input_node:          'Input',
  enrichment_node:     'Enrichment',
  qualification_node:  'Qualification',
  drafting_node:       'Drafting',
  critic_node:         'Critic Review',
  hitl_node:           'Human Approval',
  deliver_node:        'Delivery',
  manual_review_node:  'Manual Review',
}

export function GraphTrace({ steps, currentNode }: GraphTraceProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-foreground">Graph Trace</h3>
      <div className="relative space-y-2 pt-2">
        {steps.map((step, index) => {
          const isLast = index === steps.length - 1
          const label = NODE_LABELS[step.name] ?? step.name

          return (
            <div key={step.name} className="relative">
              {!isLast && (
                <div className="absolute left-2.5 top-10 h-8 w-0.5 bg-border" />
              )}
              <div className="flex gap-4">
                <div className="relative flex h-5 w-5 shrink-0 items-center justify-center">
                  {step.status === 'completed'  && <CheckCircle2 className="h-5 w-5 text-green-400" />}
                  {step.status === 'in-progress' && <Clock className="h-5 w-5 animate-spin text-blue-400" />}
                  {step.status === 'pending'     && <Circle className="h-5 w-5 text-muted-foreground/40" />}
                </div>
                <div className="flex-1 pb-2">
                  <div className={cn(
                    'rounded-lg p-3',
                    step.status === 'completed'   ? 'bg-green-500/10'  : '',
                    step.status === 'in-progress' ? 'bg-blue-500/10'   : '',
                    step.status === 'pending'     ? 'bg-muted/30'      : '',
                  )}>
                    <p className={cn(
                      'text-sm font-medium',
                      step.status === 'completed'   ? 'text-foreground'         : '',
                      step.status === 'in-progress' ? 'text-blue-400'           : '',
                      step.status === 'pending'     ? 'text-muted-foreground'   : '',
                    )}>
                      {label}
                    </p>
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
