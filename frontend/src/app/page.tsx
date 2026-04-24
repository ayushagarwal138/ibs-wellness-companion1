'use client';

import { Header } from '@/components/ui/header';
import { Footer } from '@/components/layout/footer';
import { HeroSection } from '@/components/ui/hero-section';
import { FeatureCard, FeatureGrid } from '@/components/ui/feature-card';
import { Shield, Brain, TrendingUp, MessageCircle, Bell, Heart, ArrowRight, CheckCircle, Star, Users } from 'lucide-react';
import { colors, spacing, typography, borderRadius, shadows, gradients, animations } from '@/lib/design-system';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  const handleStartJourney = () => {
    router.push('/register');
  };

  const handleLearnMore = () => {
    // Scroll to features section
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
      featuresSection.scrollIntoView({ behavior: 'smooth' });
    }
  };
  const features = [
    {
      icon: 'TrendingUp' as const,
      title: 'AI-Powered Predictions',
      description: 'Advanced machine learning algorithms analyze your patterns to predict potential flare-ups before they happen, giving you time to take preventive action.',
    },
    {
      icon: 'MessageCircle' as const,
      title: 'Smart Health Assistant',
      description: 'Get instant, personalized answers about symptoms, diet recommendations, and treatment options from our intelligent chatbot.',
    },
    {
      icon: 'Bell' as const,
      title: 'Intelligent Reminders',
      description: 'Never miss medications or important health activities with smart, context-aware notifications tailored to your routine.',
    },
    {
      icon: 'Brain' as const,
      title: 'Advanced Analytics',
      description: 'Visualize your health journey with comprehensive charts, trends, and insights that help you understand your condition better.',
    },
    {
      icon: 'Heart' as const,
      title: 'Personalized Nutrition',
      description: 'Receive tailored meal suggestions and dietary guidance based on your specific triggers, preferences, and nutritional needs.',
    },
    {
      icon: 'Shield' as const,
      title: 'Privacy & Security',
      description: 'Your sensitive health data is protected with enterprise-grade security, encryption, and strict privacy controls.',
    },
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'IBS Patient',
      content: 'This app has been life-changing. The predictions are incredibly accurate, and I\'ve reduced my flare-ups by 70%.',
      rating: 5,
    },
    {
      name: 'Dr. Michael Chen',
      role: 'Gastroenterologist',
      content: 'I recommend this to all my IBS patients. The data insights help me provide better, more personalized treatment plans.',
      rating: 5,
    },
    {
      name: 'Emma Rodriguez',
      role: 'Wellness Coach',
      content: 'The AI assistant is remarkably helpful. It provides evidence-based recommendations that complement professional care.',
      rating: 5,
    },
  ];

  return (
    <div style={{ minHeight: '100vh', backgroundColor: colors.neutral[50] }}>
      <Header variant="transparent" />
      
      {/* Hero Section */}
      <HeroSection
        onPrimaryClick={handleStartJourney}
        onSecondaryClick={handleLearnMore}
      />

      {/* Features Section */}
      <section
        id="features"
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
          {/* Section Header */}
          <div
            style={{
              textAlign: 'center',
              marginBottom: spacing[16],
            }}
          >
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: `${spacing[2]} ${spacing[4]}`,
                backgroundColor: colors.primary[50],
                borderRadius: borderRadius.full,
                marginBottom: spacing[4],
                border: `1px solid ${colors.primary[200]}`,
              }}
            >
              <Star size={16} style={{ marginRight: spacing[2], color: colors.primary[600] }} />
              <span
                style={{
                  fontSize: typography.fontSize.sm,
                  fontWeight: typography.fontWeight.semibold,
                  color: colors.primary[700],
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}
              >
                Powerful Features
              </span>
            </div>
            
            <h2
              style={{
                fontSize: typography.fontSize['4xl'],
                fontWeight: typography.fontWeight.bold,
                color: colors.neutral[900],
                marginBottom: spacing[4],
                lineHeight: typography.lineHeight.tight,
              }}
            >
              Everything You Need to Manage IBS
            </h2>
            
            <p
              style={{
                fontSize: typography.fontSize.xl,
                color: colors.neutral[600],
                maxWidth: '600px',
                margin: '0 auto',
                lineHeight: typography.lineHeight.relaxed,
              }}
            >
              Comprehensive tools powered by AI and machine learning to help you understand, predict, and manage your IBS symptoms effectively.
            </p>
          </div>

          {/* Feature Cards */}
          <FeatureGrid columns={3} gap={8}>
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                variant={index % 3 === 0 ? 'gradient' : index % 3 === 1 ? 'default' : 'minimal'}
                size="md"
              />
            ))}
          </FeatureGrid>
        </div>
      </section>

      {/* Testimonials Section */}
      <section
        id="about"
        style={{
          padding: `${spacing[20]} 0`,
          background: gradients.light,
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
              textAlign: 'center',
              marginBottom: spacing[16],
            }}
          >
            <h2
              style={{
                fontSize: typography.fontSize['4xl'],
                fontWeight: typography.fontWeight.bold,
                color: colors.neutral[900],
                marginBottom: spacing[4],
              }}
            >
              Trusted by Thousands
            </h2>
            <p
              style={{
                fontSize: typography.fontSize.xl,
                color: colors.neutral[600],
                maxWidth: '600px',
                margin: '0 auto',
              }}
            >
              See what patients and healthcare professionals are saying about our platform.
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
              gap: spacing[8],
            }}
          >
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                style={{
                  backgroundColor: 'white',
                  padding: spacing[8],
                  borderRadius: borderRadius.xl,
                  boxShadow: shadows.md,
                  border: `1px solid ${colors.neutral[200]}`,
                  transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                  transform: 'translateY(0)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = shadows.lg;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = shadows.md;
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    marginBottom: spacing[4],
                  }}
                >
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star
                      key={i}
                      size={20}
                      style={{
                        color: colors.accent.orange[500],
                        fill: colors.accent.orange[500],
                      }}
                    />
                  ))}
                </div>
                
                <p
                  style={{
                    fontSize: typography.fontSize.lg,
                    lineHeight: typography.lineHeight.relaxed,
                    color: colors.neutral[700],
                    marginBottom: spacing[6],
                    fontStyle: 'italic',
                  }}
                >
                  "{testimonial.content}"
                </p>
                
                <div>
                  <div
                    style={{
                      fontSize: typography.fontSize.base,
                      fontWeight: typography.fontWeight.semibold,
                      color: colors.neutral[900],
                    }}
                  >
                    {testimonial.name}
                  </div>
                  <div
                    style={{
                      fontSize: typography.fontSize.sm,
                      color: colors.neutral[600],
                    }}
                  >
                    {testimonial.role}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section
        id="contact"
        style={{
          padding: `${spacing[20]} 0`,
          background: gradients.primary,
          color: 'white',
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
          <h2
            style={{
              fontSize: typography.fontSize['4xl'],
              fontWeight: typography.fontWeight.bold,
              marginBottom: spacing[6],
              lineHeight: typography.lineHeight.tight,
            }}
          >
            Ready to Take Control of Your IBS?
          </h2>
          
          <p
            style={{
              fontSize: typography.fontSize.xl,
              marginBottom: spacing[10],
              opacity: 0.9,
              lineHeight: typography.lineHeight.relaxed,
            }}
          >
            Join thousands of users who have already improved their quality of life with our AI-powered IBS management platform.
          </p>

          <div
            style={{
              display: 'flex',
              gap: spacing[4],
              justifyContent: 'center',
              flexWrap: 'wrap',
            }}
          >
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
                transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                boxShadow: shadows.lg,
                display: 'flex',
                alignItems: 'center',
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
              Start Free Trial
              <ArrowRight size={20} style={{ marginLeft: spacing[2] }} />
            </button>

            <button
              style={{
                padding: `${spacing[4]} ${spacing[8]}`,
                fontSize: typography.fontSize.lg,
                fontWeight: typography.fontWeight.semibold,
                backgroundColor: 'transparent',
                color: 'white',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                borderRadius: borderRadius.xl,
                cursor: 'pointer',
                transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                backdropFilter: 'blur(10px)',
                transform: 'translateY(0)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.5)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              Schedule Demo
            </button>
          </div>

          {/* Trust indicators */}
          <div
            style={{
              marginTop: spacing[12],
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: spacing[8],
              flexWrap: 'wrap',
              opacity: 0.8,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing[2] }}>
              <CheckCircle size={20} />
              <span style={{ fontSize: typography.fontSize.sm }}>No credit card required</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing[2] }}>
              <CheckCircle size={20} />
              <span style={{ fontSize: typography.fontSize.sm }}>14-day free trial</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing[2] }}>
              <CheckCircle size={20} />
              <span style={{ fontSize: typography.fontSize.sm }}>Cancel anytime</span>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}