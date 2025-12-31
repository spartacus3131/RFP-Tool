import clsx from 'clsx'

export interface BadgeProps {
  variant?: 'default' | 'go' | 'maybe' | 'nogo' | 'pending' | 'info'
  size?: 'sm' | 'md'
  dot?: boolean
  children: React.ReactNode
  className?: string
}

const variantStyles = {
  default: 'bg-surface text-text-secondary border-border',
  go: 'bg-status-go-bg text-status-go border-status-go/20',
  maybe: 'bg-status-maybe-bg text-status-maybe border-status-maybe/20',
  nogo: 'bg-status-nogo-bg text-status-nogo border-status-nogo/20',
  pending: 'bg-status-pending-bg text-status-pending border-status-pending/20',
  info: 'bg-status-info-bg text-status-info border-status-info/20',
}

const dotColors = {
  default: 'bg-text-secondary',
  go: 'bg-status-go',
  maybe: 'bg-status-maybe',
  nogo: 'bg-status-nogo',
  pending: 'bg-status-pending',
  info: 'bg-status-info',
}

export function Badge({
  variant = 'default',
  size = 'sm',
  dot = false,
  children,
  className,
}: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium border rounded',
        size === 'sm' ? 'px-1.5 py-0.5 text-ui-xs gap-1' : 'px-2 py-1 text-ui-sm gap-1.5',
        variantStyles[variant],
        className
      )}
    >
      {dot && (
        <span className={clsx('w-1.5 h-1.5 rounded-full', dotColors[variant])} />
      )}
      {children}
    </span>
  )
}

// Specialized status badge for Go/No-Go decisions
export interface StatusBadgeProps {
  status: 'new' | 'processing' | 'extracted' | 'reviewed' | 'go' | 'no_go' | 'pending'
  className?: string
}

const statusConfig: Record<string, { label: string; variant: BadgeProps['variant'] }> = {
  new: { label: 'NEW', variant: 'pending' },
  processing: { label: 'PROCESSING', variant: 'info' },
  extracted: { label: 'EXTRACTED', variant: 'info' },
  reviewed: { label: 'REVIEWED', variant: 'maybe' },
  go: { label: 'GO', variant: 'go' },
  no_go: { label: 'NO-GO', variant: 'nogo' },
  pending: { label: 'PENDING', variant: 'pending' },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.pending
  return (
    <Badge variant={config.variant} dot className={className}>
      {config.label}
    </Badge>
  )
}

// Recommendation badge for AI suggestions
export interface RecommendationBadgeProps {
  recommendation: 'GO' | 'MAYBE' | 'NO_GO'
  confidence?: number
  className?: string
}

const recommendationConfig: Record<string, { variant: BadgeProps['variant'] }> = {
  GO: { variant: 'go' },
  MAYBE: { variant: 'maybe' },
  NO_GO: { variant: 'nogo' },
}

export function RecommendationBadge({ recommendation, confidence, className }: RecommendationBadgeProps) {
  const config = recommendationConfig[recommendation] || recommendationConfig.MAYBE
  return (
    <Badge variant={config.variant} size="md" className={className}>
      {recommendation.replace('_', '-')}
      {confidence !== undefined && (
        <span className="ml-1 opacity-75">{confidence}%</span>
      )}
    </Badge>
  )
}
