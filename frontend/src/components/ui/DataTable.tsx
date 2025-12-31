import { useState, useMemo } from 'react'
import clsx from 'clsx'
import { ChevronUp, ChevronDown, MoreHorizontal, Check } from 'lucide-react'

export interface Column<T> {
  key: string
  header: string
  width?: string // e.g., '100px', 'flex', '20%'
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  render?: (row: T, index: number) => React.ReactNode
}

export interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyField: keyof T
  selectable?: boolean
  selectedIds?: Set<string>
  onSelectionChange?: (ids: Set<string>) => void
  onRowClick?: (row: T) => void
  emptyMessage?: string
  className?: string
  rowHeight?: 'sm' | 'md' | 'lg'
}

type SortDirection = 'asc' | 'desc' | null

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  keyField,
  selectable = false,
  selectedIds = new Set(),
  onSelectionChange,
  onRowClick,
  emptyMessage = 'No data',
  className,
  rowHeight = 'md',
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>(null)

  const handleSort = (key: string) => {
    if (sortKey === key) {
      if (sortDirection === 'asc') setSortDirection('desc')
      else if (sortDirection === 'desc') {
        setSortKey(null)
        setSortDirection(null)
      }
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  const sortedData = useMemo(() => {
    if (!sortKey || !sortDirection) return data
    return [...data].sort((a, b) => {
      const aVal = a[sortKey]
      const bVal = b[sortKey]
      if (aVal === bVal) return 0
      if (aVal === null || aVal === undefined) return 1
      if (bVal === null || bVal === undefined) return -1
      const comparison = aVal < bVal ? -1 : 1
      return sortDirection === 'asc' ? comparison : -comparison
    })
  }, [data, sortKey, sortDirection])

  const handleSelectAll = () => {
    if (selectedIds.size === data.length) {
      onSelectionChange?.(new Set())
    } else {
      onSelectionChange?.(new Set(data.map((row) => String(row[keyField]))))
    }
  }

  const handleSelectRow = (id: string) => {
    const newSelection = new Set(selectedIds)
    if (newSelection.has(id)) {
      newSelection.delete(id)
    } else {
      newSelection.add(id)
    }
    onSelectionChange?.(newSelection)
  }

  const rowHeightClass = {
    sm: 'h-row-sm',
    md: 'h-row-md',
    lg: 'h-row-lg',
  }[rowHeight]

  const alignClass = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
  }

  if (data.length === 0) {
    return (
      <div className={clsx('panel p-8 text-center', className)}>
        <p className="text-text-tertiary">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className={clsx('panel overflow-hidden', className)}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-surface-hover border-b border-border">
            <tr>
              {selectable && (
                <th className="w-10 px-3">
                  <Checkbox
                    checked={selectedIds.size === data.length}
                    indeterminate={selectedIds.size > 0 && selectedIds.size < data.length}
                    onChange={handleSelectAll}
                  />
                </th>
              )}
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={clsx(
                    'px-3 py-2 text-ui-xs font-medium text-text-secondary uppercase tracking-wide',
                    alignClass[col.align || 'left'],
                    col.sortable && 'cursor-pointer select-none hover:text-text-primary'
                  )}
                  style={{ width: col.width }}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.header}
                    {col.sortable && sortKey === col.key && (
                      sortDirection === 'asc' ? (
                        <ChevronUp className="w-3 h-3" />
                      ) : (
                        <ChevronDown className="w-3 h-3" />
                      )
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            {sortedData.map((row, index) => {
              const rowId = String(row[keyField])
              const isSelected = selectedIds.has(rowId)
              return (
                <tr
                  key={rowId}
                  className={clsx(
                    'row-hover',
                    rowHeightClass,
                    isSelected && 'bg-accent-muted',
                    onRowClick && 'cursor-pointer'
                  )}
                  onClick={() => onRowClick?.(row)}
                >
                  {selectable && (
                    <td className="w-10 px-3" onClick={(e) => e.stopPropagation()}>
                      <Checkbox
                        checked={isSelected}
                        onChange={() => handleSelectRow(rowId)}
                      />
                    </td>
                  )}
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={clsx(
                        'px-3 py-2 text-ui-base',
                        alignClass[col.align || 'left']
                      )}
                    >
                      {col.render ? col.render(row, index) : row[col.key]}
                    </td>
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Checkbox component for table selection
interface CheckboxProps {
  checked: boolean
  indeterminate?: boolean
  onChange: () => void
}

function Checkbox({ checked, indeterminate, onChange }: CheckboxProps) {
  return (
    <button
      role="checkbox"
      aria-checked={indeterminate ? 'mixed' : checked}
      onClick={(e) => {
        e.stopPropagation()
        onChange()
      }}
      className={clsx(
        'w-4 h-4 rounded border flex items-center justify-center transition-colors',
        checked || indeterminate
          ? 'bg-accent border-accent text-white'
          : 'bg-transparent border-border hover:border-text-tertiary'
      )}
    >
      {checked && <Check className="w-3 h-3" />}
      {indeterminate && !checked && (
        <div className="w-2 h-0.5 bg-white rounded" />
      )}
    </button>
  )
}

// Action menu for row actions
export interface ActionMenuItem {
  label: string
  icon?: React.ReactNode
  onClick: () => void
  danger?: boolean
  shortcut?: string
}

export interface ActionsMenuProps {
  items: ActionMenuItem[]
}

export function ActionsMenu({ items }: ActionsMenuProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={(e) => {
          e.stopPropagation()
          setOpen(!open)
        }}
        className="p-1 rounded hover:bg-surface-hover text-text-tertiary hover:text-text-secondary"
      >
        <MoreHorizontal className="w-4 h-4" />
      </button>

      {open && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 top-full mt-1 z-20 min-w-[160px] panel py-1 shadow-lg animate-fade-in">
            {items.map((item, index) => (
              <button
                key={index}
                onClick={(e) => {
                  e.stopPropagation()
                  item.onClick()
                  setOpen(false)
                }}
                className={clsx(
                  'w-full px-3 py-1.5 text-ui-sm text-left flex items-center gap-2 hover:bg-surface-hover',
                  item.danger ? 'text-status-nogo' : 'text-text-primary'
                )}
              >
                {item.icon}
                <span className="flex-1">{item.label}</span>
                {item.shortcut && (
                  <kbd className="kbd text-ui-xs">{item.shortcut}</kbd>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
