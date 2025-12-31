import clsx from 'clsx'

export interface ScoreIndicatorProps {
  label: string
  value: number // 0-100
  weight?: number // Weight percentage for the criterion
  className?: string
}

function getScoreColor(value: number): string {
  if (value >= 70) return 'bg-status-go'
  if (value >= 40) return 'bg-status-maybe'
  return 'bg-status-nogo'
}

export function ScoreIndicator({ label, value, weight, className }: ScoreIndicatorProps) {
  return (
    <div className={clsx('space-y-1', className)}>
      <div className="flex items-center justify-between text-ui-sm">
        <span className="text-text-secondary">{label}</span>
        <div className="flex items-center gap-2">
          {weight && (
            <span className="text-text-tertiary text-ui-xs">{weight}%</span>
          )}
          <span className="text-text-primary font-medium tabular-nums">{value}%</span>
        </div>
      </div>
      <div className="h-1.5 bg-surface rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-300', getScoreColor(value))}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  )
}

// Composite score card with multiple criteria
export interface ScoreCardProps {
  title: string
  totalScore: number
  criteria: Array<{
    label: string
    value: number
    weight: number
  }>
  className?: string
}

export function ScoreCard({ title, totalScore, criteria, className }: ScoreCardProps) {
  return (
    <div className={clsx('panel p-4 space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-heading-sm text-text-primary">{title}</h3>
        <div className="flex items-baseline gap-1">
          <span className={clsx(
            'text-heading-lg tabular-nums',
            totalScore >= 70 ? 'text-status-go' :
            totalScore >= 40 ? 'text-status-maybe' : 'text-status-nogo'
          )}>
            {totalScore}
          </span>
          <span className="text-text-tertiary text-ui-sm">/100</span>
        </div>
      </div>

      <div className="space-y-3">
        {criteria.map((criterion) => (
          <ScoreIndicator
            key={criterion.label}
            label={criterion.label}
            value={criterion.value}
            weight={criterion.weight}
          />
        ))}
      </div>
    </div>
  )
}

// Simple numeric score display
export interface ScoreBadgeProps {
  value: number
  max?: number
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function ScoreBadge({ value, max = 100, size = 'md', className }: ScoreBadgeProps) {
  const percentage = (value / max) * 100
  const colorClass = percentage >= 70 ? 'text-status-go' :
                     percentage >= 40 ? 'text-status-maybe' : 'text-status-nogo'

  const sizeClasses = {
    sm: 'text-ui-sm',
    md: 'text-ui-md font-medium',
    lg: 'text-heading-sm',
  }

  return (
    <span className={clsx('tabular-nums', colorClass, sizeClasses[size], className)}>
      {value}
    </span>
  )
}
