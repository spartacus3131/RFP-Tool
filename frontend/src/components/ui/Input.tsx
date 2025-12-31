import { forwardRef, InputHTMLAttributes } from 'react'
import clsx from 'clsx'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-ui-sm font-medium text-text-secondary mb-1.5"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-tertiary">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={clsx(
              'w-full h-9 px-3 bg-surface border rounded text-ui-base text-text-primary',
              'placeholder:text-text-tertiary',
              'transition-colors duration-75',
              'hover:border-border focus:border-accent focus:ring-1 focus:ring-accent/40',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              error ? 'border-status-nogo focus:border-status-nogo focus:ring-status-nogo/40' : 'border-border',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center text-text-tertiary">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p className="mt-1.5 text-ui-sm text-status-nogo">{error}</p>
        )}
        {hint && !error && (
          <p className="mt-1.5 text-ui-sm text-text-tertiary">{hint}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }
