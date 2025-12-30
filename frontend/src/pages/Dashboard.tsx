import { useQuery } from '@tanstack/react-query'
import { FileText, CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react'
import { dashboardApi } from '../api/client'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
  })

  if (isLoading) {
    return <div className="text-gray-500">Loading dashboard...</div>
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-700">
        Failed to load dashboard. Is the backend running?
      </div>
    )
  }

  const stats = data?.stats || {}
  const recentRfps = data?.recent_rfps || []

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-gray-600">
          Overview of your RFP pipeline and recent activity.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid grid-cols-4 gap-6">
        <StatCard
          label="Total RFPs"
          value={stats.total_rfps || 0}
          icon={FileText}
          color="blue"
        />
        <StatCard
          label="GO Decisions"
          value={stats.by_status?.go || 0}
          icon={CheckCircle}
          color="green"
        />
        <StatCard
          label="NO-GO Decisions"
          value={stats.by_status?.no_go || 0}
          icon={XCircle}
          color="red"
        />
        <StatCard
          label="Pending"
          value={stats.pending_decisions || 0}
          icon={Clock}
          color="yellow"
        />
      </div>

      {/* Go Rate */}
      {stats.total_rfps > 0 && (
        <div className="mb-8 rounded-lg border border-gray-200 bg-white p-6">
          <div className="flex items-center gap-3">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <div>
              <p className="text-sm text-gray-500">GO Rate</p>
              <p className="text-2xl font-bold text-gray-900">{stats.go_rate}%</p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Quick Actions</h2>
        <div className="flex gap-4">
          <Link
            to="/quick-scan"
            className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700"
          >
            Quick Scan URL
          </Link>
          <Link
            to="/rfps"
            className="rounded-lg border border-gray-300 px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            View All RFPs
          </Link>
        </div>
      </div>

      {/* Recent RFPs */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Recent RFPs</h2>
        {recentRfps.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-gray-500">No RFPs yet</p>
            <p className="mt-1 text-sm text-gray-400">
              Use Quick Scan to analyze your first RFP
            </p>
          </div>
        ) : (
          <div className="rounded-lg border border-gray-200 bg-white">
            <table className="w-full">
              <thead className="border-b border-gray-200 bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                    RFP
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                    Client
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                    Recommendation
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {recentRfps.map((rfp: any) => (
                  <tr key={rfp.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-900">
                          {rfp.opportunity_title || 'Untitled'}
                        </p>
                        {rfp.rfp_number && (
                          <p className="text-xs text-gray-500">{rfp.rfp_number}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {rfp.client_name || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={rfp.status} />
                    </td>
                    <td className="px-4 py-3">
                      {rfp.recommendation && (
                        <RecommendationBadge recommendation={rfp.recommendation} />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string
  value: number
  icon: any
  color: 'blue' | 'green' | 'red' | 'yellow'
}) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <div className="flex items-center gap-4">
        <div className={`rounded-lg p-3 ${colors[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    new: 'bg-gray-100 text-gray-700',
    processing: 'bg-blue-100 text-blue-700',
    extracted: 'bg-purple-100 text-purple-700',
    reviewed: 'bg-yellow-100 text-yellow-700',
    go: 'bg-green-100 text-green-700',
    no_go: 'bg-red-100 text-red-700',
  }

  return (
    <span className={`inline-block rounded px-2 py-1 text-xs font-medium ${colors[status] || colors.new}`}>
      {status.toUpperCase().replace('_', ' ')}
    </span>
  )
}

function RecommendationBadge({ recommendation }: { recommendation: string }) {
  const colors: Record<string, string> = {
    GO: 'bg-green-100 text-green-700',
    MAYBE: 'bg-yellow-100 text-yellow-700',
    NO_GO: 'bg-red-100 text-red-700',
  }

  return (
    <span className={`inline-block rounded px-2 py-1 text-xs font-medium ${colors[recommendation] || 'bg-gray-100 text-gray-700'}`}>
      {recommendation}
    </span>
  )
}
