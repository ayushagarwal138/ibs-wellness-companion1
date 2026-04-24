'use client';

import React from 'react';
import { colors, typography, spacing, borderRadius } from '@/lib/design-system';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'secondary':
        return {
          backgroundColor: colors.neutral[100],
          color: colors.neutral[800],
          border: `1px solid ${colors.neutral[200]}`,
        };
      case 'destructive':
        return {
          backgroundColor: colors.accent.red[100],
          color: colors.accent.red[800],
          border: `1px solid ${colors.accent.red[200]}`,
        };
      case 'outline':
        return {
          backgroundColor: 'transparent',
          color: colors.neutral[700],
          border: `1px solid ${colors.neutral[300]}`,
        };
      case 'success':
        return {
          backgroundColor: colors.secondary[100],
          color: colors.secondary[800],
          border: `1px solid ${colors.secondary[200]}`,
        };
      case 'warning':
        return {
          backgroundColor: colors.accent.orange[100],
          color: colors.accent.orange[800],
          border: `1px solid ${colors.accent.orange[200]}`,
        };
      default:
        return {
          backgroundColor: colors.primary[100],
          color: colors.primary[800],
          border: `1px solid ${colors.primary[200]}`,
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return {
          padding: `${spacing[1]} ${spacing[2]}`,
          fontSize: typography.fontSize.xs,
        };
      case 'lg':
        return {
          padding: `${spacing[2]} ${spacing[4]}`,
          fontSize: typography.fontSize.sm,
        };
      default:
        return {
          padding: `${spacing[1]} ${spacing[3]}`,
          fontSize: typography.fontSize.xs,
        };
    }
  };

  return (
    <span
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        borderRadius: borderRadius.full,
        fontWeight: typography.fontWeight.medium,
        whiteSpace: 'nowrap',
        ...getVariantStyles(),
        ...getSizeStyles(),
      }}
    >
      {children}
    </span>
  );
};