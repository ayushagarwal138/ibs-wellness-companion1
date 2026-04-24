import React from 'react';
import { cn } from '@/lib/utils';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'centered' | 'sidebar' | 'dashboard';
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  background?: 'default' | 'gray' | 'gradient' | 'glass';
}

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  children,
  className,
  variant = 'default',
  maxWidth = 'lg',
  padding = 'md',
  background = 'default'
}) => {
  const maxWidthClasses = {
    sm: 'max-w-2xl',
    md: 'max-w-4xl',
    lg: 'max-w-6xl',
    xl: 'max-w-7xl',
    '2xl': 'max-w-8xl',
    full: 'max-w-full'
  };

  const paddingClasses = {
    none: '',
    sm: 'px-4 py-4 sm:px-6 sm:py-6',
    md: 'px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10',
    lg: 'px-6 py-8 sm:px-8 sm:py-10 lg:px-12 lg:py-12',
    xl: 'px-8 py-10 sm:px-10 sm:py-12 lg:px-16 lg:py-16'
  };

  const backgroundClasses = {
    default: 'bg-background',
    gray: 'bg-gray-50',
    gradient: 'bg-gradient-to-br from-gray-50 to-white',
    glass: 'bg-white/80 backdrop-blur-sm'
  };

  const variantClasses = {
    default: 'w-full mx-auto',
    centered: 'w-full mx-auto flex flex-col items-center justify-center min-h-[50vh]',
    sidebar: 'w-full mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6 lg:gap-8',
    dashboard: 'w-full mx-auto space-y-6 lg:space-y-8'
  };

  return (
    <div className={cn(
      variantClasses[variant],
      maxWidthClasses[maxWidth],
      paddingClasses[padding],
      backgroundClasses[background],
      className
    )}>
      {children}
    </div>
  );
};

interface ResponsiveSectionProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  spacing?: 'sm' | 'md' | 'lg' | 'xl';
  background?: 'none' | 'white' | 'gray' | 'gradient';
  border?: boolean;
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
}

export const ResponsiveSection: React.FC<ResponsiveSectionProps> = ({
  children,
  className,
  title,
  subtitle,
  spacing = 'md',
  background = 'none',
  border = false,
  shadow = 'none'
}) => {
  const spacingClasses = {
    sm: 'py-8 sm:py-10',
    md: 'py-10 sm:py-12 lg:py-16',
    lg: 'py-12 sm:py-16 lg:py-20',
    xl: 'py-16 sm:py-20 lg:py-24'
  };

  const backgroundClasses = {
    none: '',
    white: 'bg-white',
    gray: 'bg-gray-50',
    gradient: 'bg-gradient-to-br from-white to-gray-50'
  };

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl'
  };

  return (
    <section className={cn(
      spacingClasses[spacing],
      backgroundClasses[background],
      shadowClasses[shadow],
      border && 'border border-gray-200',
      className
    )}>
      {(title || subtitle) && (
        <div className="container-responsive mb-8 sm:mb-12">
          {title && (
            <h2 className="heading-section text-center sm:text-left">
              {title}
            </h2>
          )}
          {subtitle && (
            <p className="text-subtitle text-center sm:text-left mt-2">
              {subtitle}
            </p>
          )}
        </div>
      )}
      {children}
    </section>
  );
};

interface ResponsiveCardGridProps {
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
  minCardWidth?: string;
}

export const ResponsiveCardGrid: React.FC<ResponsiveCardGridProps> = ({
  children,
  className,
  cols = { default: 1, sm: 2, lg: 3 },
  gap = 'md',
  minCardWidth = '280px'
}) => {
  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8',
    xl: 'gap-10'
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
        gridTemplateColumns: minCardWidth ? `repeat(auto-fit, minmax(${minCardWidth}, 1fr))` : undefined
      }}
    >
      {children}
    </div>
  );
};

interface ResponsiveHeroProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  background?: 'default' | 'gradient' | 'image';
  backgroundImage?: string;
  height?: 'sm' | 'md' | 'lg' | 'xl' | 'screen';
  overlay?: boolean;
}

export const ResponsiveHero: React.FC<ResponsiveHeroProps> = ({
  children,
  className,
  title,
  subtitle,
  background = 'default',
  backgroundImage,
  height = 'md',
  overlay = false
}) => {
  const heightClasses = {
    sm: 'min-h-[40vh]',
    md: 'min-h-[60vh]',
    lg: 'min-h-[80vh]',
    xl: 'min-h-[90vh]',
    screen: 'min-h-screen'
  };

  const backgroundClasses = {
    default: 'bg-gradient-to-br from-primary/10 to-secondary/10',
    gradient: 'bg-gradient-to-br from-primary to-secondary',
    image: backgroundImage ? 'bg-cover bg-center bg-no-repeat' : 'bg-gray-100'
  };

  return (
    <section 
      className={cn(
        'relative flex items-center justify-center',
        heightClasses[height],
        backgroundClasses[background],
        className
      )}
      style={backgroundImage ? { backgroundImage: `url(${backgroundImage})` } : undefined}
    >
      {overlay && (
        <div className="absolute inset-0 bg-black/30" />
      )}
      
      <div className="relative z-10 container-responsive text-center">
        {title && (
          <h1 className="heading-hero text-white mb-6">
            {title}
          </h1>
        )}
        {subtitle && (
          <p className="text-subtitle text-white/90 mb-8 max-w-3xl mx-auto">
            {subtitle}
          </p>
        )}
        {children}
      </div>
    </section>
  );
};

interface ResponsiveNavProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'sticky' | 'floating';
  background?: 'white' | 'transparent' | 'glass';
  border?: boolean;
  shadow?: boolean;
}

export const ResponsiveNav: React.FC<ResponsiveNavProps> = ({
  children,
  className,
  variant = 'default',
  background = 'white',
  border = true,
  shadow = true
}) => {
  const variantClasses = {
    default: 'relative',
    sticky: 'sticky top-0 z-50',
    floating: 'fixed top-4 left-4 right-4 z-50 rounded-xl'
  };

  const backgroundClasses = {
    white: 'bg-white',
    transparent: 'bg-transparent',
    glass: 'bg-white/80 backdrop-blur-md'
  };

  return (
    <nav className={cn(
      variantClasses[variant],
      backgroundClasses[background],
      border && 'border-b border-gray-200',
      shadow && 'shadow-sm',
      className
    )}>
      <div className="container-responsive">
        {children}
      </div>
    </nav>
  );
};