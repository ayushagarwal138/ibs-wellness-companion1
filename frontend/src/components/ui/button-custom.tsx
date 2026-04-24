'use client';

import React from 'react';
import Link from 'next/link';
import { colors, spacing, typography, borderRadius, components } from '@/lib/design-system';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
  onClick?: () => void;
  href?: string;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  className?: string;
}

export function ButtonCustom({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  href,
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  className = '',
}: ButtonProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: colors.primary[600],
          color: 'white',
          border: `1px solid ${colors.primary[600]}`,
          '&:hover': {
            backgroundColor: colors.primary[700],
            borderColor: colors.primary[700],
          },
          '&:focus': {
            boxShadow: `0 0 0 3px ${colors.primary[200]}`,
          },
        };
      case 'secondary':
        return {
          backgroundColor: colors.secondary[100],
          color: colors.secondary[900],
          border: `1px solid ${colors.secondary[300]}`,
          '&:hover': {
            backgroundColor: colors.secondary[200],
            borderColor: colors.secondary[400],
          },
          '&:focus': {
            boxShadow: `0 0 0 3px ${colors.secondary[200]}`,
          },
        };
      case 'outline':
        return {
          backgroundColor: 'transparent',
          color: colors.primary[600],
          border: `1px solid ${colors.primary[300]}`,
          '&:hover': {
            backgroundColor: colors.primary[50],
            borderColor: colors.primary[400],
          },
          '&:focus': {
            boxShadow: `0 0 0 3px ${colors.primary[200]}`,
          },
        };
      case 'ghost':
        return {
          backgroundColor: 'transparent',
          color: colors.neutral[700],
          border: '1px solid transparent',
          '&:hover': {
            backgroundColor: colors.neutral[100],
          },
          '&:focus': {
            boxShadow: `0 0 0 3px ${colors.neutral[200]}`,
          },
        };
      case 'danger':
        return {
          backgroundColor: colors.status.error,
          color: 'white',
          border: `1px solid ${colors.status.error}`,
          '&:hover': {
            backgroundColor: colors.accent.red[700],
            borderColor: colors.accent.red[700],
          },
          '&:focus': {
            boxShadow: `0 0 0 3px ${colors.accent.red[200]}`,
          },
        };
      default:
        return {};
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return {
          padding: `${spacing[2]} ${spacing[3]}`,
          fontSize: typography.fontSize.sm,
          lineHeight: typography.lineHeight.tight,
        };
      case 'md':
        return {
          padding: `${spacing[3]} ${spacing[4]}`,
          fontSize: typography.fontSize.base,
          lineHeight: typography.lineHeight.normal,
        };
      case 'lg':
        return {
          padding: `${spacing[4]} ${spacing[6]}`,
          fontSize: typography.fontSize.lg,
          lineHeight: typography.lineHeight.normal,
        };
      case 'xl':
        return {
          padding: `${spacing[5]} ${spacing[8]}`,
          fontSize: typography.fontSize.xl,
          lineHeight: typography.lineHeight.normal,
        };
      default:
        return {};
    }
  };

  const baseStyles = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing[2],
    fontWeight: typography.fontWeight.medium,
    borderRadius: borderRadius.lg,
    transition: 'all 0.2s ease-in-out',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    opacity: disabled || loading ? 0.6 : 1,
    textDecoration: 'none',
    width: fullWidth ? '100%' : 'auto',
    ...getVariantStyles(),
    ...getSizeStyles(),
  };

  const buttonContent = (
    <>
      {loading && (
        <div
          className="animate-spin rounded-full border-2 border-current border-t-transparent"
          style={{
            width: size === 'sm' ? '14px' : size === 'lg' || size === 'xl' ? '18px' : '16px',
            height: size === 'sm' ? '14px' : size === 'lg' || size === 'xl' ? '18px' : '16px',
          }}
        />
      )}
      {!loading && icon && iconPosition === 'left' && icon}
      {children}
      {!loading && icon && iconPosition === 'right' && icon}
    </>
  );

  if (href && !disabled && !loading) {
    return (
      <Link
        href={href}
        style={baseStyles}
        className={className}
      >
        {buttonContent}
      </Link>
    );
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      style={baseStyles}
      className={className}
    >
      {buttonContent}
    </button>
  );
}