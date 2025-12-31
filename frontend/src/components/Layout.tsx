import { Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Search, FileText, Users, Command } from 'lucide-react'
import clsx from 'clsx'
import { CommandPalette, useKeyboardShortcuts } from './ui/CommandPalette'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard, shortcut: 'G D' },
  { name: 'Quick Scan', href: '/quick-scan', icon: Search, shortcut: 'G S' },
  { name: 'RFPs', href: '/rfps', icon: FileText, shortcut: 'G R' },
  { name: 'Sub-Consultants', href: '/subconsultants', icon: Users, shortcut: 'G U' },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const navigate = useNavigate()

  // Register keyboard shortcuts (two-letter "Go To" sequences)
  useKeyboardShortcuts({
    'G D': () => navigate('/'),
    'G S': () => navigate('/quick-scan'),
    'G R': () => navigate('/rfps'),
    'G U': () => navigate('/subconsultants'),
  })

  return (
    <div className="min-h-screen bg-background">
      {/* Command Palette */}
      <CommandPalette />

      {/* Sidebar - 224px (Notion standard) */}
      <div className="fixed inset-y-0 left-0 w-sidebar bg-surface border-r border-border">
        {/* Logo */}
        <div className="flex h-14 items-center px-4 border-b border-border">
          <h1 className="text-heading-sm text-text-primary">RFP Intelligence</h1>
        </div>

        {/* Navigation */}
        <nav className="mt-2 px-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-ui-base transition-colors',
                  isActive
                    ? 'bg-accent-muted text-text-primary'
                    : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
                )}
              >
                <item.icon className="h-4 w-4" />
                <span className="flex-1">{item.name}</span>
                <kbd className="kbd text-ui-xs opacity-0 group-hover:opacity-100">
                  {item.shortcut}
                </kbd>
              </Link>
            )
          })}
        </nav>

        {/* Command palette hint */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
          <button
            onClick={() => {
              // Trigger Cmd+K
              const event = new KeyboardEvent('keydown', {
                key: 'k',
                metaKey: true,
                bubbles: true,
              })
              document.dispatchEvent(event)
            }}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-md bg-surface-hover text-text-secondary hover:text-text-primary transition-colors text-ui-sm"
          >
            <Command className="h-4 w-4" />
            <span>Command palette</span>
            <kbd className="kbd ml-auto">⌘K</kbd>
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-sidebar">
        {/* Top bar */}
        <header className="sticky top-0 z-10 h-14 bg-background/80 backdrop-blur-sm border-b border-border flex items-center px-6">
          <div className="flex-1">
            {/* Breadcrumb or page title could go here */}
          </div>

          {/* Quick actions */}
          <div className="flex items-center gap-2">
            <kbd className="kbd">?</kbd>
            <span className="text-ui-xs text-text-tertiary">shortcuts</span>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
