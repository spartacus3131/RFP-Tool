/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Core palette - Dark mode first (from DESIGN-BRIEF.md)
        background: '#1F2126',
        surface: {
          DEFAULT: '#2A2E35',
          hover: '#353A42',
          elevated: '#32373F',
        },
        // Text hierarchy
        text: {
          primary: '#F5F5F5',
          secondary: '#A7A9A9',
          tertiary: '#6B7280',
        },
        // Semantic colors
        accent: {
          DEFAULT: '#2780A0',
          hover: '#2E8FB2',
          muted: 'rgba(39, 128, 160, 0.15)',
        },
        // Status colors
        status: {
          go: '#2DB864',
          'go-bg': 'rgba(45, 184, 100, 0.15)',
          maybe: '#D4A634',
          'maybe-bg': 'rgba(212, 166, 52, 0.15)',
          nogo: '#FF5459',
          'nogo-bg': 'rgba(255, 84, 89, 0.15)',
          pending: '#6B7280',
          'pending-bg': 'rgba(107, 114, 128, 0.15)',
          info: '#3B82F6',
          'info-bg': 'rgba(59, 130, 246, 0.15)',
        },
        // Border colors
        border: {
          DEFAULT: '#3A3F47',
          subtle: '#2F333A',
          focus: 'rgba(39, 128, 160, 0.4)',
        },
      },
      fontFamily: {
        sans: ['"Inter"', '"SF Pro Display"', '-apple-system', 'system-ui', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Geist Mono"', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        // Typography scale from DESIGN-BRIEF.md
        'ui-xs': ['11px', { lineHeight: '16px', letterSpacing: '0.01em' }],
        'ui-sm': ['12px', { lineHeight: '16px', letterSpacing: '0.01em' }],
        'ui-base': ['13px', { lineHeight: '20px' }],
        'ui-md': ['14px', { lineHeight: '20px' }],
        'heading-sm': ['16px', { lineHeight: '24px', fontWeight: '600' }],
        'heading-md': ['18px', { lineHeight: '28px', fontWeight: '600' }],
        'heading-lg': ['24px', { lineHeight: '32px', fontWeight: '600' }],
        'heading-xl': ['32px', { lineHeight: '40px', fontWeight: '700' }],
      },
      spacing: {
        // 8px grid with 4px half-steps
        '0.5': '2px',
        '1': '4px',
        '1.5': '6px',
        '2': '8px',
        '2.5': '10px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
        // Sidebar width (Notion standard)
        'sidebar': '224px',
      },
      borderRadius: {
        'sm': '4px',
        'DEFAULT': '6px',
        'md': '8px',
        'lg': '12px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.3)',
        'DEFAULT': '0 2px 4px rgba(0, 0, 0, 0.3)',
        'md': '0 4px 8px rgba(0, 0, 0, 0.4)',
        'lg': '0 8px 16px rgba(0, 0, 0, 0.4)',
        'focus': '0 0 0 2px rgba(39, 128, 160, 0.4)',
      },
      animation: {
        'fade-in': 'fadeIn 150ms ease-out',
        'slide-up': 'slideUp 150ms ease-out',
        'slide-down': 'slideDown 150ms ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      // Row heights for data tables
      height: {
        'row-sm': '32px',
        'row-md': '40px',
        'row-lg': '48px',
      },
    },
  },
  plugins: [],
}
