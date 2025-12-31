import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Search, CheckCircle, AlertCircle, HelpCircle, Loader2, Calendar, Building, FileText, ExternalLink } from 'lucide-react'
import { quickScan } from '../api/client'
import clsx from 'clsx'
import { Button, Input, Badge, RecommendationBadge, ScoreCard } from '../components/ui'

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
  recommendation?: 'GO' | 'MAYBE' | 'NO_GO'
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
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-heading-lg text-text-primary">Quick Scan</h1>
        <p className="mt-1 text-ui-base text-text-secondary">
          Paste a bidsandtenders.ca URL to instantly triage an RFP before downloading documents.
        </p>
      </div>

      {/* URL Input */}
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-3">
          <div className="flex-1">
            <Input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://durham.bidsandtenders.ca/Module/Tenders/en/Tender/Detail/..."
              leftIcon={<Search className="h-4 w-4" />}
            />
          </div>
          <Button
            type="submit"
            disabled={scanMutation.isPending || !url.trim()}
            loading={scanMutation.isPending}
          >
            {!scanMutation.isPending && <Search className="h-4 w-4" />}
            Scan
          </Button>
        </div>
        <p className="mt-2 text-ui-xs text-text-tertiary">
          Supported: bidsandtenders.ca domains (Durham, York, Peel, Toronto, Ottawa, Hamilton)
        </p>
      </form>

      {/* Error State */}
      {scanMutation.isError && (
        <div className="mb-8 panel p-4 border-status-nogo/20 bg-status-nogo-bg">
          <p className="font-medium text-status-nogo">Scan failed</p>
          <p className="text-ui-sm text-status-nogo/80">{(scanMutation.error as Error).message}</p>
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
            <div className="panel p-6">
              <div className="mb-6">
                <div className="flex items-start justify-between">
                  <div>
                    {result.rfp_number && (
                      <span className="inline-block font-mono text-ui-sm text-text-tertiary mb-2">
                        {result.rfp_number}
                      </span>
                    )}
                    <h2 className="text-heading-md text-text-primary">
                      {result.opportunity_title || 'Untitled RFP'}
                    </h2>
                    {result.client_name && (
                      <p className="mt-1 flex items-center gap-2 text-text-secondary">
                        <Building className="h-4 w-4" />
                        {result.client_name}
                      </p>
                    )}
                  </div>
                  {result.recommendation && (
                    <RecommendationBadge recommendation={result.recommendation} />
                  )}
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
              <div className="space-y-4 border-t border-border pt-4">
                {result.scope_summary && (
                  <div>
                    <h3 className="text-ui-sm font-medium text-text-tertiary">Scope Summary</h3>
                    <p className="mt-1 text-text-primary">{result.scope_summary}</p>
                  </div>
                )}

                {result.category && (
                  <div>
                    <h3 className="text-ui-sm font-medium text-text-tertiary">Category</h3>
                    <p className="mt-1 text-text-primary">{result.category}</p>
                  </div>
                )}

                {result.contract_duration && (
                  <div>
                    <h3 className="text-ui-sm font-medium text-text-tertiary">Contract Duration</h3>
                    <p className="mt-1 text-text-primary">{result.contract_duration}</p>
                  </div>
                )}

                {result.eligibility_notes && (
                  <div>
                    <h3 className="text-ui-sm font-medium text-text-tertiary">Eligibility Notes</h3>
                    <p className="mt-1 text-text-primary">{result.eligibility_notes}</p>
                  </div>
                )}

                {result.trade_agreements && (
                  <div>
                    <h3 className="text-ui-sm font-medium text-text-tertiary">Trade Agreements</h3>
                    <p className="mt-1 text-text-primary">{result.trade_agreements}</p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="mt-6 flex items-center gap-4 border-t border-border pt-4">
                <a
                  href={result.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Button variant="secondary">
                    <ExternalLink className="h-4 w-4" />
                    View Original
                  </Button>
                </a>
                {result.rfp_id && (
                  <span className="flex items-center gap-2 text-ui-sm text-status-go">
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
  recommendation?: 'GO' | 'MAYBE' | 'NO_GO'
  reasons?: string[]
  error?: string
}) {
  if (error) {
    return (
      <div className="panel p-4 border-status-nogo/20 bg-status-nogo-bg">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-6 w-6 text-status-nogo" />
          <div>
            <h3 className="font-medium text-status-nogo">Scan Error</h3>
            <p className="text-ui-sm text-status-nogo/80">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  const config = {
    GO: {
      bg: 'bg-status-go-bg',
      border: 'border-status-go/20',
      icon: CheckCircle,
      iconColor: 'text-status-go',
      titleColor: 'text-status-go',
      textColor: 'text-text-secondary',
    },
    MAYBE: {
      bg: 'bg-status-maybe-bg',
      border: 'border-status-maybe/20',
      icon: HelpCircle,
      iconColor: 'text-status-maybe',
      titleColor: 'text-status-maybe',
      textColor: 'text-text-secondary',
    },
    NO_GO: {
      bg: 'bg-status-nogo-bg',
      border: 'border-status-nogo/20',
      icon: AlertCircle,
      iconColor: 'text-status-nogo',
      titleColor: 'text-status-nogo',
      textColor: 'text-text-secondary',
    },
  }

  const c = config[recommendation as keyof typeof config] || config.MAYBE
  const Icon = c.icon

  return (
    <div className={clsx('panel p-4 border', c.bg, c.border)}>
      <div className="flex items-start gap-3">
        <Icon className={clsx('h-6 w-6', c.iconColor)} />
        <div>
          <h3 className={clsx('font-medium', c.titleColor)}>
            Recommendation: {recommendation?.replace('_', '-')}
          </h3>
          {reasons && reasons.length > 0 && (
            <ul className={clsx('mt-2 space-y-1 text-ui-sm', c.textColor)}>
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
        'panel p-3',
        highlight && 'border-accent/30 bg-accent-muted'
      )}
    >
      <p className="text-ui-xs font-medium text-text-tertiary">{label}</p>
      <p
        className={clsx(
          'mt-1 flex items-center gap-2 text-ui-sm font-medium',
          highlight ? 'text-accent' : 'text-text-primary'
        )}
      >
        <Calendar className="h-4 w-4" />
        {value || 'Not specified'}
      </p>
    </div>
  )
}
