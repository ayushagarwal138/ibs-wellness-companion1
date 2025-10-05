'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Heart, Menu, X, LogOut, Settings, Bell, BarChart3, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/auth-context';
import { colors, spacing, typography, layout } from '@/lib/design-system';

interface HeaderProps {
  variant?: 'default' | 'transparent';
  showAuth?: boolean;
}

export function Header({ variant = 'default', showAuth = true }: HeaderProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push('/');
    setIsUserMenuOpen(false);
  };

  const navigationItems = [
    { href: '/dashboard', label: 'Dashboard', icon: BarChart3, requiresAuth: true },
    { href: '/analytics', label: 'Analytics', icon: Activity, requiresAuth: true },
    { href: '/chat', label: 'AI Assistant', icon: null, requiresAuth: true },
    { href: '/features', label: 'Features', icon: null, requiresAuth: false },
    { href: '/about', label: 'About', icon: null, requiresAuth: false },
  ];

  const headerStyle = {
    backgroundColor: variant === 'transparent' 
      ? (isScrolled ? 'rgba(255, 255, 255, 0.95)' : 'transparent')
      : (isScrolled ? 'rgba(255, 255, 255, 0.95)' : 'white'),
    borderBottom: variant === 'transparent' && !isScrolled 
      ? 'none' 
      : `1px solid ${isScrolled ? colors.neutral[100] : colors.neutral[200]}`,
    backdropFilter: (variant === 'transparent' || isScrolled) ? 'blur(20px)' : 'none',
    boxShadow: isScrolled ? '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)' : 'none',
  };

  return (
    <header 
      className={`sticky top-0 z-50 w-full transition-all duration-500 ${isScrolled ? 'glass-card' : ''}`}
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
        <Link href="/" className="flex items-center space-x-3 group">
          <div 
            className="relative p-2 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg"
          >
            <Heart className="h-6 w-6 text-white" />
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-400 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm"></div>
          </div>
          <div className="flex flex-col">
            <span 
              className="text-xl lg:text-2xl font-bold transition-colors duration-300 bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent"
              style={{ 
                fontWeight: typography.fontWeight.bold,
                lineHeight: '1.2'
              }}
            >
              IBS Wellness
            </span>
            <span className="text-xs text-gray-500 font-medium hidden sm:block">
              AI-Powered Health Companion
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden lg:flex items-center space-x-1">
          {navigationItems.map((item) => {
            if (item.requiresAuth && !user) return null;
            if (!item.requiresAuth && user && item.href === '/features') return null;
            
            const IconComponent = item.icon;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-all duration-300 font-medium group"
                style={{
                  fontSize: typography.fontSize.sm,
                  fontWeight: typography.fontWeight.medium,
                }}
              >
                {IconComponent && (
                  <IconComponent className="h-4 w-4 transition-transform duration-300 group-hover:scale-110" />
                )}
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Desktop Auth Section */}
        {showAuth && (
          <div className="hidden lg:flex items-center space-x-3">
            {user ? (
              <>
                {/* Notifications */}
                <button className="relative p-2 rounded-lg hover:bg-gray-50 transition-colors duration-300 group">
                  <Bell className="h-5 w-5 text-gray-600 group-hover:text-gray-900 transition-colors duration-300" />
                  <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center bg-red-500 text-white text-xs">
                    3
                  </Badge>
                </button>

                {/* User Menu */}
                <div className="relative">
                  <button
                    onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                    className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-all duration-300 group"
                  >
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold bg-gradient-to-br from-blue-500 to-purple-600 group-hover:shadow-md transition-all duration-300"
                        style={{
                          fontSize: typography.fontSize.sm,
                        }}
                      >
                        {user?.email?.charAt(0).toUpperCase()}
                      </div>
                      <div className="hidden xl:block text-left">
                        <div className="text-sm font-medium text-gray-900 truncate max-w-32">
                          {user?.email?.split('@')[0]}
                        </div>
                        <div className="text-xs text-gray-500">
                          Premium User
                        </div>
                      </div>
                    </div>
                    <X 
                      className={`h-4 w-4 text-gray-400 transition-transform duration-300 ${isUserMenuOpen ? 'rotate-45' : 'rotate-0'}`}
                    />
                  </button>

                  {/* User Dropdown Menu */}
                  {isUserMenuOpen && (
                    <div 
                      className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50 glass-card"
                      style={{
                        borderRadius: '0.75rem',
                        border: `1px solid ${colors.neutral[100]}`,
                        boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04)',
                      }}
                    >
                      <div className="px-4 py-3 border-b border-gray-100">
                        <div className="text-sm font-medium text-gray-900 truncate">
                          {user?.email?.split('@')[0]}
                        </div>
                        <div className="text-xs text-gray-500">
                          {user?.email}
                        </div>
                      </div>
                      <Link
                        href="/dashboard/settings"
                        className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-50 transition-colors duration-200 group"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        <Settings className="h-4 w-4 group-hover:scale-110 transition-transform duration-200" />
                        <span className="font-medium">Settings</span>
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="flex items-center space-x-3 px-4 py-3 text-red-600 hover:bg-red-50 transition-colors duration-200 w-full text-left group"
                      >
                        <LogOut className="h-4 w-4 group-hover:scale-110 transition-transform duration-200" />
                        <span className="font-medium">Sign Out</span>
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <Link href="/login">
                  <Button 
                    variant="ghost" 
                    className="font-medium hover:bg-gray-50"
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
                    className="font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-300"
                    style={{
                      color: 'white',
                      fontSize: typography.fontSize.base,
                      fontWeight: typography.fontWeight.semibold,
                      padding: `${spacing[3]} ${spacing[5]}`,
                      borderRadius: '0.75rem',
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
          className="lg:hidden p-2 rounded-lg hover:bg-gray-50 transition-colors duration-300"
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
          className="lg:hidden bg-white/95 backdrop-blur-lg border-t border-gray-200"
          style={{
            borderTop: `1px solid ${colors.neutral[200]}`,
          }}
        >
          <div 
            className="container mx-auto py-4"
            style={{ 
              maxWidth: layout.container.maxWidth,
              padding: `${spacing[4]} ${layout.container.padding}`,
            }}
          >
            <nav className="flex flex-col space-y-2">
              {navigationItems.map((item) => {
                if (item.requiresAuth && !user) return null;
                if (!item.requiresAuth && user && item.href === '/features') return null;
                
                const IconComponent = item.icon;
                
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center space-x-3 p-3 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors duration-300 font-medium"
                    onClick={() => setIsMobileMenuOpen(false)}
                    style={{
                      fontSize: typography.fontSize.base,
                      fontWeight: typography.fontWeight.medium,
                    }}
                  >
                    {IconComponent && (
                      <IconComponent className="h-5 w-5" />
                    )}
                    <span>{item.label}</span>
                  </Link>
                );
              })}
              
              {showAuth && (
                <div className="pt-4 border-t border-gray-200 space-y-3">
                  {user ? (
                    <>
                      <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <div 
                          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold bg-gradient-to-br from-blue-500 to-purple-600"
                          style={{
                            fontSize: typography.fontSize.sm,
                          }}
                        >
                          {user?.email?.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900 truncate">
                            {user?.email?.split('@')[0]}
                          </div>
                          <div className="text-xs text-gray-500">
                            {user?.email}
                          </div>
                        </div>
                      </div>
                      <Link
                        href="/dashboard/settings"
                        className="flex items-center space-x-3 p-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors duration-300"
                        onClick={() => setIsMobileMenuOpen(false)}
                      >
                        <Settings className="h-5 w-5" />
                        <span className="font-medium">Settings</span>
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="flex items-center space-x-3 p-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-300 w-full text-left"
                      >
                        <LogOut className="h-5 w-5" />
                        <span className="font-medium">Sign Out</span>
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
                        className="block w-full text-center py-3 text-white rounded-lg font-semibold transition-colors duration-300 bg-gradient-to-r from-blue-600 to-purple-600"
                        onClick={() => setIsMobileMenuOpen(false)}
                        style={{
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