import { Header } from '@/components/dashboard/Header'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { getLeadsPendingApproval, mockLeads } from '@/lib/mock-data'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pendingCount = getLeadsPendingApproval(mockLeads)

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="ml-64 flex flex-col flex-1">
        {/* Header */}
        <Header pendingCount={pendingCount} />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
