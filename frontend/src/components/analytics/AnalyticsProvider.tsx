'use client'

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useAnalytics } from '@/hooks/useAnalytics';

interface AnalyticsProviderProps {
  children: React.ReactNode;
}

export default function AnalyticsProvider({ children }: AnalyticsProviderProps) {
  const pathname = usePathname();
  const { trackPageView } = useAnalytics();

  // Track page views when pathname changes
  useEffect(() => {
    if (pathname) {
      // Get page title from document or use pathname
      const pageTitle = document.title || pathname;
      trackPageView(pathname, pageTitle);
    }
  }, [pathname, trackPageView]);

  return <>{children}</>;
}