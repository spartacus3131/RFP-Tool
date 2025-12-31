import { forwardRef, ButtonHTMLAttributes } from 'react'
import clsx from 'clsx'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  shortcut?: string
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, shortcut, children, disabled, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium transition-colors duration-75 rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed'

    const variants = {
      primary: 'bg-accent text-white hover:bg-accent-hover active:bg-accent/90',
      secondary: 'bg-surface border border-border text-text-primary hover:bg-surface-hover active:bg-surface',
      ghost: 'text-text-secondary hover:text-text-primary hover:bg-surface-hover active:bg-surface',
      danger: 'bg-status-nogo/10 text-status-nogo border border-status-nogo/20 hover:bg-status-nogo/20 active:bg-status-nogo/15',
    }

    const sizes = {
      sm: 'h-7 px-2.5 text-ui-sm gap-1.5',
      md: 'h-8 px-3 text-ui-base gap-2',
      lg: 'h-10 px-4 text-ui-md gap-2',
    }

    return (
      <button
        ref={ref}
        className={clsx(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {children}
        {shortcut && (
          <kbd className="ml-auto kbd">{shortcut}</kbd>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button }
