'use client';

import React from 'react';
import { colors, borderRadius } from '@/lib/design-system';

interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  className = '',
  size = 'md',
  variant = 'default',
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return { height: '4px' };
      case 'lg':
        return { height: '12px' };
      default:
        return { height: '8px' };
    }
  };

  const getVariantColor = () => {
    switch (variant) {
      case 'success':
        return colors.secondary[500];
      case 'warning':
        return colors.accent.orange[500];
      case 'error':
        return colors.accent.red[500];
      default:
        return colors.primary[500];
    }
  };

  return (
    <div
      className={className}
      style={{
        width: '100%',
        backgroundColor: colors.neutral[200],
        borderRadius: borderRadius.full,
        overflow: 'hidden',
        ...getSizeStyles(),
      }}
    >
      <div
        style={{
          height: '100%',
          backgroundColor: getVariantColor(),
          borderRadius: borderRadius.full,
          width: `${percentage}%`,
          transition: 'width 0.3s ease-in-out',
        }}
      />
    </div>
  );
};