import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  ArrowRight,
  Calendar,
  AlertTriangle,
  Users,
} from 'lucide-react'
import { dashboardApi, subConsultantsApi } from '../api/client'
import { Link } from 'react-router-dom'
import {
  Button,
  StatusBadge,
  RecommendationBadge,
  DataTable,
  Column,
} from '../components/ui'

interface RFP {
  id: string
  opportunity_title: string
  rfp_number?: string
  client_name?: string
  status: string
  recommendation?: 'GO' | 'MAYBE' | 'NO_GO'
  score?: number
  submission_deadline?: string
  created_at: string
}

interface UpcomingRFP {
  id: string
  opportunity_title?: string
  client_name?: string
  submission_deadline: string
  days_remaining: number
  status: string
}

export default function Dashboard() {
  const navigate = useNavigate()

  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
  })

  const { data: upcomingData } = useQuery({
    queryKey: ['upcoming-deadlines'],
    queryFn: () =>
      fetch('http://localhost:8000/api/dashboard/upcoming-deadlines?days=14').then((r) =>
        r.json()
      ),
  })

  const { data: subsData } = useQuery({
    queryKey: ['subconsultants'],
    queryFn: () => subConsultantsApi.list(),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-text-tertiary">Loading dashboard...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="panel p-4 border-status-nogo/20 bg-status-nogo-bg">
        <p className="text-status-nogo">Failed to load dashboard. Is the backend running?</p>
      </div>
    )
  }

  const stats = data?.stats || {}
  const recentRfps: RFP[] = data?.recent_rfps || []
  const upcomingRfps: UpcomingRFP[] = upcomingData?.upcoming || []
  const subCount = subsData?.length || 0

  const columns: Column<RFP>[] = [
    {
      key: 'opportunity_title',
      header: 'RFP',
      width: 'flex',
      sortable: true,
      render: (row) => (
        <div>
          <p className="text-text-primary font-medium">
            {row.opportunity_title || row.client_name || 'Untitled'}
          </p>
          {row.rfp_number && (
            <p className="text-ui-xs text-text-tertiary font-mono">{row.rfp_number}</p>
          )}
        </div>
      ),
    },
    {
      key: 'client_name',
      header: 'Client',
      width: '180px',
      sortable: true,
      render: (row) => (
        <span className="text-text-secondary truncate">{row.client_name || '-'}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      width: '120px',
      render: (row) => <StatusBadge status={row.status as any} />,
    },
    {
      key: 'recommendation',
      header: 'Decision',
      width: '100px',
      render: (row) =>
        row.recommendation ? (
          <RecommendationBadge recommendation={row.recommendation} />
        ) : (
          <span className="text-text-tertiary">-</span>
        ),
    },
    {
      key: 'created_at',
      header: 'Added',
      width: '100px',
      render: (row) => (
        <span className="text-text-tertiary text-ui-sm">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-heading-lg text-text-primary">Dashboard</h1>
          <p className="mt-1 text-ui-base text-text-secondary">
            Overview of your RFP pipeline and recent activity.
          </p>
        </div>
        <div className="flex gap-3">
          <Link to="/quick-scan">
            <Button>Quick Scan URL</Button>
          </Link>
          <Link to="/rfps">
            <Button variant="secondary">
              Upload PDF
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <StatCard
          label="Total RFPs"
          value={stats.total_rfps || 0}
          icon={FileText}
          variant="default"
        />
        <StatCard
          label="GO Decisions"
          value={stats.by_status?.go || 0}
          icon={CheckCircle}
          variant="go"
        />
        <StatCard
          label="NO-GO"
          value={stats.by_status?.no_go || 0}
          icon={XCircle}
          variant="nogo"
        />
        <StatCard
          label="Pending Review"
          value={stats.pending_decisions || 0}
          icon={Clock}
          variant="pending"
        />
        <StatCard
          label="Sub-Consultants"
          value={subCount}
          icon={Users}
          variant="default"
          href="/sub-consultants"
        />
      </div>

      {/* GO Rate + Upcoming Deadlines Row */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* GO Rate Card */}
        <div className="panel p-4">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-md bg-status-go-bg">
              <TrendingUp className="h-5 w-5 text-status-go" />
            </div>
            <div>
              <p className="text-ui-sm text-text-secondary">GO Rate</p>
              <p className="text-heading-xl text-text-primary tabular-nums">
                {stats.go_rate || 0}%
              </p>
            </div>
          </div>
          <div className="flex gap-4 text-ui-sm">
            <div>
              <span className="text-text-tertiary">Decided: </span>
              <span className="text-text-primary font-medium">
                {(stats.by_status?.go || 0) + (stats.by_status?.no_go || 0)}
              </span>
            </div>
            <div>
              <span className="text-text-tertiary">Pending: </span>
              <span className="text-text-primary font-medium">{stats.pending_decisions || 0}</span>
            </div>
          </div>
        </div>

        {/* Upcoming Deadlines */}
        <div className="panel p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-text-tertiary" />
              <h3 className="text-heading-sm text-text-primary">Upcoming Deadlines</h3>
            </div>
            <span className="text-ui-sm text-text-tertiary">Next 14 days</span>
          </div>

          {upcomingRfps.length === 0 ? (
            <p className="text-text-tertiary text-ui-sm">No upcoming deadlines</p>
          ) : (
            <div className="space-y-2">
              {upcomingRfps.slice(0, 4).map((rfp) => (
                <div
                  key={rfp.id}
                  onClick={() => navigate(`/rfps/${rfp.id}`)}
                  className="flex items-center justify-between p-2 rounded hover:bg-surface-secondary cursor-pointer"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-text-primary text-ui-sm truncate">
                      {rfp.opportunity_title || rfp.client_name || 'Untitled'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-3">
                    {rfp.days_remaining <= 3 && (
                      <AlertTriangle className="h-4 w-4 text-status-nogo" />
                    )}
                    <span
                      className={`text-ui-sm font-medium ${
                        rfp.days_remaining <= 3
                          ? 'text-status-nogo'
                          : rfp.days_remaining <= 7
                            ? 'text-status-pending'
                            : 'text-text-secondary'
                      }`}
                    >
                      {rfp.days_remaining === 0
                        ? 'Today'
                        : rfp.days_remaining === 1
                          ? '1 day'
                          : `${rfp.days_remaining} days`}
                    </span>
                  </div>
                </div>
              ))}
              {upcomingRfps.length > 4 && (
                <Link
                  to="/rfps"
                  className="block text-center text-ui-sm text-accent-primary hover:underline pt-2"
                >
                  View all {upcomingRfps.length} upcoming
                </Link>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Recent RFPs */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-heading-sm text-text-primary">Recent RFPs</h2>
          <Link to="/rfps" className="text-ui-sm text-accent-primary hover:underline">
            View all
          </Link>
        </div>
        {recentRfps.length === 0 ? (
          <div className="panel p-8 text-center border-dashed">
            <FileText className="mx-auto h-12 w-12 text-text-tertiary" />
            <p className="mt-3 text-text-secondary">No RFPs yet</p>
            <p className="mt-1 text-ui-sm text-text-tertiary">
              Use Quick Scan to analyze your first RFP
            </p>
            <Link to="/quick-scan" className="mt-4 inline-block">
              <Button>Start Quick Scan</Button>
            </Link>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={recentRfps}
            keyField="id"
            onRowClick={(row) => navigate(`/rfps/${row.id}`)}
          />
        )}
      </div>

      {/* Quick Links */}
      <div className="grid md:grid-cols-3 gap-4">
        <QuickLinkCard
          title="Quick Scan"
          description="Analyze RFP from bidsandtenders.ca URL"
          href="/quick-scan"
          icon={FileText}
        />
        <QuickLinkCard
          title="Upload PDF"
          description="Deep scan uploaded RFP documents"
          href="/rfps"
          icon={ArrowRight}
        />
        <QuickLinkCard
          title="Sub-Consultants"
          description="Manage your partner registry"
          href="/sub-consultants"
          icon={Users}
        />
      </div>
    </div>
  )
}

interface StatCardProps {
  label: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  variant: 'default' | 'go' | 'nogo' | 'pending'
  href?: string
}

function StatCard({ label, value, icon: Icon, variant, href }: StatCardProps) {
  const iconStyles = {
    default: 'bg-accent-muted text-accent',
    go: 'bg-status-go-bg text-status-go',
    nogo: 'bg-status-nogo-bg text-status-nogo',
    pending: 'bg-status-pending-bg text-status-pending',
  }

  const content = (
    <div className={`panel p-4 ${href ? 'hover:border-accent-primary cursor-pointer' : ''}`}>
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-md ${iconStyles[variant]}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-ui-sm text-text-secondary">{label}</p>
          <p className="text-heading-lg text-text-primary tabular-nums">{value}</p>
        </div>
      </div>
    </div>
  )

  if (href) {
    return <Link to={href}>{content}</Link>
  }
  return content
}

interface QuickLinkCardProps {
  title: string
  description: string
  href: string
  icon: React.ComponentType<{ className?: string }>
}

function QuickLinkCard({ title, description, href, icon: Icon }: QuickLinkCardProps) {
  return (
    <Link
      to={href}
      className="panel p-4 hover:border-accent-primary transition-colors group"
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-md bg-surface-secondary group-hover:bg-accent-muted">
          <Icon className="h-5 w-5 text-text-tertiary group-hover:text-accent" />
        </div>
        <div>
          <h3 className="text-heading-sm text-text-primary group-hover:text-accent-primary">
            {title}
          </h3>
          <p className="text-ui-sm text-text-tertiary mt-1">{description}</p>
        </div>
      </div>
    </Link>
  )
}
