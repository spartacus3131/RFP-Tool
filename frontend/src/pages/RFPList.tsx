import { useState, useRef, useMemo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { FileText, Upload, Filter, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { dashboardApi, rfpApi } from '../api/client'
import { Link, useNavigate } from 'react-router-dom'
import {
  Button,
  StatusBadge,
  RecommendationBadge,
  DataTable,
  Column,
  ScoreBadge,
  ActionsMenu,
  ActionMenuItem,
  Badge,
} from '../components/ui'

interface RFP {
  id: string
  rfp_number?: string
  opportunity_title: string
  client_name?: string
  source: string
  status: string
  recommendation?: 'GO' | 'MAYBE' | 'NO_GO'
  score?: number
  submission_deadline?: string
  created_at: string
}

interface UploadStatus {
  status: 'idle' | 'uploading' | 'success' | 'error'
  message?: string
  pageCount?: number
  rfpId?: string
}

const STATUS_OPTIONS = [
  { value: 'new', label: 'New' },
  { value: 'processing', label: 'Processing' },
  { value: 'extracted', label: 'Extracted' },
  { value: 'reviewed', label: 'Reviewed' },
  { value: 'go', label: 'GO' },
  { value: 'no_go', label: 'NO-GO' },
]

export default function RFPList() {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({ status: 'idle' })
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [clientFilter, setClientFilter] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploadStatus({ status: 'uploading', message: `Uploading ${file.name}...` })

    try {
      const result = await rfpApi.upload(file)
      setUploadStatus({
        status: 'success',
        message: result.message,
        pageCount: result.page_count,
        rfpId: result.id,
      })
      // Refresh the RFP list
      queryClient.invalidateQueries({ queryKey: ['rfps'] })
    } catch (error: any) {
      setUploadStatus({
        status: 'error',
        message: error.response?.data?.detail || 'Upload failed. Please try again.',
      })
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const { data, isLoading } = useQuery({
    queryKey: ['rfps', statusFilter, clientFilter],
    queryFn: () =>
      dashboardApi.listRfps({
        status: statusFilter || undefined,
        client: clientFilter || undefined,
      }),
  })

  const rfps: RFP[] = data?.rfps || []

  // Get unique clients for filter dropdown
  const uniqueClients = useMemo(() => {
    const clients = new Set<string>()
    rfps.forEach((rfp) => {
      if (rfp.client_name) clients.add(rfp.client_name)
    })
    return Array.from(clients).sort()
  }, [rfps])

  const hasActiveFilters = statusFilter || clientFilter

  const clearFilters = () => {
    setStatusFilter('')
    setClientFilter('')
  }

  const getRowActions = (row: RFP): ActionMenuItem[] => [
    {
      label: 'View Details',
      shortcut: 'Enter',
      onClick: () => console.log('View:', row.id),
    },
    {
      label: 'Mark as GO',
      shortcut: 'G',
      onClick: () => console.log('Mark GO:', row.id),
    },
    {
      label: 'Mark as NO-GO',
      shortcut: 'N',
      onClick: () => console.log('Mark NO-GO:', row.id),
    },
    {
      label: 'Delete',
      shortcut: 'D',
      danger: true,
      onClick: () => console.log('Delete:', row.id),
    },
  ]

  const columns: Column<RFP>[] = [
    {
      key: 'rfp_number',
      header: 'RFP #',
      width: '120px',
      sortable: true,
      render: (row) => (
        <span className="font-mono text-ui-sm text-text-secondary">
          {row.rfp_number || '-'}
        </span>
      ),
    },
    {
      key: 'opportunity_title',
      header: 'Title',
      width: 'flex',
      sortable: true,
      render: (row) => (
        <span className="text-text-primary font-medium">
          {row.opportunity_title || 'Untitled'}
        </span>
      ),
    },
    {
      key: 'client_name',
      header: 'Client',
      width: '150px',
      sortable: true,
      render: (row) => (
        <span className="text-text-secondary">{row.client_name || '-'}</span>
      ),
    },
    {
      key: 'source',
      header: 'Source',
      width: '100px',
      render: (row) => (
        <span className="text-ui-sm text-text-tertiary">
          {row.source === 'quick_scan' ? 'Quick Scan' : 'PDF Upload'}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      width: '120px',
      sortable: true,
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
      key: 'score',
      header: 'Score',
      width: '80px',
      align: 'right',
      sortable: true,
      render: (row) =>
        row.score !== undefined ? (
          <ScoreBadge value={row.score} />
        ) : (
          <span className="text-text-tertiary">-</span>
        ),
    },
    {
      key: 'submission_deadline',
      header: 'Deadline',
      width: '110px',
      sortable: true,
      render: (row) => (
        <span className="text-ui-sm text-text-secondary">
          {row.submission_deadline || '-'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      width: '50px',
      align: 'right',
      render: (row) => <ActionsMenu items={getRowActions(row)} />,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-heading-lg text-text-primary">RFPs</h1>
          <p className="mt-1 text-ui-base text-text-secondary">
            All RFPs in your pipeline.
          </p>
        </div>
        <div className="flex gap-3">
          <Link to="/quick-scan">
            <Button>Quick Scan URL</Button>
          </Link>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
          />
          <Button
            variant="secondary"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadStatus.status === 'uploading'}
          >
            {uploadStatus.status === 'uploading' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Upload className="h-4 w-4" />
            )}
            {uploadStatus.status === 'uploading' ? 'Uploading...' : 'Upload PDF'}
          </Button>
        </div>
      </div>

      {/* Upload Status Banner */}
      {uploadStatus.status !== 'idle' && uploadStatus.status !== 'uploading' && (
        <div
          className={`panel px-4 py-3 flex items-center gap-3 animate-slide-down ${
            uploadStatus.status === 'success'
              ? 'border-green-500/30 bg-green-500/5'
              : 'border-red-500/30 bg-red-500/5'
          }`}
        >
          {uploadStatus.status === 'success' ? (
            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
          )}
          <div className="flex-1">
            <p className={`text-ui-sm ${uploadStatus.status === 'success' ? 'text-green-400' : 'text-red-400'}`}>
              {uploadStatus.message}
            </p>
            {uploadStatus.pageCount && (
              <p className="text-ui-xs text-text-tertiary mt-0.5">
                Ready for Claude AI extraction (Sprint 2)
              </p>
            )}
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setUploadStatus({ status: 'idle' })}
          >
            Dismiss
          </Button>
        </div>
      )}

      {/* Bulk Actions Bar (when items selected) */}
      {selectedIds.size > 0 && (
        <div className="panel px-4 py-3 flex items-center gap-4 animate-slide-down">
          <span className="text-ui-sm text-text-secondary">
            {selectedIds.size} selected
          </span>
          <div className="flex gap-2">
            <Button size="sm" variant="ghost" onClick={() => console.log('Bulk GO')}>
              Mark GO
            </Button>
            <Button size="sm" variant="ghost" onClick={() => console.log('Bulk NO-GO')}>
              Mark NO-GO
            </Button>
            <Button size="sm" variant="danger" onClick={() => console.log('Bulk Delete')}>
              Delete
            </Button>
          </div>
          <Button
            size="sm"
            variant="ghost"
            className="ml-auto"
            onClick={() => setSelectedIds(new Set())}
          >
            Clear selection
          </Button>
        </div>
      )}

      {/* Filters */}
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <Button
            variant={showFilters ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4" />
            Filters
            {hasActiveFilters && (
              <span className="ml-1.5 px-1.5 py-0.5 text-xs bg-accent-primary text-white rounded-full">
                {(statusFilter ? 1 : 0) + (clientFilter ? 1 : 0)}
              </span>
            )}
          </Button>
          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <X className="h-4 w-4" />
              Clear filters
            </Button>
          )}
        </div>

        {/* Filter Controls */}
        {showFilters && (
          <div className="panel p-4 flex flex-wrap gap-4 animate-slide-down">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-ui-sm text-text-secondary mb-1.5">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
              >
                <option value="">All statuses</option>
                {STATUS_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="block text-ui-sm text-text-secondary mb-1.5">Client</label>
              <input
                type="text"
                value={clientFilter}
                onChange={(e) => setClientFilter(e.target.value)}
                placeholder="Search by client name..."
                className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
              />
            </div>
          </div>
        )}

        {/* Active Filter Tags */}
        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2">
            {statusFilter && (
              <Badge variant="info" className="flex items-center gap-1">
                Status: {STATUS_OPTIONS.find((s) => s.value === statusFilter)?.label}
                <button
                  onClick={() => setStatusFilter('')}
                  className="ml-1 hover:text-white"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            {clientFilter && (
              <Badge variant="info" className="flex items-center gap-1">
                Client: {clientFilter}
                <button
                  onClick={() => setClientFilter('')}
                  className="ml-1 hover:text-white"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
          </div>
        )}
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-text-tertiary">Loading RFPs...</div>
        </div>
      ) : (
        <DataTable
          columns={columns}
          data={rfps}
          keyField="id"
          selectable
          selectedIds={selectedIds}
          onSelectionChange={setSelectedIds}
          onRowClick={(row) => navigate(`/rfps/${row.id}`)}
          emptyMessage="No RFPs yet. Use Quick Scan to analyze your first RFP."
        />
      )}

      {/* Empty state */}
      {!isLoading && rfps.length === 0 && (
        <div className="panel p-12 text-center border-dashed">
          <FileText className="mx-auto h-12 w-12 text-text-tertiary" />
          <p className="mt-4 text-heading-sm text-text-primary">No RFPs yet</p>
          <p className="mt-2 text-text-secondary">
            Use Quick Scan to analyze RFPs from bidsandtenders.ca
          </p>
          <Link to="/quick-scan" className="mt-4 inline-block">
            <Button>Start Quick Scan</Button>
          </Link>
        </div>
      )}

      {/* Keyboard hints */}
      <div className="flex items-center justify-center gap-6 text-ui-xs text-text-tertiary">
        <span className="flex items-center gap-1.5">
          <kbd className="kbd">J</kbd>
          <kbd className="kbd">K</kbd>
          navigate
        </span>
        <span className="flex items-center gap-1.5">
          <kbd className="kbd">Space</kbd>
          select
        </span>
        <span className="flex items-center gap-1.5">
          <kbd className="kbd">Enter</kbd>
          open
        </span>
        <span className="flex items-center gap-1.5">
          <kbd className="kbd">G</kbd>
          GO
        </span>
        <span className="flex items-center gap-1.5">
          <kbd className="kbd">N</kbd>
          NO-GO
        </span>
      </div>
    </div>
  )
}
