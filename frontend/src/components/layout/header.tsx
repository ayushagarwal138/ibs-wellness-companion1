'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Heart, Menu, X, User, LogOut, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/auth-context';
import { colors, spacing, typography, layout } from '@/lib/design-system';

interface HeaderProps {
  variant?: 'default' | 'transparent';
  showAuth?: boolean;
}

export function Header({ variant = 'default', showAuth = true }: HeaderProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/');
    setIsUserMenuOpen(false);
  };

  const navigationItems = [
    { href: '/dashboard', label: 'Dashboard', requiresAuth: true },
    { href: '/chat', label: 'Chat Assistant', requiresAuth: true },
    { href: '/features', label: 'Features', requiresAuth: false },
    { href: '/about', label: 'About', requiresAuth: false },
    { href: '/contact', label: 'Contact', requiresAuth: false },
  ];

  const headerStyle = {
    backgroundColor: variant === 'transparent' ? 'transparent' : 'white',
    borderBottom: variant === 'transparent' ? 'none' : `1px solid ${colors.neutral[200]}`,
    backdropFilter: variant === 'transparent' ? 'blur(10px)' : 'none',
  };

  return (
    <header 
      className="sticky top-0 z-50 w-full transition-all duration-300"
      style={headerStyle}
    >
      <div 
        className="container mx-auto flex items-center justify-between"
        style={{ 
          maxWidth: layout.container.maxWidth,
          padding: `0 ${layout.container.padding}`,
          height: layout.header.height 
        }}
      >
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2 group">
          <div 
            className="transition-transform duration-300 group-hover:scale-110"
            style={{ color: colors.primary[600] }}
          >
            <Heart className="h-8 w-8" />
          </div>
          <span 
            className="text-2xl font-bold transition-colors duration-300"
            style={{ 
              fontWeight: typography.fontWeight.bold,
              fontSize: typography.fontSize['2xl'],
              color: colors.neutral[900]
            }}
          >
            IBS Wellness
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          {navigationItems.map((item) => {
            if (item.requiresAuth && !user) return null;
            if (!item.requiresAuth && user && item.href === '/features') return null;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className="text-gray-600 hover:text-gray-900 transition-colors duration-300 font-medium"
                style={{
                  fontSize: typography.fontSize.base,
                  fontWeight: typography.fontWeight.medium,
                }}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Desktop Auth Section */}
        {showAuth && (
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors duration-300"
                  style={{
                    borderRadius: '0.5rem',
                    padding: spacing[2],
                  }}
                >
                  <div 
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white font-medium"
                    style={{
                      backgroundColor: colors.primary[600],
                      fontSize: typography.fontSize.sm,
                    }}
                  >
                    {user.email?.charAt(0).toUpperCase()}
                  </div>
                  <span 
                    className="text-gray-700 font-medium"
                    style={{ fontSize: typography.fontSize.sm }}
                  >
                    {user.email}
                  </span>
                </button>

                {/* User Dropdown Menu */}
                {isUserMenuOpen && (
                  <div 
                    className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
                    style={{
                      borderRadius: '0.5rem',
                      border: `1px solid ${colors.neutral[200]}`,
                      boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
                    }}
                  >
                    <Link
                      href="/dashboard/settings"
                      className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                      onClick={() => setIsUserMenuOpen(false)}
                    >
                      <Settings className="h-4 w-4" />
                      <span>Settings</span>
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors duration-200 w-full text-left"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link href="/login">
                  <Button 
                    variant="ghost" 
                    className="font-medium"
                    style={{
                      color: colors.neutral[600],
                      fontSize: typography.fontSize.base,
                    }}
                  >
                    Sign In
                  </Button>
                </Link>
                <Link href="/register">
                  <Button 
                    className="font-semibold"
                    style={{
                      backgroundColor: colors.primary[600],
                      color: 'white',
                      fontSize: typography.fontSize.base,
                      fontWeight: typography.fontWeight.semibold,
                      padding: `${spacing[3]} ${spacing[4]}`,
                      borderRadius: '0.5rem',
                    }}
                  >
                    Get Started
                  </Button>
                </Link>
              </div>
            )}
          </div>
        )}

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors duration-300"
          style={{
            padding: spacing[2],
            borderRadius: '0.5rem',
          }}
        >
          {isMobileMenuOpen ? (
            <X className="h-6 w-6" style={{ color: colors.neutral[600] }} />
          ) : (
            <Menu className="h-6 w-6" style={{ color: colors.neutral[600] }} />
          )}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div 
          className="md:hidden bg-white border-t border-gray-200"
          style={{
            borderTop: `1px solid ${colors.neutral[200]}`,
            backgroundColor: 'white',
          }}
        >
          <div 
            className="container mx-auto py-4"
            style={{ 
              maxWidth: layout.container.maxWidth,
              padding: `${spacing[4]} ${layout.container.padding}`,
            }}
          >
            <nav className="flex flex-col space-y-4">
              {navigationItems.map((item) => {
                if (item.requiresAuth && !user) return null;
                if (!item.requiresAuth && user && item.href === '/features') return null;
                
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="text-gray-600 hover:text-gray-900 transition-colors duration-300 font-medium py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                    style={{
                      fontSize: typography.fontSize.base,
                      fontWeight: typography.fontWeight.medium,
                    }}
                  >
                    {item.label}
                  </Link>
                );
              })}
              
              {showAuth && (
                <div className="pt-4 border-t border-gray-200 space-y-3">
                  {user ? (
                    <>
                      <div className="flex items-center space-x-3 py-2">
                        <div 
                          className="w-8 h-8 rounded-full flex items-center justify-center text-white font-medium"
                          style={{
                            backgroundColor: colors.primary[600],
                            fontSize: typography.fontSize.sm,
                          }}
                        >
                          {user.email?.charAt(0).toUpperCase()}
                        </div>
                        <span 
                          className="text-gray-700 font-medium"
                          style={{ fontSize: typography.fontSize.sm }}
                        >
                          {user.email}
                        </span>
                      </div>
                      <Link
                        href="/dashboard/settings"
                        className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-300 py-2"
                        onClick={() => setIsMobileMenuOpen(false)}
                      >
                        <Settings className="h-4 w-4" />
                        <span>Settings</span>
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-300 py-2 w-full text-left"
                      >
                        <LogOut className="h-4 w-4" />
                        <span>Sign Out</span>
                      </button>
                    </>
                  ) : (
                    <>
                      <Link 
                        href="/login" 
                        className="block w-full text-center py-3 text-gray-600 hover:text-gray-900 transition-colors duration-300 font-medium"
                        onClick={() => setIsMobileMenuOpen(false)}
                      >
                        Sign In
                      </Link>
                      <Link 
                        href="/register" 
                        className="block w-full text-center py-3 text-white rounded-lg font-semibold transition-colors duration-300"
                        onClick={() => setIsMobileMenuOpen(false)}
                        style={{
                          backgroundColor: colors.primary[600],
                          borderRadius: '0.5rem',
                        }}
                      >
                        Get Started
                      </Link>
                    </>
                  )}
                </div>
              )}
            </nav>
          </div>
        </div>
      )}
    </header>
  );
}