import { useQuery } from '@tanstack/react-query'
import { FileText, Upload } from 'lucide-react'
import { dashboardApi } from '../api/client'
import { Link } from 'react-router-dom'

export default function RFPList() {
  const { data, isLoading } = useQuery({
    queryKey: ['rfps'],
    queryFn: () => dashboardApi.listRfps(),
  })

  const rfps = data?.rfps || []

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">RFPs</h1>
          <p className="mt-1 text-gray-600">All RFPs in your pipeline.</p>
        </div>
        <div className="flex gap-4">
          <Link
            to="/quick-scan"
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Quick Scan URL
          </Link>
          <button
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            onClick={() => alert('PDF upload coming in Sprint 2!')}
          >
            <Upload className="h-4 w-4" />
            Upload PDF
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-gray-500">Loading RFPs...</div>
      ) : rfps.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-4 text-lg font-medium text-gray-900">No RFPs yet</p>
          <p className="mt-2 text-gray-500">
            Use Quick Scan to analyze RFPs from bidsandtenders.ca
          </p>
          <Link
            to="/quick-scan"
            className="mt-4 inline-block rounded-lg bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Start Quick Scan
          </Link>
        </div>
      ) : (
        <div className="rounded-lg border border-gray-200 bg-white">
          <table className="w-full">
            <thead className="border-b border-gray-200 bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                  RFP Number
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                  Title
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                  Client
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                  Source
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">
                  Deadline
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {rfps.map((rfp: any) => (
                <tr key={rfp.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {rfp.rfp_number || '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {rfp.opportunity_title || 'Untitled'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {rfp.client_name || '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {rfp.source === 'quick_scan' ? 'Quick Scan' : 'PDF Upload'}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={rfp.status} />
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {rfp.submission_deadline || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
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
