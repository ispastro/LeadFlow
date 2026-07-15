'use client'

interface HeaderProps {
  pendingCount: number
}

export function Header({ pendingCount }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-sm">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-sm font-bold">AI</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground">Agent Supervisor Dashboard</h1>
            <p className="text-xs text-muted-foreground">Lead Qualification System</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium text-foreground">
              Global Lead Flow Status
            </p>
            <p className="text-xs text-muted-foreground">
              {pendingCount} {pendingCount === 1 ? 'lead' : 'leads'} pending approval
            </p>
          </div>
        </div>
      </div>
    </header>
  )
}
