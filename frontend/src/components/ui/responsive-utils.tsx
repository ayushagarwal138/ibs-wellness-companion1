import React from 'react';
import { cn } from '@/lib/utils';

interface ResponsiveContainerProps {
  children: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  className,
  size = 'lg',
  padding = 'md'
}) => {
  const sizeClasses = {
    sm: 'max-w-2xl',
    md: 'max-w-4xl',
    lg: 'max-w-6xl',
    xl: 'max-w-7xl',
    full: 'max-w-full'
  };

  const paddingClasses = {
    none: '',
    sm: 'px-4 sm:px-6',
    md: 'px-4 sm:px-6 lg:px-8',
    lg: 'px-6 sm:px-8 lg:px-12'
  };

  return (
    <div className={cn(
      'w-full mx-auto',
      sizeClasses[size],
      paddingClasses[padding],
      className
    )}>
      {children}
    </div>
  );
};

interface ResponsiveGridProps {
  children: React.ReactNode;
  className?: string;
  cols?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: 'sm' | 'md' | 'lg' | 'xl';
  minItemWidth?: string;
}

export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  className,
  cols = { default: 1, sm: 2, lg: 3 },
  gap = 'md',
  minItemWidth = '280px'
}) => {
  const gapClasses = {
    sm: 'gap-3 sm:gap-4',
    md: 'gap-4 sm:gap-6',
    lg: 'gap-6 sm:gap-8',
    xl: 'gap-8 sm:gap-10'
  };

  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
    5: 'grid-cols-5',
    6: 'grid-cols-6'
  };

  const getGridClasses = () => {
    const classes = ['grid'];
    
    if (cols.default) classes.push(gridCols[cols.default as keyof typeof gridCols]);
    if (cols.sm) classes.push(`sm:${gridCols[cols.sm as keyof typeof gridCols]}`);
    if (cols.md) classes.push(`md:${gridCols[cols.md as keyof typeof gridCols]}`);
    if (cols.lg) classes.push(`lg:${gridCols[cols.lg as keyof typeof gridCols]}`);
    if (cols.xl) classes.push(`xl:${gridCols[cols.xl as keyof typeof gridCols]}`);
    
    return classes.join(' ');
  };

  return (
    <div 
      className={cn(
        getGridClasses(),
        gapClasses[gap],
        className
      )}
      style={{
        gridTemplateColumns: minItemWidth ? `repeat(auto-fit, minmax(${minItemWidth}, 1fr))` : undefined
      }}
    >
      {children}
    </div>
  );
};

interface ResponsiveStackProps {
  children: React.ReactNode;
  className?: string;
  direction?: 'vertical' | 'horizontal' | 'responsive';
  spacing?: 'sm' | 'md' | 'lg' | 'xl';
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
}

export const ResponsiveStack: React.FC<ResponsiveStackProps> = ({
  children,
  className,
  direction = 'responsive',
  spacing = 'md',
  align = 'start',
  justify = 'start'
}) => {
  const directionClasses = {
    vertical: 'flex flex-col',
    horizontal: 'flex flex-row',
    responsive: 'flex flex-col sm:flex-row'
  };

  const spacingClasses = {
    sm: direction === 'responsive' ? 'space-y-2 sm:space-y-0 sm:space-x-2' : 
        direction === 'vertical' ? 'space-y-2' : 'space-x-2',
    md: direction === 'responsive' ? 'space-y-4 sm:space-y-0 sm:space-x-4' : 
        direction === 'vertical' ? 'space-y-4' : 'space-x-4',
    lg: direction === 'responsive' ? 'space-y-6 sm:space-y-0 sm:space-x-6' : 
        direction === 'vertical' ? 'space-y-6' : 'space-x-6',
    xl: direction === 'responsive' ? 'space-y-8 sm:space-y-0 sm:space-x-8' : 
        direction === 'vertical' ? 'space-y-8' : 'space-x-8'
  };

  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch'
  };

  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
    evenly: 'justify-evenly'
  };

  return (
    <div className={cn(
      directionClasses[direction],
      spacingClasses[spacing],
      alignClasses[align],
      justifyClasses[justify],
      className
    )}>
      {children}
    </div>
  );
};

interface ResponsiveTextProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'hero' | 'heading' | 'subheading' | 'body' | 'caption';
  align?: 'left' | 'center' | 'right' | 'responsive';
  color?: 'default' | 'muted' | 'health' | 'wellness' | 'premium' | 'analytics';
}

export const ResponsiveText: React.FC<ResponsiveTextProps> = ({
  children,
  className,
  variant = 'body',
  align = 'left',
  color = 'default'
}) => {
  const variantClasses = {
    hero: 'heading-hero',
    heading: 'heading-section',
    subheading: 'heading-card',
    body: 'text-body',
    caption: 'text-caption'
  };

  const alignClasses = {
    left: 'text-left',
    center: 'text-center',
    right: 'text-right',
    responsive: 'text-center sm:text-left'
  };

  const colorClasses = {
    default: '',
    muted: 'text-muted-foreground',
    health: 'text-health',
    wellness: 'text-wellness',
    premium: 'text-premium',
    analytics: 'text-analytics'
  };

  return (
    <div className={cn(
      variantClasses[variant],
      alignClasses[align],
      colorClasses[color],
      className
    )}>
      {children}
    </div>
  );
};

// Responsive visibility utilities
interface ResponsiveShowProps {
  children: React.ReactNode;
  on?: ('sm' | 'md' | 'lg' | 'xl')[];
  className?: string;
}

export const ResponsiveShow: React.FC<ResponsiveShowProps> = ({
  children,
  on = ['sm'],
  className
}) => {
  const visibilityClasses = on.map(breakpoint => `${breakpoint}:block`).join(' ');
  
  return (
    <div className={cn('hidden', visibilityClasses, className)}>
      {children}
    </div>
  );
};

export const ResponsiveHide: React.FC<ResponsiveShowProps> = ({
  children,
  on = ['sm'],
  className
}) => {
  const visibilityClasses = on.map(breakpoint => `${breakpoint}:hidden`).join(' ');
  
  return (
    <div className={cn('block', visibilityClasses, className)}>
      {children}
    </div>
  );
};

// Responsive spacing component
interface ResponsiveSpacerProps {
  size?: {
    default?: 'sm' | 'md' | 'lg' | 'xl';
    sm?: 'sm' | 'md' | 'lg' | 'xl';
    md?: 'sm' | 'md' | 'lg' | 'xl';
    lg?: 'sm' | 'md' | 'lg' | 'xl';
  };
  className?: string;
}

export const ResponsiveSpacer: React.FC<ResponsiveSpacerProps> = ({
  size = { default: 'md' },
  className
}) => {
  const sizeClasses = {
    sm: 'h-4',
    md: 'h-8',
    lg: 'h-12',
    xl: 'h-16'
  };

  const getSpacingClasses = () => {
    const classes = [];
    
    if (size.default) classes.push(sizeClasses[size.default]);
    if (size.sm) classes.push(`sm:${sizeClasses[size.sm]}`);
    if (size.md) classes.push(`md:${sizeClasses[size.md]}`);
    if (size.lg) classes.push(`lg:${sizeClasses[size.lg]}`);
    
    return classes.join(' ');
  };

  return <div className={cn(getSpacingClasses(), className)} />;
};