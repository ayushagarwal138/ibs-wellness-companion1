'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Menu, X, User, UserPlus, ChevronDown, LogOut } from 'lucide-react';
import { colors, typography, spacing, borderRadius, shadows, animations } from '@/lib/design-system';
import { useAuth } from '@/contexts/auth-context';

interface HeaderProps {
  variant?: 'default' | 'transparent' | 'solid';
  showAuth?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ 
  variant = 'default', 
  showAuth = true 
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { user, logout, loading } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { label: 'Features', href: '#features' },
    { label: 'How it Works', href: '#how-it-works' },
    { label: 'About', href: '#about' },
    { label: 'Contact', href: '#contact' },
  ];

  const getHeaderStyle = () => {
    const baseStyle = {
      position: 'fixed' as const,
      top: 0,
      left: 0,
      right: 0,
      zIndex: 1000,
      transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
    };

    if (variant === 'transparent' && !isScrolled) {
      return {
        ...baseStyle,
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      };
    }

    if (variant === 'transparent' && isScrolled) {
      return {
        ...baseStyle,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(25px)',
        borderBottom: `1px solid ${colors.neutral[200]}`,
        boxShadow: shadows.lg,
      };
    }

    return {
      ...baseStyle,
      backgroundColor: 'rgba(255, 255, 255, 0.98)',
      backdropFilter: 'blur(20px)',
      borderBottom: `1px solid ${colors.neutral[200]}`,
      boxShadow: shadows.md,
    };
  };

  const getTextColor = () => {
    if (variant === 'transparent' && !isScrolled) {
      return 'white';
    }
    return colors.neutral[800];
  };

  const getLinkStyle = (isActive = false) => ({
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
    color: getTextColor(),
    textDecoration: 'none',
    padding: `${spacing[2]} ${spacing[4]}`,
    borderRadius: borderRadius.md,
    transition: `all ${animations.duration.fast} ${animations.easing.smooth}`,
    position: 'relative' as const,
    opacity: isActive ? 1 : 0.9,
    '&:hover': {
      opacity: 1,
      backgroundColor: variant === 'transparent' || !isScrolled 
        ? 'rgba(255, 255, 255, 0.1)' 
        : colors.neutral[50],
    }
  });

  return (
    <header style={getHeaderStyle()}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          maxWidth: '1400px',
          margin: '0 auto',
          padding: `0 ${spacing[8]}`,
          height: '80px',
        }}
      >
        {/* Enhanced Logo - Left Corner */}
        <div style={{ flex: '0 0 auto' }}>
          <Link
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              textDecoration: 'none',
              gap: spacing[3],
              transition: `all ${animations.duration.fast} ${animations.easing.smooth}`,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.02)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            {/* Professional Logo Icon */}
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: borderRadius.xl,
                background: `linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[700]} 50%, ${colors.primary[800]} 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: `0 4px 20px rgba(37, 99, 235, 0.3)`,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Logo Symbol */}
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  fontWeight: typography.fontWeight.bold,
                  color: colors.primary[700],
                }}
              >
                W
              </div>
              
              {/* Subtle glow effect */}
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%)',
                  animation: 'shimmer 3s ease-in-out infinite',
                }}
              />
            </div>
            
            {/* Brand Text */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <span
                style={{
                  fontSize: typography.fontSize.xl,
                  fontWeight: typography.fontWeight.bold,
                  color: getTextColor(),
                  lineHeight: 1,
                  letterSpacing: '-0.02em',
                }}
              >
                IBS Wellness
              </span>
              <span
                style={{
                    fontSize: typography.fontSize.xs,
                    fontWeight: typography.fontWeight.medium,
                    color: variant === 'transparent' && !isScrolled ? 'rgba(255, 255, 255, 0.8)' : colors.neutral[600],
                    lineHeight: 1,
                    letterSpacing: '0.05em',
                    textTransform: 'uppercase',
                  }}
              >
                Companion
              </span>
            </div>
          </Link>
        </div>

        {/* Centered Desktop Navigation */}
        <div style={{ flex: '1 1 auto', display: 'flex', justifyContent: 'center' }}>
          <nav
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: spacing[1],
              backgroundColor: variant === 'transparent' && !isScrolled 
                ? 'rgba(255, 255, 255, 0.08)'
                : 'rgba(0, 0, 0, 0.03)',
              padding: `${spacing[2]} ${spacing[6]}`,
              borderRadius: borderRadius['2xl'],
              backdropFilter: 'blur(15px)',
              border: `1px solid ${variant === 'transparent' && !isScrolled 
                ? 'rgba(255, 255, 255, 0.15)' 
                : colors.neutral[200]}`,
              boxShadow: variant === 'transparent' && !isScrolled 
                ? '0 8px 32px rgba(0, 0, 0, 0.1)' 
                : shadows.sm,
            }}
            className="desktop-nav"
          >
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                style={{
                  ...getLinkStyle(),
                  padding: `${spacing[3]} ${spacing[4]}`,
                  borderRadius: borderRadius.lg,
                  fontWeight: typography.fontWeight.semibold,
                  fontSize: typography.fontSize.sm,
                  position: 'relative',
                  overflow: 'hidden',
                  transition: `all ${animations.duration.fast} ${animations.easing.smooth}`,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = variant === 'transparent' && !isScrolled 
                    ? 'rgba(255, 255, 255, 0.2)' 
                    : colors.primary[50];
                  e.currentTarget.style.color = variant === 'transparent' && !isScrolled 
                    ? 'white' 
                    : colors.primary[700];
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = shadows.sm;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = getTextColor();
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Auth Buttons */}
        {showAuth && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: spacing[3],
            }}
            className="desktop-auth"
          >
            {user ? (
              // Authenticated user menu
              <div style={{ display: 'flex', alignItems: 'center', gap: spacing[3] }}>
                {/* User info */}
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: spacing[2],
                  color: getTextColor(),
                  fontSize: typography.fontSize.sm,
                  fontWeight: typography.fontWeight.medium
                }}>
                  <User size={18} />
                  <span>Welcome, {user.first_name || user.email}</span>
                </div>
                
                {/* Dashboard Button */}
                <Link
                  href="/dashboard"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: `${spacing[2]} ${spacing[4]}`,
                    fontSize: typography.fontSize.sm,
                    fontWeight: typography.fontWeight.semibold,
                    borderRadius: borderRadius.lg,
                    cursor: 'pointer',
                    transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                    textDecoration: 'none',
                    backgroundColor: 'transparent',
                    color: getTextColor(),
                    border: `1px solid ${variant === 'transparent' && !isScrolled ? 'rgba(255, 255, 255, 0.3)' : colors.neutral[300]}`,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = variant === 'transparent' && !isScrolled 
                      ? 'rgba(255, 255, 255, 0.15)' 
                      : colors.neutral[50];
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  Dashboard
                </Link>

                {/* Logout Button */}
                <button
                  onClick={logout}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: `${spacing[2]} ${spacing[4]}`,
                    fontSize: typography.fontSize.sm,
                    fontWeight: typography.fontWeight.semibold,
                    borderRadius: borderRadius.lg,
                    cursor: 'pointer',
                    transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                    backgroundColor: 'transparent',
                    color: getTextColor(),
                    border: `1px solid ${variant === 'transparent' || !isScrolled ? 'rgba(255, 255, 255, 0.3)' : colors.neutral[300]}`,
                  }}
                  onMouseEnter={(e) => {
                     e.currentTarget.style.backgroundColor = colors.accent.red[50];
                     e.currentTarget.style.color = colors.accent.red[600];
                     e.currentTarget.style.borderColor = colors.accent.red[300];
                   }}
                   onMouseLeave={(e) => {
                     e.currentTarget.style.backgroundColor = 'transparent';
                     e.currentTarget.style.color = getTextColor();
                     e.currentTarget.style.borderColor = variant === 'transparent' || !isScrolled 
                       ? 'rgba(255, 255, 255, 0.3)' 
                       : colors.neutral[300];
                   }}
                >
                  <LogOut size={16} style={{ marginRight: spacing[1] }} />
                  Sign Out
                </button>
              </div>
            ) : (
              // Unauthenticated user buttons
              <div style={{ display: 'flex', alignItems: 'center', gap: spacing[3] }}>
                {/* Professional CTA Badge */}
                <div
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: `${spacing[1]} ${spacing[3]}`,
                    fontSize: typography.fontSize.xs,
                    fontWeight: typography.fontWeight.medium,
                    borderRadius: borderRadius.full,
                    background: `linear-gradient(135deg, ${colors.primary[100]} 0%, ${colors.primary[200]} 100%)`,
                    color: colors.primary[800],
                    border: `1px solid ${colors.primary[300]}`,
                    animation: 'pulse-glow 2s ease-in-out infinite',
                  }}
                >
                  ✨ Free Trial Available
                </div>

                {/* Enhanced Sign In Button */}
                <Link
                  href="/login"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: `${spacing[3]} ${spacing[6]}`,
                    fontSize: typography.fontSize.sm,
                    fontWeight: typography.fontWeight.semibold,
                    borderRadius: borderRadius.xl,
                    cursor: 'pointer',
                    transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                    textDecoration: 'none',
                    transform: 'translateY(0)',
                    backgroundColor: 'transparent',
                    color: getTextColor(),
                    border: `2px solid ${variant === 'transparent' && !isScrolled ? 'rgba(255, 255, 255, 0.3)' : colors.neutral[300]}`,
                    backdropFilter: 'blur(10px)',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = variant === 'transparent' && !isScrolled 
                      ? 'rgba(255, 255, 255, 0.15)' 
                      : colors.neutral[50];
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.borderColor = variant === 'transparent' && !isScrolled 
                      ? 'rgba(255, 255, 255, 0.6)' 
                      : colors.primary[400];
                    e.currentTarget.style.boxShadow = shadows.lg;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.borderColor = variant === 'transparent' && !isScrolled 
                      ? 'rgba(255, 255, 255, 0.3)' 
                      : colors.neutral[300];
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <User size={18} style={{ marginRight: spacing[2] }} />
                  Sign In
                </Link>
                
                {/* Premium Sign Up Button */}
                <Link
                  href="/register"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: `${spacing[3]} ${spacing[8]}`,
                    fontSize: typography.fontSize.sm,
                    fontWeight: typography.fontWeight.bold,
                    borderRadius: borderRadius.xl,
                    cursor: 'pointer',
                    transition: `all ${animations.duration.normal} ${animations.easing.smooth}`,
                    border: 'none',
                    textDecoration: 'none',
                    transform: 'translateY(0)',
                    background: `linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[700]} 50%, ${colors.primary[800]} 100%)`,
                    color: 'white',
                    boxShadow: `0 8px 32px rgba(37, 99, 235, 0.3)`,
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = `linear-gradient(135deg, ${colors.primary[700]} 0%, ${colors.primary[800]} 50%, ${colors.primary[900]} 100%)`;
                    e.currentTarget.style.transform = 'translateY(-3px) scale(1.05)';
                    e.currentTarget.style.boxShadow = `0 12px 40px rgba(37, 99, 235, 0.4)`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = `linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[700]} 50%, ${colors.primary[800]} 100%)`;
                    e.currentTarget.style.transform = 'translateY(0) scale(1)';
                    e.currentTarget.style.boxShadow = `0 8px 32px rgba(37, 99, 235, 0.3)`;
                  }}
                >
                  <UserPlus size={18} style={{ marginRight: spacing[2] }} />
                  Start Free Trial
                  
                  {/* Shimmer Effect */}
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: '-100%',
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                    animation: 'shimmer 2s ease-in-out infinite',
                  }} />
                  
                  {/* Professional Badge */}
                  <div style={{
                    position: 'absolute',
                    top: '-2px',
                    right: '-2px',
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: `linear-gradient(135deg, ${colors.accent.purple[400]} 0%, ${colors.accent.purple[600]} 100%)`,
                    animation: 'pulse-glow 1.5s ease-in-out infinite',
                  }} />
                </Link>
              </div>
            )}
          </div>
        )}

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          style={{
            display: 'none',
            alignItems: 'center',
            justifyContent: 'center',
            width: '40px',
            height: '40px',
            backgroundColor: 'transparent',
            border: 'none',
            borderRadius: borderRadius.md,
            cursor: 'pointer',
            color: getTextColor(),
          }}
          className="mobile-menu-btn"
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            backgroundColor: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(20px)',
            borderBottom: `1px solid ${colors.neutral[200]}`,
            boxShadow: shadows.xl,
            padding: spacing[6],
            animation: `slideDown ${animations.duration.normal} ${animations.easing.smooth}`,
            display: 'none',
          }}
          className="mobile-menu"
        >
          <nav
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: spacing[1],
            }}
          >
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                style={{
                  ...getLinkStyle(),
                  color: colors.neutral[800],
                  padding: `${spacing[3]} ${spacing[4]}`,
                  borderRadius: borderRadius.md,
                  fontWeight: typography.fontWeight.medium,
                }}
              >
                {item.label}
              </Link>
            ))}
            
            {showAuth && (
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: spacing[3],
                  marginTop: spacing[6],
                  paddingTop: spacing[6],
                  borderTop: `1px solid ${colors.neutral[200]}`,
                }}
              >
                {user ? (
                  // Authenticated user mobile menu
                  <>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: spacing[2],
                      padding: `${spacing[3]} ${spacing[4]}`,
                      backgroundColor: colors.neutral[50],
                      borderRadius: borderRadius.md,
                      color: colors.neutral[700],
                      fontSize: typography.fontSize.sm,
                      fontWeight: typography.fontWeight.medium,
                    }}>
                      <User size={16} />
                      <span>Welcome, {user.first_name || user.email}</span>
                    </div>
                    
                    <Link
                      href="/dashboard"
                      onClick={() => setIsMobileMenuOpen(false)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: `${spacing[3]} ${spacing[6]}`,
                        backgroundColor: 'transparent',
                        color: colors.neutral[700],
                        border: `1px solid ${colors.neutral[300]}`,
                        borderRadius: borderRadius.md,
                        textDecoration: 'none',
                        fontWeight: typography.fontWeight.medium,
                        transition: `all ${animations.duration.fast} ${animations.easing.smooth}`,
                      }}
                    >
                      Dashboard
                    </Link>
                    
                    <button
                      onClick={() => {
                        logout();
                        setIsMobileMenuOpen(false);
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: `${spacing[3]} ${spacing[6]}`,
                        backgroundColor: 'transparent',
                        color: colors.accent.red[600],
                        border: `1px solid ${colors.accent.red[300]}`,
                        borderRadius: borderRadius.md,
                        fontWeight: typography.fontWeight.medium,
                        transition: `all ${animations.duration.fast} ${animations.easing.smooth}`,
                        cursor: 'pointer',
                      }}
                    >
                      <LogOut size={16} style={{ marginRight: spacing[2] }} />
                      Sign Out
                    </button>
                  </>
                ) : (
                  // Unauthenticated user mobile menu
                  <>
                    <Link
                      href="/login"
                      onClick={() => setIsMobileMenuOpen(false)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: `${spacing[3]} ${spacing[6]}`,
                        backgroundColor: 'transparent',
                        color: colors.neutral[700],
                        border: `1px solid ${colors.neutral[300]}`,
                        borderRadius: borderRadius.md,
                        textDecoration: 'none',
                        fontWeight: typography.fontWeight.medium,
                        transition: `all ${animations.duration.fast} ${animations.easing.smooth}`,
                      }}
                    >
                      <User size={16} style={{ marginRight: spacing[2] }} />
                      Sign In
                    </Link>
                    
                    <Link
                      href="/register"
                      onClick={() => setIsMobileMenuOpen(false)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: `${spacing[3]} ${spacing[6]}`,
                        background: `linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[700]} 100%)`,
                        color: 'white',
                        border: 'none',
                        borderRadius: borderRadius.md,
                        textDecoration: 'none',
                        fontWeight: typography.fontWeight.semibold,
                        boxShadow: shadows.md,
                        transition: `all ${animations.duration.fast} ${animations.easing.smooth}`,
                      }}
                    >
                      <UserPlus size={16} style={{ marginRight: spacing[2] }} />
                      Start Free Trial
                    </Link>
                  </>
                )}
              </div>
            )}
          </nav>
        </div>
      )}

      {/* Add keyframes for animations */}
      <style jsx>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes shimmer {
          0% {
            left: -100%;
          }
          100% {
            left: 100%;
          }
        }
        
        @keyframes pulse-glow {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.7;
            transform: scale(1.1);
          }
        }

        /* Responsive styles */
        @media (max-width: 1023px) {
          .desktop-nav {
            display: none !important;
          }
          .desktop-auth {
            display: none !important;
          }
          .mobile-menu-btn {
            display: flex !important;
          }
          .mobile-menu {
            display: block !important;
          }
        }

        @media (min-width: 1024px) {
          .desktop-nav {
            display: flex !important;
          }
          .desktop-auth {
            display: flex !important;
          }
          .mobile-menu-btn {
            display: none !important;
          }
          .mobile-menu {
            display: none !important;
          }
        }
      `}</style>
    </header>
  );
};