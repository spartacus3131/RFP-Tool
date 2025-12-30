import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Search, CheckCircle, AlertCircle, HelpCircle, Loader2, Calendar, Building, FileText } from 'lucide-react'
import { quickScan } from '../api/client'
import clsx from 'clsx'

interface QuickScanResult {
  success: boolean
  error?: string
  rfp_number?: string
  client_name?: string
  opportunity_title?: string
  published_date?: string
  question_deadline?: string
  submission_deadline?: string
  contract_duration?: string
  scope_summary?: string
  category?: string
  eligibility_notes?: string
  trade_agreements?: string
  recommendation?: string
  recommendation_reasons?: string[]
  source_url: string
  scraped_at: string
  rfp_id?: string
}

export default function QuickScan() {
  const [url, setUrl] = useState('')

  const scanMutation = useMutation({
    mutationFn: (url: string) => quickScan.scan(url),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) {
      scanMutation.mutate(url.trim())
    }
  }

  const result = scanMutation.data as QuickScanResult | undefined

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Quick Scan</h1>
        <p className="mt-1 text-gray-600">
          Paste a bidsandtenders.ca URL to instantly triage an RFP before downloading documents.
        </p>
      </div>

      {/* URL Input */}
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-4">
          <div className="flex-1">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://durham.bidsandtenders.ca/Module/Tenders/en/Tender/Detail/..."
              className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={scanMutation.isPending || !url.trim()}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700 disabled:bg-gray-400"
          >
            {scanMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            Scan
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Supported: bidsandtenders.ca domains (Durham, York, Peel, Toronto, Ottawa, Hamilton)
        </p>
      </form>

      {/* Error State */}
      {scanMutation.isError && (
        <div className="mb-8 rounded-lg bg-red-50 p-4 text-red-700">
          <p className="font-medium">Scan failed</p>
          <p className="text-sm">{(scanMutation.error as Error).message}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Recommendation Banner */}
          <RecommendationBanner
            recommendation={result.recommendation}
            reasons={result.recommendation_reasons}
            error={result.error}
          />

          {/* Main Info Card */}
          {result.success && (
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <div className="mb-6">
                <div className="flex items-start justify-between">
                  <div>
                    {result.rfp_number && (
                      <span className="inline-block rounded bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 mb-2">
                        {result.rfp_number}
                      </span>
                    )}
                    <h2 className="text-xl font-semibold text-gray-900">
                      {result.opportunity_title || 'Untitled RFP'}
                    </h2>
                    {result.client_name && (
                      <p className="mt-1 flex items-center gap-2 text-gray-600">
                        <Building className="h-4 w-4" />
                        {result.client_name}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Key Dates */}
              <div className="mb-6 grid grid-cols-3 gap-4">
                <DateCard
                  label="Published"
                  value={result.published_date}
                />
                <DateCard
                  label="Questions Due"
                  value={result.question_deadline}
                />
                <DateCard
                  label="Submission Deadline"
                  value={result.submission_deadline}
                  highlight
                />
              </div>

              {/* Details */}
              <div className="space-y-4 border-t border-gray-100 pt-4">
                {result.scope_summary && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Scope Summary</h3>
                    <p className="mt-1 text-gray-900">{result.scope_summary}</p>
                  </div>
                )}

                {result.category && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Category</h3>
                    <p className="mt-1 text-gray-900">{result.category}</p>
                  </div>
                )}

                {result.contract_duration && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Contract Duration</h3>
                    <p className="mt-1 text-gray-900">{result.contract_duration}</p>
                  </div>
                )}

                {result.eligibility_notes && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Eligibility Notes</h3>
                    <p className="mt-1 text-gray-900">{result.eligibility_notes}</p>
                  </div>
                )}

                {result.trade_agreements && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Trade Agreements</h3>
                    <p className="mt-1 text-gray-900">{result.trade_agreements}</p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="mt-6 flex gap-4 border-t border-gray-100 pt-4">
                <a
                  href={result.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  <FileText className="h-4 w-4" />
                  View Original
                </a>
                {result.rfp_id && (
                  <span className="flex items-center gap-2 text-sm text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    Saved to database
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function RecommendationBanner({
  recommendation,
  reasons,
  error,
}: {
  recommendation?: string
  reasons?: string[]
  error?: string
}) {
  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-6 w-6 text-red-600" />
          <div>
            <h3 className="font-medium text-red-800">Scan Error</h3>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  const config = {
    GO: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      icon: CheckCircle,
      iconColor: 'text-green-600',
      titleColor: 'text-green-800',
      textColor: 'text-green-700',
    },
    MAYBE: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      icon: HelpCircle,
      iconColor: 'text-yellow-600',
      titleColor: 'text-yellow-800',
      textColor: 'text-yellow-700',
    },
    NO_GO: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: AlertCircle,
      iconColor: 'text-red-600',
      titleColor: 'text-red-800',
      textColor: 'text-red-700',
    },
  }

  const c = config[recommendation as keyof typeof config] || config.MAYBE
  const Icon = c.icon

  return (
    <div className={clsx('rounded-lg border p-4', c.bg, c.border)}>
      <div className="flex items-start gap-3">
        <Icon className={clsx('h-6 w-6', c.iconColor)} />
        <div>
          <h3 className={clsx('font-medium', c.titleColor)}>
            Recommendation: {recommendation}
          </h3>
          {reasons && reasons.length > 0 && (
            <ul className={clsx('mt-2 space-y-1 text-sm', c.textColor)}>
              {reasons.map((reason, i) => (
                <li key={i}>• {reason}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

function DateCard({
  label,
  value,
  highlight,
}: {
  label: string
  value?: string
  highlight?: boolean
}) {
  return (
    <div
      className={clsx(
        'rounded-lg border p-3',
        highlight ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'
      )}
    >
      <p className="text-xs font-medium text-gray-500">{label}</p>
      <p
        className={clsx(
          'mt-1 flex items-center gap-2 text-sm font-medium',
          highlight ? 'text-blue-700' : 'text-gray-900'
        )}
      >
        <Calendar className="h-4 w-4" />
        {value || 'Not specified'}
      </p>
    </div>
  )
}
