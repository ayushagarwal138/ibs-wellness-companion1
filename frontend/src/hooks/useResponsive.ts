'use client';

import { useState, useEffect } from 'react';

// Breakpoint definitions
const breakpoints = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

type Breakpoint = keyof typeof breakpoints;

interface ResponsiveState {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  currentBreakpoint: Breakpoint;
}

// Safe defaults for SSR
const getDefaultState = (): ResponsiveState => ({
  width: 1024, // Default to desktop width
  height: 768,
  isMobile: false,
  isTablet: false,
  isDesktop: true,
  currentBreakpoint: 'lg',
});

// Check if we're in a browser environment
const isBrowser = typeof window !== 'undefined';

export const useResponsive = (): ResponsiveState => {
  const [state, setState] = useState<ResponsiveState>(() => {
    if (!isBrowser) {
      return getDefaultState();
    }

    const width = window.innerWidth;
    const height = window.innerHeight;

    return {
      width,
      height,
      isMobile: width < breakpoints.md,
      isTablet: width >= breakpoints.md && width < breakpoints.lg,
      isDesktop: width >= breakpoints.lg,
      currentBreakpoint: getCurrentBreakpoint(width),
    };
  });

  useEffect(() => {
    if (!isBrowser) return;

    const handleResize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;

      setState({
        width,
        height,
        isMobile: width < breakpoints.md,
        isTablet: width >= breakpoints.md && width < breakpoints.lg,
        isDesktop: width >= breakpoints.lg,
        currentBreakpoint: getCurrentBreakpoint(width),
      });
    };

    // Debounce resize events
    let timeoutId: NodeJS.Timeout;
    const debouncedHandleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleResize, 150);
    };

    window.addEventListener('resize', debouncedHandleResize);
    
    // Call once to set initial state after hydration
    handleResize();

    return () => {
      window.removeEventListener('resize', debouncedHandleResize);
      clearTimeout(timeoutId);
    };
  }, []);

  return state;
};

function getCurrentBreakpoint(width: number): Breakpoint | 'xs' {
  if (width >= breakpoints['2xl']) return '2xl';
  if (width >= breakpoints.xl) return 'xl';
  if (width >= breakpoints.lg) return 'lg';
  if (width >= breakpoints.md) return 'md';
  if (width >= breakpoints.sm) return 'sm';
  return 'xs';
}

// Hook for checking specific breakpoints
export const useBreakpoint = (breakpoint: Breakpoint): boolean => {
  const [matches, setMatches] = useState(() => {
    if (!isBrowser) {
      // Default to desktop breakpoint for SSR
      return breakpoint === 'lg' || breakpoint === 'xl' || breakpoint === '2xl';
    }
    return window.innerWidth >= breakpoints[breakpoint];
  });

  useEffect(() => {
    if (!isBrowser) return;

    const checkBreakpoint = () => {
      setMatches(window.innerWidth >= breakpoints[breakpoint]);
    };

    checkBreakpoint();
    window.addEventListener('resize', checkBreakpoint);

    return () => window.removeEventListener('resize', checkBreakpoint);
  }, [breakpoint]);

  return matches;
 };

// Hook for checking if current screen is between two breakpoints
export const useBreakpointRange = (
  min: Breakpoint | 'xs',
  max: Breakpoint | 'xs'
): boolean => {
  const { width } = useResponsive();
  
  const minWidth = min === 'xs' ? 0 : breakpoints[min as Breakpoint];
  const maxWidth = max === 'xs' ? breakpoints.sm - 1 : breakpoints[max as Breakpoint] - 1;
  
  return width >= minWidth && width <= maxWidth;
};

// Hook for responsive values
export const useResponsiveValue = <T>(values: {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
  '2xl'?: T;
}): T | undefined => {
  const { currentBreakpoint } = useResponsive();
  
  // Find the appropriate value based on current breakpoint
  const breakpointOrder: (Breakpoint | 'xs')[] = ['2xl', 'xl', 'lg', 'md', 'sm', 'xs'];
  const currentIndex = breakpointOrder.indexOf(currentBreakpoint);
  
  // Look for the value starting from current breakpoint and going down
  for (let i = currentIndex; i < breakpointOrder.length; i++) {
    const bp = breakpointOrder[i];
    const value = values[bp as keyof typeof values];
    if (value !== undefined) {
      return value;
    }
  }
  
  return undefined;
};

// Hook for responsive grid columns
export const useResponsiveColumns = (config: {
  xs?: number;
  sm?: number;
  md?: number;
  lg?: number;
  xl?: number;
  '2xl'?: number;
}): number => {
  const columns = useResponsiveValue(config);
  return columns || 1;
};

// Hook for responsive spacing
export const useResponsiveSpacing = (config: {
  xs?: string;
  sm?: string;
  md?: string;
  lg?: string;
  xl?: string;
  '2xl'?: string;
}): string => {
  const spacing = useResponsiveValue(config);
  return spacing || '1rem';
};

// Hook for orientation detection
export const useOrientation = () => {
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>(() => {
    if (typeof window === 'undefined') return 'landscape';
    return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleOrientationChange = () => {
      setOrientation(window.innerHeight > window.innerWidth ? 'portrait' : 'landscape');
    };

    window.addEventListener('resize', handleOrientationChange);
    window.addEventListener('orientationchange', handleOrientationChange);

    return () => {
      window.removeEventListener('resize', handleOrientationChange);
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, []);

  return orientation;
};

// Hook for detecting touch devices
export const useTouchDevice = (): boolean => {
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const checkTouchDevice = () => {
      setIsTouchDevice(
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        // @ts-ignore
        navigator.msMaxTouchPoints > 0
      );
    };

    checkTouchDevice();
  }, []);

  return isTouchDevice;
};

// Hook for responsive font sizes
export const useResponsiveFontSize = (config: {
  xs?: string;
  sm?: string;
  md?: string;
  lg?: string;
  xl?: string;
  '2xl'?: string;
}): string => {
  const fontSize = useResponsiveValue(config);
  return fontSize || '1rem';
};

// Hook for responsive container width
export const useResponsiveContainer = (): string => {
  const { currentBreakpoint } = useResponsive();
  
  const containerWidths = {
    xs: '100%',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  };
  
  return containerWidths[currentBreakpoint];
};