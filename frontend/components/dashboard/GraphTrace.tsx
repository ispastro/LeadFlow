'use client'

import { CheckCircle2, Clock, Circle, AlertCircle } from 'lucide-react'
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
  hitl_node:           'Human Approval',
  drafting_node:       'Drafting',
  critic_node:         'Critic Review',
  deliver_node:        'Delivery',
  manual_review_node:  'Manual Review',
}

export function GraphTrace({ steps, currentNode }: GraphTraceProps) {
  if (!steps || steps.length === 0) return null

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-foreground">Pipeline Trace</h3>
      <div className="relative space-y-1 pt-1">
        {steps.map((step, index) => {
          const isLast = index === steps.length - 1
          const isManualReview = step.name === 'manual_review_node'
          const label = NODE_LABELS[step.name] ?? step.name

          return (
            <div key={step.name} className="relative">
              {/* Connector line */}
              {!isLast && (
                <div className="absolute left-[9px] top-9 h-[calc(100%-8px)] w-0.5 bg-border" />
              )}
              <div className="flex gap-3">
                {/* Status icon */}
                <div className="relative flex h-5 w-5 shrink-0 items-center justify-center mt-2.5">
                  {step.status === 'completed' && !isManualReview && (
                    <CheckCircle2 className="h-5 w-5 text-green-400" />
                  )}
                  {step.status === 'completed' && isManualReview && (
                    <AlertCircle className="h-5 w-5 text-yellow-400" />
                  )}
                  {step.status === 'in-progress' && (
                    <Clock className="h-5 w-5 text-blue-400 animate-pulse" />
                  )}
                  {step.status === 'pending' && (
                    <Circle className="h-5 w-5 text-muted-foreground/30" />
                  )}
                </div>

                {/* Card */}
                <div className="flex-1 pb-2">
                  <div
                    className={cn(
                      'rounded-lg px-3 py-2.5 transition-colors',
                      step.status === 'completed' && !isManualReview ? 'bg-green-500/8' : '',
                      step.status === 'completed' && isManualReview  ? 'bg-yellow-500/10' : '',
                      step.status === 'in-progress' ? 'bg-blue-500/10 ring-1 ring-blue-500/20' : '',
                      step.status === 'pending'     ? 'bg-muted/20' : '',
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p
                        className={cn(
                          'text-sm font-medium',
                          step.status === 'completed' && !isManualReview ? 'text-foreground'       : '',
                          step.status === 'completed' && isManualReview  ? 'text-yellow-400'       : '',
                          step.status === 'in-progress'                  ? 'text-blue-400'         : '',
                          step.status === 'pending'                      ? 'text-muted-foreground' : '',
                        )}
                      >
                        {label}
                      </p>
                      {step.status === 'in-progress' && (
                        <span className="text-[10px] font-medium text-blue-400 uppercase tracking-wide">
                          Active
                        </span>
                      )}
                    </div>
                    {step.detail && (
                      <p className="mt-0.5 text-xs text-muted-foreground leading-snug">
                        {step.detail}
                      </p>
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
