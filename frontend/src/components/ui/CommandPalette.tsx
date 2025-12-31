import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import clsx from 'clsx'
import {
  Search,
  LayoutDashboard,
  FileText,
  Users,
  ScanSearch,
  Settings,
  Plus,
  ArrowRight,
} from 'lucide-react'

interface Command {
  id: string
  label: string
  shortcut?: string
  icon?: React.ReactNode
  action: () => void
  section?: string
}

interface CommandPaletteProps {
  commands?: Command[]
}

export function CommandPalette({ commands: customCommands }: CommandPaletteProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  // Default navigation commands
  const defaultCommands: Command[] = [
    {
      id: 'dashboard',
      label: 'Go to Dashboard',
      shortcut: 'G D',
      icon: <LayoutDashboard className="w-4 h-4" />,
      action: () => navigate('/'),
      section: 'Navigation',
    },
    {
      id: 'quick-scan',
      label: 'Quick Scan URL',
      shortcut: 'G S',
      icon: <ScanSearch className="w-4 h-4" />,
      action: () => navigate('/quick-scan'),
      section: 'Navigation',
    },
    {
      id: 'rfps',
      label: 'Go to RFPs',
      shortcut: 'G R',
      icon: <FileText className="w-4 h-4" />,
      action: () => navigate('/rfps'),
      section: 'Navigation',
    },
    {
      id: 'subconsultants',
      label: 'Go to Sub-Consultants',
      shortcut: 'G U',
      icon: <Users className="w-4 h-4" />,
      action: () => navigate('/subconsultants'),
      section: 'Navigation',
    },
    {
      id: 'new-rfp',
      label: 'New RFP from URL',
      shortcut: 'N',
      icon: <Plus className="w-4 h-4" />,
      action: () => navigate('/quick-scan'),
      section: 'Actions',
    },
  ]

  const allCommands = [...defaultCommands, ...(customCommands || [])]

  const filteredCommands = query
    ? allCommands.filter((cmd) =>
        cmd.label.toLowerCase().includes(query.toLowerCase())
      )
    : allCommands

  // Group commands by section
  const groupedCommands = filteredCommands.reduce((groups, cmd) => {
    const section = cmd.section || 'Other'
    if (!groups[section]) groups[section] = []
    groups[section].push(cmd)
    return groups
  }, {} as Record<string, Command[]>)

  // Flatten for keyboard navigation
  const flatCommands = Object.values(groupedCommands).flat()

  // Keyboard shortcut to open (Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setOpen(true)
      }
      if (e.key === 'Escape') {
        setOpen(false)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Focus input when opening
  useEffect(() => {
    if (open) {
      inputRef.current?.focus()
      setQuery('')
      setSelectedIndex(0)
    }
  }, [open])

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex((i) => (i + 1) % flatCommands.length)
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex((i) => (i - 1 + flatCommands.length) % flatCommands.length)
          break
        case 'Enter':
          e.preventDefault()
          if (flatCommands[selectedIndex]) {
            flatCommands[selectedIndex].action()
            setOpen(false)
          }
          break
      }
    },
    [flatCommands, selectedIndex]
  )

  // Reset selection when filtered results change
  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => setOpen(false)}
      />

      {/* Dialog */}
      <div className="absolute left-1/2 top-[20%] -translate-x-1/2 w-full max-w-lg">
        <div className="panel shadow-lg overflow-hidden animate-slide-down">
          {/* Search input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
            <Search className="w-5 h-5 text-text-tertiary" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search commands..."
              className="flex-1 bg-transparent text-text-primary placeholder:text-text-tertiary outline-none text-ui-md"
            />
            <kbd className="kbd">esc</kbd>
          </div>

          {/* Results */}
          <div className="max-h-80 overflow-y-auto py-2">
            {flatCommands.length === 0 ? (
              <div className="px-4 py-8 text-center text-text-tertiary">
                No commands found
              </div>
            ) : (
              Object.entries(groupedCommands).map(([section, commands]) => (
                <div key={section}>
                  <div className="px-4 py-1.5 text-ui-xs text-text-tertiary font-medium uppercase tracking-wide">
                    {section}
                  </div>
                  {commands.map((cmd) => {
                    const globalIndex = flatCommands.indexOf(cmd)
                    const isSelected = globalIndex === selectedIndex
                    return (
                      <button
                        key={cmd.id}
                        onClick={() => {
                          cmd.action()
                          setOpen(false)
                        }}
                        onMouseEnter={() => setSelectedIndex(globalIndex)}
                        className={clsx(
                          'w-full px-4 py-2 flex items-center gap-3 text-left transition-colors',
                          isSelected ? 'bg-surface-hover text-text-primary' : 'text-text-secondary hover:bg-surface-hover'
                        )}
                      >
                        <span className="text-text-tertiary">{cmd.icon}</span>
                        <span className="flex-1 text-ui-base">{cmd.label}</span>
                        {cmd.shortcut && (
                          <kbd className="kbd">{cmd.shortcut}</kbd>
                        )}
                        {isSelected && (
                          <ArrowRight className="w-4 h-4 text-accent" />
                        )}
                      </button>
                    )
                  })}
                </div>
              ))
            )}
          </div>

          {/* Footer hint */}
          <div className="px-4 py-2 border-t border-border text-ui-xs text-text-tertiary flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="kbd">↑↓</kbd> navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="kbd">↵</kbd> select
            </span>
            <span className="flex items-center gap-1">
              <kbd className="kbd">esc</kbd> close
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Hook for registering keyboard shortcuts
export function useKeyboardShortcuts(shortcuts: Record<string, () => void>) {
  useEffect(() => {
    const keys: string[] = []
    let timeout: number | null = null

    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return
      }

      // Clear previous keys after delay
      if (timeout) clearTimeout(timeout)
      timeout = window.setTimeout(() => {
        keys.length = 0
      }, 500)

      keys.push(e.key.toUpperCase())
      const combo = keys.join(' ')

      // Check for matching shortcut
      for (const [shortcut, action] of Object.entries(shortcuts)) {
        if (combo === shortcut || combo.endsWith(shortcut)) {
          e.preventDefault()
          action()
          keys.length = 0
          break
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      if (timeout) clearTimeout(timeout)
    }
  }, [shortcuts])
}
