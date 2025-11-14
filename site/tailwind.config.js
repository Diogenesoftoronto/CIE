/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'serif': ['Times New Roman', 'Times', 'serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        distill: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        }
      },
      typography: {
        'distill': {
          css: {
            '--tw-prose-body': '#334155',
            '--tw-prose-headings': '#0f172a',
            '--tw-prose-links': '#3b82f6',
            '--tw-prose-bold': '#0f172a',
            '--tw-prose-counters': '#64748b',
            '--tw-prose-bullets': '#cbd5e1',
            '--tw-prose-hr': '#e2e8f0',
            '--tw-prose-quotes': '#334155',
            '--tw-prose-quote-borders': '#e2e8f0',
            '--tw-prose-captions': '#64748b',
            '--tw-prose-code': '#0f172a',
            '--tw-prose-pre-code': '#f8fafc',
            '--tw-prose-pre-bg': '#0f172a',
            '--tw-prose-th-borders': '#cbd5e1',
            '--tw-prose-td-borders': '#e2e8f0',
          }
        }
      }
    },
  },
  plugins: [],
}