'use client';

import React, { useEffect, useRef, useState } from 'react';
import { animations } from '@/lib/design-system';

interface AnimatedSectionProps {
  children: React.ReactNode;
  animation?: 'fadeIn' | 'slideUp' | 'scaleIn' | 'slideInLeft' | 'slideInRight';
  delay?: number;
  duration?: number;
  threshold?: number;
  className?: string;
  style?: React.CSSProperties;
}

export const AnimatedSection: React.FC<AnimatedSectionProps> = ({
  children,
  animation = 'fadeIn',
  delay = 0,
  duration = 600,
  threshold = 0.1,
  className = '',
  style = {},
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry && entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      {
        threshold,
        rootMargin: '50px',
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [threshold]);

  const getAnimationStyles = (): React.CSSProperties => {
    const baseStyles: React.CSSProperties = {
      transition: `all ${duration}ms ${animations.easing.smooth}`,
      transitionDelay: `${delay}ms`,
    };

    if (!isVisible) {
      switch (animation) {
        case 'fadeIn':
          return {
            ...baseStyles,
            opacity: 0,
            transform: 'translateY(20px)',
          };
        case 'slideUp':
          return {
            ...baseStyles,
            opacity: 0,
            transform: 'translateY(40px)',
          };
        case 'scaleIn':
          return {
            ...baseStyles,
            opacity: 0,
            transform: 'scale(0.95)',
          };
        case 'slideInLeft':
          return {
            ...baseStyles,
            opacity: 0,
            transform: 'translateX(-40px)',
          };
        case 'slideInRight':
          return {
            ...baseStyles,
            opacity: 0,
            transform: 'translateX(40px)',
          };
        default:
          return {
            ...baseStyles,
            opacity: 0,
          };
      }
    }

    return {
      ...baseStyles,
      opacity: 1,
      transform: 'translateY(0) translateX(0) scale(1)',
    };
  };

  return (
    <div
      ref={ref}
      className={className}
      style={{
        ...getAnimationStyles(),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// Stagger animation for multiple elements
interface StaggeredAnimationProps {
  children: React.ReactNode[];
  animation?: 'fadeIn' | 'slideUp' | 'scaleIn';
  staggerDelay?: number;
  initialDelay?: number;
  className?: string;
}

export const StaggeredAnimation: React.FC<StaggeredAnimationProps> = ({
  children,
  animation = 'fadeIn',
  staggerDelay = 100,
  initialDelay = 0,
  className = '',
}) => {
  return (
    <div className={className}>
      {React.Children.map(children, (child, index) => (
        <AnimatedSection
          key={index}
          animation={animation}
          delay={initialDelay + index * staggerDelay}
        >
          {child}
        </AnimatedSection>
      ))}
    </div>
  );
};

// Hover animation wrapper
interface HoverAnimationProps {
  children: React.ReactNode;
  scale?: number;
  translateY?: number;
  duration?: number;
  className?: string;
  style?: React.CSSProperties;
}

export const HoverAnimation: React.FC<HoverAnimationProps> = ({
  children,
  scale = 1.02,
  translateY = -2,
  duration = 200,
  className = '',
  style = {},
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={className}
      style={{
        transition: `transform ${duration}ms ${animations.easing.smooth}`,
        transform: isHovered 
          ? `scale(${scale}) translateY(${translateY}px)` 
          : 'scale(1) translateY(0)',
        ...style,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}
    </div>
  );
};

// Floating animation for decorative elements
interface FloatingAnimationProps {
  children: React.ReactNode;
  duration?: number;
  distance?: number;
  delay?: number;
  className?: string;
  style?: React.CSSProperties;
}

export const FloatingAnimation: React.FC<FloatingAnimationProps> = ({
  children,
  duration = 3000,
  distance = 10,
  delay = 0,
  className = '',
  style = {},
}) => {
  return (
    <div
      className={className}
      style={{
        animation: `float ${duration}ms ${animations.easing.smooth} ${delay}ms infinite alternate`,
        ...style,
      }}
    >
      {children}
      <style jsx>{`
        @keyframes float {
          from {
            transform: translateY(0px);
          }
          to {
            transform: translateY(-${distance}px);
          }
        }
      `}</style>
    </div>
  );
};

// Pulse animation for attention-grabbing elements
interface PulseAnimationProps {
  children: React.ReactNode;
  scale?: number;
  duration?: number;
  className?: string;
  style?: React.CSSProperties;
}

export const PulseAnimation: React.FC<PulseAnimationProps> = ({
  children,
  scale = 1.05,
  duration = 2000,
  className = '',
  style = {},
}) => {
  return (
    <div
      className={className}
      style={{
        animation: `pulse ${duration}ms ${animations.easing.smooth} infinite alternate`,
        ...style,
      }}
    >
      {children}
      <style jsx>{`
        @keyframes pulse {
          from {
            transform: scale(1);
          }
          to {
            transform: scale(${scale});
          }
        }
      `}</style>
    </div>
  );
};