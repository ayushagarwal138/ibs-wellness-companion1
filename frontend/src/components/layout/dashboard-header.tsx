'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ProfileDropdown } from '@/components/ui/profile-dropdown';
import { NotificationIcon } from '@/components/ui/notification-icon';
import { useNotificationState } from '@/hooks/useNotificationState';
import { Heart, BarChart3, PlusCircle, Calendar, MessageCircle, User, FileText, DollarSign } from 'lucide-react';

interface DashboardHeaderProps {
  title?: string;
  showBackButton?: boolean;
  backHref?: string;
}

export function DashboardHeader({ 
  title = "IBS Wellness Dashboard", 
  showBackButton = false, 
  backHref = "/dashboard" 
}: DashboardHeaderProps) {
  const pathname = usePathname();
  const currentPath = pathname || '';
  
  // Initialize notification state
  const {
    notifications,
    markAsRead,
    markAllAsRead,
    dismissNotification,
  } = useNotificationState();

  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: BarChart3,
      active: currentPath === '/dashboard',
    },
    {
      name: 'Profile',
      href: '/profile',
      icon: User,
      active: currentPath === '/profile' || currentPath.startsWith('/profile/'),
    },
    {
      name: 'Log Symptoms',
      href: '/dashboard/log-symptoms',
      icon: PlusCircle,
      active: currentPath === '/dashboard/log-symptoms',
    },
    {
      name: 'Diet History',
      href: '/diet-history',
      icon: Calendar,
      active: currentPath === '/diet-history',
    },
    {
      name: 'Chat Assistant',
      href: '/chat',
      icon: MessageCircle,
      active: currentPath === '/chat',
    },
    {
      name: 'Analytics',
      href: '/dashboard/analytics',
      icon: BarChart3,
      active: currentPath === '/dashboard/analytics',
    },
    // {
    //   name: 'Financial',
    //   href: '/financial',
    //   icon: DollarSign,
    //   active: currentPath === '/financial',
    // },
    {
      name: 'Reports',
      href: '/reports',
      icon: FileText,
      active: currentPath === '/reports',
    },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40 w-full">
      <div className="w-full px-4 sm:px-6 lg:px-8 xl:px-12">
        {/* Top Row - Logo, Title, Notifications, Profile */}
        <div className="flex justify-between items-center py-4">
          {/* Left Section - Logo and Title */}
          <div className="flex items-center space-x-4 flex-shrink-0">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <Heart className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900 hidden sm:block">
                IBS Wellness
              </span>
            </Link>
            
            {showBackButton && (
              <div className="flex items-center">
                <span className="text-gray-300 mx-2">/</span>
                <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
              </div>
            )}
          </div>

          {/* Right Section - Notifications and Profile */}
          <div className="flex items-center space-x-4 flex-shrink-0">
            {/* Notifications */}
            <NotificationIcon
              notifications={notifications}
              onMarkAsRead={markAsRead}
              onMarkAllAsRead={markAllAsRead}
              onDismiss={dismissNotification}
              onNotificationClick={(notification) => {
                // Handle notification click - could navigate to specific pages
                if (notification.actionUrl) {
                  window.location.href = notification.actionUrl;
                }
              }}
            />

            {/* Profile Dropdown */}
            <ProfileDropdown />
          </div>
        </div>

        {/* Bottom Row - Navigation (hidden on mobile) */}
        <div className="hidden lg:block border-t border-gray-100 py-3">
          <nav className="flex items-center justify-center">
            <div className="flex items-center space-x-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 ${
                      item.active
                        ? 'bg-blue-100 text-blue-700 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="whitespace-nowrap">{item.name}</span>
                  </Link>
                );
              })}
            </div>
          </nav>
        </div>

        {/* Mobile Navigation */}
        <div className="lg:hidden border-t border-gray-200 py-3">
          <nav className="flex space-x-1 overflow-x-auto scrollbar-hide pb-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-200 hover:scale-105 ${
                    item.active
                      ? 'bg-blue-100 text-blue-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}