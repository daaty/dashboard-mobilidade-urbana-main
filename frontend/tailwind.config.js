/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f8f9fa',
          100: '#e9ecef',
          200: '#dee2e6',
          300: '#ced4da',
          400: '#adb5bd',
          500: '#6c757d',
          600: '#495057',
          700: '#343a40',
          800: '#212529',
          900: '#1a1a1a',
        },
        success: {
          50: '#d4edda',
          100: '#c3e6cb',
          200: '#b1dfbb',
          300: '#9ed79c',
          400: '#8cc97d',
          500: '#28a745',
          600: '#238e3f',
          700: '#1e7e34',
          800: '#1c7430',
          900: '#155724',
        },
        warning: {
          50: '#fff3cd',
          100: '#ffeaa7',
          200: '#ffdd75',
          300: '#ffcf40',
          400: '#ffc107',
          500: '#e0a800',
          600: '#d39e00',
          700: '#b7950b',
          800: '#9c7e00',
          900: '#856404',
        },
        danger: {
          50: '#f8d7da',
          100: '#f1b0b7',
          200: '#ea868f',
          300: '#e35d6a',
          400: '#dc3545',
          500: '#c82333',
          600: '#bd2130',
          700: '#a71e2a',
          800: '#901e2a',
          900: '#721c24',
        },
        info: {
          50: '#d1ecf1',
          100: '#bee5eb',
          200: '#9fdbea',
          300: '#7dcde3',
          400: '#5bc0de',
          500: '#17a2b8',
          600: '#138496',
          700: '#0f6674',
          800: '#0c5460',
          900: '#0a3d47',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'sm': '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.08)',
        'lg': '0 10px 15px rgba(0, 0, 0, 0.12), 0 4px 6px rgba(0, 0, 0, 0.08)',
        'xl': '0 20px 25px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.04)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
