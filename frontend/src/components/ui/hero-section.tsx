'use client';

import React from 'react';
import { colors, typography, spacing, borderRadius, shadows, gradients, animations } from '@/lib/design-system';

interface HeroSectionProps {
  title?: string;
  subtitle?: string;
  description?: string;
  primaryButtonText?: string;
  secondaryButtonText?: string;
  onPrimaryClick?: () => void;
  onSecondaryClick?: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  title = "Take Control of Your IBS Journey",
  subtitle = "Personalized wellness companion",
  description = "Track symptoms, discover triggers, and get AI-powered insights to manage your IBS effectively. Join thousands who've found relief through data-driven wellness.",
  primaryButtonText = "Start Your Journey",
  secondaryButtonText = "Learn More",
  onPrimaryClick,
  onSecondaryClick,
}) => {
  return (
    <section 
      style={{
        position: 'relative',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: gradients.hero,
        overflow: 'hidden',
        paddingTop: '80px', // Account for fixed header
      }}
    >
      {/* Background Pattern */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `
            radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.05) 0%, transparent 50%)
          `,
          pointerEvents: 'none',
        }}
      />
      
      {/* Floating Elements */}
      <div
        style={{
          position: 'absolute',
          top: '20%',
          right: '10%',
          width: '100px',
          height: '100px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: borderRadius.full,
          animation: 'float 6s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '20%',
          left: '5%',
          width: '60px',
          height: '60px',
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: borderRadius.full,
          animation: 'float 4s ease-in-out infinite reverse',
        }}
      />
      
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: `0 ${spacing[6]}`,
          position: 'relative',
          zIndex: 1,
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: spacing[12],
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          <div>
            {/* Subtitle */}
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: `${spacing[2]} ${spacing[4]}`,
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                borderRadius: borderRadius.full,
                marginBottom: spacing[6],
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
              }}
            >
              <span
                style={{
                  fontSize: typography.fontSize.sm,
                  fontWeight: typography.fontWeight.medium,
                  color: 'white',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}
              >
                {subtitle}
              </span>
            </div>

            {/* Main Title */}
            <h1
              style={{
                fontSize: typography.fontSize['5xl'],
                fontWeight: typography.fontWeight.bold,
                lineHeight: typography.lineHeight.tight,
                color: 'white',
                marginBottom: spacing[6],
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              }}
            >
              {title}
            </h1>

            {/* Description */}
            <p
              style={{
                fontSize: typography.fontSize.xl,
                lineHeight: typography.lineHeight.relaxed,
                color: 'rgba(255, 255, 255, 0.9)',
                marginBottom: spacing[10],
                maxWidth: '600px',
                margin: `0 auto ${spacing[10]} auto`,
              }}
            >
              {description}
            </p>

            {/* CTA Buttons */}
            <div
              style={{
                display: 'flex',
                gap: spacing[4],
                justifyContent: 'center',
                flexWrap: 'wrap',
              }}
            >
              <button
                onClick={onPrimaryClick}
                style={{
                  padding: `${spacing[4]} ${spacing[8]}`,
                  fontSize: typography.fontSize.lg,
                  fontWeight: typography.fontWeight.semibold,
                  color: colors.primary[700],
                  backgroundColor: 'white',
                  border: 'none',
                  borderRadius: borderRadius.xl,
                  cursor: 'pointer',
                  transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                  boxShadow: shadows.lg,
                  transform: 'translateY(0)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = shadows.xl;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = shadows.lg;
                }}
              >
                {primaryButtonText}
              </button>

              <button
                onClick={onSecondaryClick}
                style={{
                  padding: `${spacing[4]} ${spacing[8]}`,
                  fontSize: typography.fontSize.lg,
                  fontWeight: typography.fontWeight.semibold,
                  color: 'white',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: borderRadius.xl,
                  cursor: 'pointer',
                  transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                  backdropFilter: 'blur(10px)',
                  transform: 'translateY(0)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.5)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                {secondaryButtonText}
              </button>
            </div>

            {/* Trust Indicators */}
            <div
              style={{
                marginTop: spacing[12],
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: spacing[8],
                flexWrap: 'wrap',
              }}
            >
              <div style={{ textAlign: 'center' }}>
                <div
                  style={{
                    fontSize: typography.fontSize['2xl'],
                    fontWeight: typography.fontWeight.bold,
                    color: 'white',
                  }}
                >
                  10,000+
                </div>
                <div
                  style={{
                    fontSize: typography.fontSize.sm,
                    color: 'rgba(255, 255, 255, 0.8)',
                  }}
                >
                  Active Users
                </div>
              </div>
              
              <div
                style={{
                  width: '1px',
                  height: '40px',
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                }}
              />
              
              <div style={{ textAlign: 'center' }}>
                <div
                  style={{
                    fontSize: typography.fontSize['2xl'],
                    fontWeight: typography.fontWeight.bold,
                    color: 'white',
                  }}
                >
                  4.8★
                </div>
                <div
                  style={{
                    fontSize: typography.fontSize.sm,
                    color: 'rgba(255, 255, 255, 0.8)',
                  }}
                >
                  User Rating
                </div>
              </div>
              
              <div
                style={{
                  width: '1px',
                  height: '40px',
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                }}
              />
              
              <div style={{ textAlign: 'center' }}>
                <div
                  style={{
                    fontSize: typography.fontSize['2xl'],
                    fontWeight: typography.fontWeight.bold,
                    color: 'white',
                  }}
                >
                  85%
                </div>
                <div
                  style={{
                    fontSize: typography.fontSize.sm,
                    color: 'rgba(255, 255, 255, 0.8)',
                  }}
                >
                  Symptom Improvement
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add keyframes to the document */}
      <style jsx>{`
        ${animations.keyframes.float}
      `}</style>
    </section>
  );
};