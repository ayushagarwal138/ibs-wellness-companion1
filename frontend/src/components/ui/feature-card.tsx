'use client';

import React from 'react';
import { 
  TrendingUp, 
  MessageCircle, 
  Bell, 
  Brain, 
  Heart, 
  Shield,
  Star,
  Users,
  CheckCircle,
  ArrowRight
} from 'lucide-react';
import { colors, typography, spacing, borderRadius, shadows, gradients, animations } from '@/lib/design-system';

// Icon mapping for string-based icon selection
const iconMap = {
  TrendingUp,
  MessageCircle,
  Bell,
  Brain,
  Heart,
  Shield,
  Star,
  Users,
  CheckCircle,
  ArrowRight,
};

type IconName = keyof typeof iconMap;

interface FeatureCardProps {
  icon: IconName;
  title: string;
  description: string;
  variant?: 'default' | 'gradient' | 'minimal';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon: iconName,
  title,
  description,
  variant = 'default',
  size = 'md',
  onClick,
}) => {
  const Icon = iconMap[iconName];
  
  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return {
          padding: spacing[4],
          iconSize: 20,
          titleSize: typography.fontSize.lg,
          descriptionSize: typography.fontSize.sm,
        };
      case 'lg':
        return {
          padding: spacing[8],
          iconSize: 32,
          titleSize: typography.fontSize['2xl'],
          descriptionSize: typography.fontSize.lg,
        };
      default:
        return {
          padding: spacing[6],
          iconSize: 24,
          titleSize: typography.fontSize.xl,
          descriptionSize: typography.fontSize.base,
        };
    }
  };

  const getVariantStyles = () => {
    const sizeStyles = getSizeStyles();
    
    const baseStyle = {
      padding: sizeStyles.padding,
      borderRadius: borderRadius.xl,
      cursor: onClick ? 'pointer' : 'default',
      transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
      transform: 'translateY(0)',
      position: 'relative' as const,
      overflow: 'hidden' as const,
    };

    switch (variant) {
      case 'gradient':
        return {
          ...baseStyle,
          background: gradients.primary,
          color: 'white',
          border: 'none',
          boxShadow: shadows.lg,
        };
      case 'minimal':
        return {
          ...baseStyle,
          backgroundColor: 'transparent',
          border: `2px solid ${colors.neutral[200]}`,
          color: colors.neutral[800],
        };
      default:
        return {
          ...baseStyle,
          backgroundColor: 'white',
          border: `1px solid ${colors.neutral[200]}`,
          boxShadow: shadows.md,
          color: colors.neutral[800],
        };
    }
  };

  const getIconStyles = () => {
    const sizeStyles = getSizeStyles();
    
    const baseIconStyle = {
      width: `${sizeStyles.iconSize + 16}px`,
      height: `${sizeStyles.iconSize + 16}px`,
      borderRadius: borderRadius.lg,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginBottom: spacing[4],
      transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
    };

    switch (variant) {
      case 'gradient':
        return {
          ...baseIconStyle,
          backgroundColor: 'rgba(255, 255, 255, 0.2)',
          color: 'white',
        };
      case 'minimal':
        return {
          ...baseIconStyle,
          backgroundColor: colors.primary[50],
          color: colors.primary[600],
        };
      default:
        return {
          ...baseIconStyle,
          backgroundColor: colors.primary[50],
          color: colors.primary[600],
        };
    }
  };

  const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!onClick) return;
    
    e.currentTarget.style.transform = 'translateY(-8px)';
    
    if (variant === 'default') {
      e.currentTarget.style.boxShadow = shadows.xl;
    } else if (variant === 'gradient') {
      e.currentTarget.style.boxShadow = shadows['2xl'];
    } else if (variant === 'minimal') {
      e.currentTarget.style.backgroundColor = colors.neutral[50];
      e.currentTarget.style.borderColor = colors.primary[300];
    }
  };

  const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!onClick) return;
    
    e.currentTarget.style.transform = 'translateY(0)';
    
    if (variant === 'default') {
      e.currentTarget.style.boxShadow = shadows.md;
    } else if (variant === 'gradient') {
      e.currentTarget.style.boxShadow = shadows.lg;
    } else if (variant === 'minimal') {
      e.currentTarget.style.backgroundColor = 'transparent';
      e.currentTarget.style.borderColor = colors.neutral[200];
    }
  };

  const sizeStyles = getSizeStyles();

  return (
    <div
      style={getVariantStyles()}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Background Pattern for gradient variant */}
      {variant === 'gradient' && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: `
              radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%)
            `,
            pointerEvents: 'none',
          }}
        />
      )}

      <div style={{ position: 'relative', zIndex: 1 }}>
        {/* Icon */}
        <div style={getIconStyles()}>
          <Icon size={sizeStyles.iconSize} />
        </div>

        {/* Title */}
        <h3
          style={{
            fontSize: sizeStyles.titleSize,
            fontWeight: typography.fontWeight.bold,
            marginBottom: spacing[3],
            lineHeight: typography.lineHeight.tight,
          }}
        >
          {title}
        </h3>

        {/* Description */}
        <p
          style={{
            fontSize: sizeStyles.descriptionSize,
            lineHeight: typography.lineHeight.relaxed,
            opacity: variant === 'gradient' ? 0.9 : 0.7,
            margin: 0,
          }}
        >
          {description}
        </p>

        {/* Hover indicator for clickable cards */}
        {onClick && (
          <div
            style={{
              marginTop: spacing[4],
              fontSize: typography.fontSize.sm,
              fontWeight: typography.fontWeight.medium,
              opacity: 0.6,
              transition: `opacity ${animations.duration.fast} ${animations.easing.smooth}`,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '1';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '0.6';
            }}
          >
            Learn more →
          </div>
        )}
      </div>
    </div>
  );
};

// Feature Grid Component for organizing multiple cards
interface FeatureGridProps {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: keyof typeof spacing;
}

export const FeatureGrid: React.FC<FeatureGridProps> = ({
  children,
  columns = 3,
  gap = 6,
}) => {
  const getGridColumns = () => {
    switch (columns) {
      case 1:
        return '1fr';
      case 2:
        return 'repeat(auto-fit, minmax(300px, 1fr))';
      case 4:
        return 'repeat(auto-fit, minmax(250px, 1fr))';
      default:
        return 'repeat(auto-fit, minmax(320px, 1fr))';
    }
  };

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: getGridColumns(),
        gap: spacing[gap],
        width: '100%',
      }}
    >
      {children}
    </div>
  );
};