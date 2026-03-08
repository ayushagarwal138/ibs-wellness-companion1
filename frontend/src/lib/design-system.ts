// Design System Configuration
// This file contains all design tokens and configurations to avoid hardcoding

export const colors = {
  // Primary brand colors
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },
  
  // Secondary colors
  secondary: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
  
  // Accent colors
  accent: {
    purple: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',
      600: '#9333ea',
      700: '#7c3aed',
      800: '#6b21a8',
      900: '#581c87',
    },
    orange: {
      50: '#fff7ed',
      100: '#ffedd5',
      200: '#fed7aa',
      300: '#fdba74',
      400: '#fb923c',
      500: '#f97316',
      600: '#ea580c',
      700: '#c2410c',
      800: '#9a3412',
      900: '#7c2d12',
    },
    red: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },
  },
  
  // Neutral colors
  neutral: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  
  // Status colors
  status: {
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  }
} as const;

export const typography = {
  fontFamily: {
    sans: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      'Segoe UI',
      'Roboto',
      'Oxygen',
      'Ubuntu',
      'Cantarell',
      'Fira Sans',
      'Droid Sans',
      'Helvetica Neue',
      'sans-serif'
    ],
    mono: [
      'Fira Code',
      'SF Mono',
      'Monaco',
      'Inconsolata',
      'Roboto Mono',
      'Source Code Pro',
      'Menlo',
      'Consolas',
      'DejaVu Sans Mono',
      'monospace'
    ],
    display: [
      'Cal Sans',
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      'sans-serif'
    ],
  },
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px
    '3xl': '1.875rem',  // 30px
    '4xl': '2.25rem',   // 36px
    '5xl': '3rem',      // 48px
    '6xl': '3.75rem',   // 60px
    '7xl': '4.5rem',    // 72px
    '8xl': '6rem',      // 96px
    '9xl': '8rem',      // 128px
  },
  fontWeight: {
    thin: 100,
    extralight: 200,
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },
  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0em',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
  textSizes: {
    // Semantic text sizes for consistent usage
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.33,
      fontWeight: 400,
    },
    body: {
      fontSize: '1rem',
      lineHeight: 1.5,
      fontWeight: 400,
    },
    bodyLarge: {
      fontSize: '1.125rem',
      lineHeight: 1.56,
      fontWeight: 400,
    },
    subtitle: {
      fontSize: '1.25rem',
      lineHeight: 1.4,
      fontWeight: 500,
    },
    title: {
      fontSize: '1.5rem',
      lineHeight: 1.33,
      fontWeight: 600,
    },
    headline: {
      fontSize: '2.25rem',
      lineHeight: 1.22,
      fontWeight: 700,
    },
    display: {
      fontSize: '3rem',
      lineHeight: 1.17,
      fontWeight: 800,
    },
  },
} as const;

export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
  32: '8rem',     // 128px
} as const;

export const borderRadius = {
  none: '0',
  sm: '0.125rem',   // 2px
  base: '0.25rem',  // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',
} as const;

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  glow: '0 0 20px rgb(59 130 246 / 0.15)',
  colored: '0 8px 32px rgb(59 130 246 / 0.12)',
} as const;

export const gradients = {
  primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  secondary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  success: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  warm: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  cool: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
  dark: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  light: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
  hero: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
} as const;

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

export const animations = {
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
    slower: '700ms',
  },
  
  easing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    smooth: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  },
  
  keyframes: {
    fadeIn: `
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
    `,
    slideUp: `
      @keyframes slideUp {
        from { transform: translateY(100%); }
        to { transform: translateY(0); }
      }
    `,
    scaleIn: `
      @keyframes scaleIn {
        from { transform: scale(0.9); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
      }
    `,
    float: `
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
      }
    `,
  }
} as const;

// Component-specific configurations
export const components = {
  button: {
    sizes: {
      sm: {
        padding: `${spacing[2]} ${spacing[3]}`,
        fontSize: typography.fontSize.sm,
        borderRadius: borderRadius.md,
      },
      md: {
        padding: `${spacing[3]} ${spacing[4]}`,
        fontSize: typography.fontSize.base,
        borderRadius: borderRadius.md,
      },
      lg: {
        padding: `${spacing[4]} ${spacing[6]}`,
        fontSize: typography.fontSize.lg,
        borderRadius: borderRadius.lg,
      },
    },
    
    variants: {
      primary: {
        backgroundColor: colors.primary[600],
        color: 'white',
        hoverBackgroundColor: colors.primary[700],
      },
      secondary: {
        backgroundColor: colors.secondary[600],
        color: 'white',
        hoverBackgroundColor: colors.secondary[700],
      },
      outline: {
        backgroundColor: 'transparent',
        color: colors.primary[600],
        border: `1px solid ${colors.primary[600]}`,
        hoverBackgroundColor: colors.primary[50],
      },
      ghost: {
        backgroundColor: 'transparent',
        color: colors.neutral[700],
        hoverBackgroundColor: colors.neutral[100],
      },
    }
  },
  
  card: {
    padding: spacing[6],
    borderRadius: borderRadius.xl,
    shadow: shadows.md,
    backgroundColor: 'white',
    border: `1px solid ${colors.neutral[200]}`,
  },
  
  input: {
    padding: `${spacing[3]} ${spacing[4]}`,
    borderRadius: borderRadius.md,
    border: `1px solid ${colors.neutral[300]}`,
    fontSize: typography.fontSize.base,
    focusBorderColor: colors.primary[500],
  }
} as const;

// Layout configurations
export const layout = {
  container: {
    maxWidth: '1200px',
    padding: spacing[4],
  },
  
  header: {
    height: '4rem',
    padding: `${spacing[4]} ${spacing[6]}`,
  },
  
  footer: {
    padding: `${spacing[12]} ${spacing[6]}`,
  },
  
  section: {
    padding: `${spacing[20]} 0`,
  }
} as const;

// Export utility functions
export const getColor = (colorPath: string) => {
  const keys = colorPath.split('.');
  let result: any = colors;
  
  for (const key of keys) {
    result = result[key];
    if (!result) return undefined;
  }
  
  return result;
};

export const getSpacing = (size: keyof typeof spacing) => spacing[size];
export const getFontSize = (size: keyof typeof typography.fontSize) => typography.fontSize[size];
export const getBorderRadius = (size: keyof typeof borderRadius) => borderRadius[size];
export const getShadow = (size: keyof typeof shadows) => shadows[size];