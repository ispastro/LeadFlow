import type { Lead } from '@/types/dashboard'

export const mockLeads: Lead[] = [
  {
    id: 'lead-001',
    name: 'Sarah Chen',
    company: 'TechVenture Inc',
    qualificationScore: 92,
    status: 'Awaiting Approval',
    threadId: 'thread-001',
    enrichmentData: {
      industry: 'Software / SaaS',
      revenue: '$50M - $100M',
      employees: '201-500',
      website: 'techventure.com',
      linkedinUrl: 'linkedin.com/company/techventure',
    },
    timeline: [
      {
        id: 'step-1',
        name: 'Input',
        timestamp: new Date('2025-01-15T08:00:00Z'),
        status: 'completed',
        data: { source: 'email', enrichedFields: 3 },
      },
      {
        id: 'step-2',
        name: 'Enrichment',
        timestamp: new Date('2025-01-15T08:05:00Z'),
        status: 'completed',
        data: {
          company: 'TechVenture Inc',
          industry: 'Software',
          foundedYear: 2018,
        },
      },
      {
        id: 'step-3',
        name: 'Qualification',
        timestamp: new Date('2025-01-15T08:10:00Z'),
        status: 'completed',
        data: { score: 92, signal_strength: 'high' },
      },
      {
        id: 'step-4',
        name: 'Critic Feedback',
        timestamp: new Date('2025-01-15T08:15:00Z'),
        status: 'completed',
        data: { feedback: 'Excellent fit for product', confidence: 0.94 },
      },
    ],
    draftEmail: `Subject: Introducing Automated Lead Qualification for TechVenture

Hi Sarah,

I hope this message finds you well. At TechVenture Inc, you're clearly focused on scaling your operations efficiently. Our AI-powered lead qualification system could reduce your sales cycle by 40%.

I'd love to show you a 15-minute demo of how we're helping SaaS companies like yours qualify leads 3x faster.

Are you open to a brief conversation this week?

Best regards,
The Sales Team`,
    createdAt: new Date('2025-01-15T08:00:00Z'),
    lastModified: new Date('2025-01-15T08:15:00Z'),
  },
  {
    id: 'lead-002',
    name: 'Marcus Johnson',
    company: 'CloudScale Solutions',
    qualificationScore: 78,
    status: 'Drafting',
    threadId: 'thread-002',
    enrichmentData: {
      industry: 'Cloud Infrastructure',
      revenue: '$20M - $50M',
      employees: '51-200',
    },
    timeline: [
      {
        id: 'step-1',
        name: 'Input',
        timestamp: new Date('2025-01-15T09:00:00Z'),
        status: 'completed',
        data: { source: 'linkedin', enrichedFields: 2 },
      },
      {
        id: 'step-2',
        name: 'Enrichment',
        timestamp: new Date('2025-01-15T09:05:00Z'),
        status: 'completed',
        data: { company: 'CloudScale Solutions', industry: 'Cloud' },
      },
      {
        id: 'step-3',
        name: 'Qualification',
        timestamp: new Date('2025-01-15T09:10:00Z'),
        status: 'in-progress',
        data: { score: 78, signal_strength: 'medium' },
      },
      {
        id: 'step-4',
        name: 'Critic Feedback',
        timestamp: new Date('2025-01-15T09:15:00Z'),
        status: 'pending',
        data: { feedback: 'Awaiting final review' },
      },
    ],
    createdAt: new Date('2025-01-15T09:00:00Z'),
    lastModified: new Date('2025-01-15T09:10:00Z'),
  },
  {
    id: 'lead-003',
    name: 'Emma Rodriguez',
    company: 'DataFlow Analytics',
    qualificationScore: 88,
    status: 'Syncing',
    threadId: 'thread-003',
    enrichmentData: {
      industry: 'Data Analytics',
      revenue: '$10M - $20M',
      employees: '51-200',
    },
    timeline: [
      {
        id: 'step-1',
        name: 'Input',
        timestamp: new Date('2025-01-15T10:00:00Z'),
        status: 'completed',
        data: { source: 'api', enrichedFields: 4 },
      },
      {
        id: 'step-2',
        name: 'Enrichment',
        timestamp: new Date('2025-01-15T10:05:00Z'),
        status: 'completed',
        data: { company: 'DataFlow Analytics' },
      },
      {
        id: 'step-3',
        name: 'Qualification',
        timestamp: new Date('2025-01-15T10:10:00Z'),
        status: 'completed',
        data: { score: 88 },
      },
      {
        id: 'step-4',
        name: 'Critic Feedback',
        timestamp: new Date('2025-01-15T10:15:00Z'),
        status: 'completed',
        data: { feedback: 'Strong profile' },
      },
    ],
    createdAt: new Date('2025-01-15T10:00:00Z'),
    lastModified: new Date('2025-01-15T10:15:00Z'),
  },
  {
    id: 'lead-004',
    name: 'James Wilson',
    company: 'SecureNet Corp',
    qualificationScore: 45,
    status: 'Drafting',
    threadId: 'thread-004',
    enrichmentData: {
      industry: 'Cybersecurity',
      revenue: '$5M - $10M',
      employees: '20-50',
    },
    timeline: [
      {
        id: 'step-1',
        name: 'Input',
        timestamp: new Date('2025-01-15T11:00:00Z'),
        status: 'completed',
        data: { source: 'email', enrichedFields: 1 },
      },
      {
        id: 'step-2',
        name: 'Enrichment',
        timestamp: new Date('2025-01-15T11:05:00Z'),
        status: 'completed',
        data: { company: 'SecureNet Corp' },
      },
      {
        id: 'step-3',
        name: 'Qualification',
        timestamp: new Date('2025-01-15T11:10:00Z'),
        status: 'completed',
        data: { score: 45 },
      },
      {
        id: 'step-4',
        name: 'Critic Feedback',
        timestamp: new Date('2025-01-15T11:15:00Z'),
        status: 'pending',
        data: { feedback: 'Low fit for current offering' },
      },
    ],
    createdAt: new Date('2025-01-15T11:00:00Z'),
    lastModified: new Date('2025-01-15T11:10:00Z'),
  },
  {
    id: 'lead-005',
    name: 'Lisa Park',
    company: 'Growth Marketing Pro',
    qualificationScore: 85,
    status: 'Awaiting Approval',
    threadId: 'thread-005',
    enrichmentData: {
      industry: 'Marketing / Advertising',
      revenue: '$2M - $5M',
      employees: '10-20',
    },
    timeline: [
      {
        id: 'step-1',
        name: 'Input',
        timestamp: new Date('2025-01-15T12:00:00Z'),
        status: 'completed',
        data: { source: 'website', enrichedFields: 3 },
      },
      {
        id: 'step-2',
        name: 'Enrichment',
        timestamp: new Date('2025-01-15T12:05:00Z'),
        status: 'completed',
        data: { company: 'Growth Marketing Pro' },
      },
      {
        id: 'step-3',
        name: 'Qualification',
        timestamp: new Date('2025-01-15T12:10:00Z'),
        status: 'completed',
        data: { score: 85 },
      },
      {
        id: 'step-4',
        name: 'Critic Feedback',
        timestamp: new Date('2025-01-15T12:15:00Z'),
        status: 'completed',
        data: { feedback: 'Good match, recommend approval' },
      },
    ],
    draftEmail: `Subject: Transform Your Lead Generation Strategy

Hi Lisa,

Growth Marketing Pro is doing impressive work in the space. We've helped similar agencies cut their qualification time by 50%.

Let's discuss how we can integrate our system into your workflow.

Best regards,
Sales Team`,
    createdAt: new Date('2025-01-15T12:00:00Z'),
    lastModified: new Date('2025-01-15T12:15:00Z'),
  },
]

export function getLeadsPendingApproval(leads: Lead[]): number {
  return leads.filter((lead) => lead.status === 'Awaiting Approval').length
}

export function getLeadById(leads: Lead[], id: string): Lead | undefined {
  return leads.find((lead) => lead.id === id)
}
