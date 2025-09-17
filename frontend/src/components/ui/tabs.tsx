'use client';

import React, { createContext, useContext, useState } from 'react';
import { colors, typography, spacing, borderRadius, animations } from '@/lib/design-system';

interface TabsContextType {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

interface TabsProps {
  defaultValue: string;
  children: React.ReactNode;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ defaultValue, children, className = '' }) => {
  const [activeTab, setActiveTab] = useState(defaultValue);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={className}>
        {children}
      </div>
    </TabsContext.Provider>
  );
};

interface TabsListProps {
  children: React.ReactNode;
  className?: string;
}

export const TabsList: React.FC<TabsListProps> = ({ children, className = '' }) => {
  return (
    <div
      className={className}
      style={{
        display: 'flex',
        backgroundColor: colors.neutral[100],
        borderRadius: borderRadius.lg,
        padding: spacing[1],
        gap: spacing[1],
      }}
    >
      {children}
    </div>
  );
};

interface TabsTriggerProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export const TabsTrigger: React.FC<TabsTriggerProps> = ({ value, children, className = '' }) => {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('TabsTrigger must be used within a Tabs component');
  }

  const { activeTab, setActiveTab } = context;
  const isActive = activeTab === value;

  return (
    <button
      className={className}
      onClick={() => setActiveTab(value)}
      style={{
        padding: `${spacing[2]} ${spacing[4]}`,
        borderRadius: borderRadius.md,
        fontSize: typography.fontSize.sm,
        fontWeight: typography.fontWeight.medium,
        border: 'none',
        cursor: 'pointer',
        transition: `all ${animations.duration.fast} ${animations.easing.smooth}`,
        backgroundColor: isActive ? 'white' : 'transparent',
        color: isActive ? colors.neutral[900] : colors.neutral[600],
        boxShadow: isActive ? '0 1px 3px rgba(0, 0, 0, 0.1)' : 'none',
      }}
    >
      {children}
    </button>
  );
};

interface TabsContentProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export const TabsContent: React.FC<TabsContentProps> = ({ value, children, className = '' }) => {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('TabsContent must be used within a Tabs component');
  }

  const { activeTab } = context;

  if (activeTab !== value) {
    return null;
  }

  return (
    <div className={className} style={{ marginTop: spacing[4] }}>
      {children}
    </div>
  );
};