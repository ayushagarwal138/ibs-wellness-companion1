'use client';

import { Header } from '@/components/ui/header';
import { Footer } from '@/components/layout/footer';
import { colors, spacing, typography, borderRadius, shadows, gradients } from '@/lib/design-system';
import { CheckCircle, ArrowRight, Users, Brain, TrendingUp } from 'lucide-react';

export default function HowItWorksPage() {
  const steps = [
    {
      icon: Users,
      title: 'Sign Up & Profile Setup',
      description: 'Create your account and complete a comprehensive health profile to personalize your experience.',
      details: ['Medical history questionnaire', 'Dietary preferences', 'Current symptoms assessment', 'Goal setting']
    },
    {
      icon: Brain,
      title: 'Track & Monitor',
      description: 'Log your daily symptoms, meals, and activities using our intuitive tracking tools.',
      details: ['Symptom severity tracking', 'Food diary with photos', 'Mood and stress levels', 'Sleep quality monitoring']
    },
    {
      icon: TrendingUp,
      title: 'AI Analysis & Insights',
      description: 'Our advanced AI analyzes your data to identify patterns and provide personalized recommendations.',
      details: ['Trigger identification', 'Predictive analytics', 'Personalized meal plans', 'Treatment optimization']
    }
  ];

  return (
    <div style={{ minHeight: '100vh', backgroundColor: colors.neutral[50] }}>
      <Header variant="solid" />
      
      {/* Hero Section */}
      <section
        id="how-it-works"
        style={{
          padding: `${spacing[20]} 0`,
          background: gradients.light,
          textAlign: 'center',
        }}
      >
        <div
          style={{
            maxWidth: '800px',
            margin: '0 auto',
            padding: `0 ${spacing[6]}`,
          }}
        >
          <h1
            style={{
              fontSize: typography.fontSize['5xl'],
              fontWeight: typography.fontWeight.bold,
              color: colors.neutral[900],
              marginBottom: spacing[6],
              lineHeight: typography.lineHeight.tight,
            }}
          >
            How IBS Wellness Works
          </h1>
          
          <p
            style={{
              fontSize: typography.fontSize.xl,
              color: colors.neutral[600],
              marginBottom: spacing[12],
              lineHeight: typography.lineHeight.relaxed,
            }}
          >
            Our three-step approach combines cutting-edge AI technology with personalized care to help you manage your IBS effectively.
          </p>
        </div>
      </section>

      {/* Steps Section */}
      <section
        style={{
          padding: `${spacing[20]} 0`,
          backgroundColor: 'white',
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: `0 ${spacing[6]}`,
          }}
        >
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
              gap: spacing[12],
            }}
          >
            {steps.map((step, index) => {
              const Icon = step.icon;
              return (
                <div
                  key={index}
                  style={{
                    textAlign: 'center',
                    position: 'relative',
                  }}
                >
                  {/* Step Number */}
                  <div
                    style={{
                      position: 'absolute',
                      top: '-10px',
                      left: '50%',
                      transform: 'translateX(-50%)',
                      width: '40px',
                      height: '40px',
                      borderRadius: borderRadius.full,
                      backgroundColor: colors.primary[600],
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: typography.fontSize.lg,
                      fontWeight: typography.fontWeight.bold,
                      boxShadow: shadows.lg,
                    }}
                  >
                    {index + 1}
                  </div>

                  {/* Icon */}
                  <div
                    style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: borderRadius.full,
                      backgroundColor: colors.primary[50],
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: `${spacing[8]} auto ${spacing[6]} auto`,
                      border: `2px solid ${colors.primary[200]}`,
                    }}
                  >
                    <Icon size={40} style={{ color: colors.primary[600] }} />
                  </div>

                  {/* Content */}
                  <h3
                    style={{
                      fontSize: typography.fontSize['2xl'],
                      fontWeight: typography.fontWeight.bold,
                      color: colors.neutral[900],
                      marginBottom: spacing[4],
                    }}
                  >
                    {step.title}
                  </h3>

                  <p
                    style={{
                      fontSize: typography.fontSize.lg,
                      color: colors.neutral[600],
                      marginBottom: spacing[6],
                      lineHeight: typography.lineHeight.relaxed,
                    }}
                  >
                    {step.description}
                  </p>

                  {/* Details */}
                  <ul
                    style={{
                      textAlign: 'left',
                      listStyle: 'none',
                      padding: 0,
                      margin: 0,
                    }}
                  >
                    {step.details.map((detail, detailIndex) => (
                      <li
                        key={detailIndex}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          marginBottom: spacing[2],
                          fontSize: typography.fontSize.base,
                          color: colors.neutral[700],
                        }}
                      >
                        <CheckCircle
                          size={16}
                          style={{
                            color: colors.primary[600],
                            marginRight: spacing[3],
                            flexShrink: 0,
                          }}
                        />
                        {detail}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section
        style={{
          padding: `${spacing[20]} 0`,
          background: gradients.primary,
          color: 'white',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            maxWidth: '600px',
            margin: '0 auto',
            padding: `0 ${spacing[6]}`,
          }}
        >
          <h2
            style={{
              fontSize: typography.fontSize['3xl'],
              fontWeight: typography.fontWeight.bold,
              marginBottom: spacing[6],
            }}
          >
            Ready to Start Your Journey?
          </h2>
          
          <p
            style={{
              fontSize: typography.fontSize.lg,
              marginBottom: spacing[8],
              opacity: 0.9,
            }}
          >
            Join thousands of users who have already taken control of their IBS with our proven approach.
          </p>

          <button
            style={{
              padding: `${spacing[4]} ${spacing[8]}`,
              fontSize: typography.fontSize.lg,
              fontWeight: typography.fontWeight.semibold,
              backgroundColor: 'white',
              color: colors.primary[700],
              border: 'none',
              borderRadius: borderRadius.xl,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              boxShadow: shadows.lg,
            }}
          >
            Get Started Today
            <ArrowRight size={20} style={{ marginLeft: spacing[2] }} />
          </button>
        </div>
      </section>

      <Footer />
    </div>
  );
}