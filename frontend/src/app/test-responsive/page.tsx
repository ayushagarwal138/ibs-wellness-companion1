'use client';

import React from 'react';
import { useResponsive, useBreakpoint, useResponsiveValue } from '@/hooks/useResponsive';
import { ResponsiveContainer, ResponsiveGrid, ResponsiveStack, ResponsiveText } from '@/components/ui/responsive-utils';
import { ResponsiveLayout, ResponsiveSection, ResponsiveCardGrid } from '@/components/layout/responsive-layout';
import { ClientOnly } from '@/components/ui/client-only';
import { MobileTouchTest } from '@/components/ui/mobile-touch-test';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Monitor, 
  Tablet, 
  Smartphone, 
  Laptop, 
  Heart, 
  Activity, 
  TrendingUp, 
  Users,
  BarChart3,
  PieChart,
  LineChart,
  Calendar
} from 'lucide-react';

export default function ResponsiveTestPage() {
  const responsive = useResponsive();
  const isDesktop = useBreakpoint('lg');
  const isTablet = useBreakpoint('md');
  
  const gridCols = useResponsiveValue({
    xs: 1,
    sm: 2,
    md: 2,
    lg: 3,
    xl: 4
  });

  const cardSpacing = useResponsiveValue({
    xs: 'sm',
    md: 'md',
    lg: 'lg'
  });

  return (
    <ResponsiveLayout variant="dashboard" maxWidth="xl" padding="lg">
      {/* Header Section */}
      <ResponsiveSection 
        title="Responsive Design Test" 
        subtitle="Testing responsive behavior across different screen sizes and devices"
        spacing="md"
      >
        <ResponsiveContainer size="full" padding="none">
          {/* Current Breakpoint Info */}
          <Card className="card-professional mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ClientOnly fallback={<Monitor className="h-5 w-5 text-purple-500" />}>
                  {responsive.isMobile && <Smartphone className="h-5 w-5 text-blue-500" />}
                  {responsive.isTablet && <Tablet className="h-5 w-5 text-green-500" />}
                  {responsive.isDesktop && <Monitor className="h-5 w-5 text-purple-500" />}
                </ClientOnly>
                Current Screen Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveGrid cols={{ default: 1, sm: 2, lg: 4 }} gap="md">
                <div className="space-y-2">
                  <p className="text-label">Screen Size</p>
                  <ClientOnly fallback={<p className="text-2xl font-bold text-primary">1024 × 768</p>}>
                    <p className="text-2xl font-bold text-primary">
                      {responsive.width} × {responsive.height}
                    </p>
                  </ClientOnly>
                </div>
                <div className="space-y-2">
                  <p className="text-label">Current Breakpoint</p>
                  <ClientOnly fallback={<Badge variant="outline" className="text-lg px-3 py-1">lg</Badge>}>
                    <Badge variant="outline" className="text-lg px-3 py-1">
                      {responsive.currentBreakpoint}
                    </Badge>
                  </ClientOnly>
                </div>
                <div className="space-y-2">
                  <p className="text-label">Device Type</p>
                  <ClientOnly fallback={<p className="text-lg font-semibold">Desktop</p>}>
                    <p className="text-lg font-semibold">
                      {responsive.isMobile && 'Mobile'}
                      {responsive.isTablet && 'Tablet'}
                      {responsive.isDesktop && 'Desktop'}
                    </p>
                  </ClientOnly>
                </div>
                <div className="space-y-2">
                  <p className="text-label">Grid Columns</p>
                  <ClientOnly fallback={<p className="text-lg font-semibold text-green-600">3 columns</p>}>
                    <p className="text-lg font-semibold text-green-600">
                      {gridCols} columns
                    </p>
                  </ClientOnly>
                </div>
              </ResponsiveGrid>
            </CardContent>
          </Card>

          {/* Responsive Grid Test */}
          <ResponsiveSection title="Responsive Grid System" spacing="sm">
            <ResponsiveCardGrid 
              cols={{ default: 1, sm: 2, md: 3, lg: 4 }} 
              gap="md"
              minCardWidth="250px"
            >
              <Card className="card-health">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Heart className="h-5 w-5 text-red-500" />
                    Health Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-caption">Wellness Score</span>
                      <span className="font-semibold">85%</span>
                    </div>
                    <Progress value={85} className="h-2" />
                    <p className="text-caption">Excellent progress this week!</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-wellness">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-green-500" />
                    Activity Level
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-caption">Daily Goal</span>
                      <span className="font-semibold">92%</span>
                    </div>
                    <Progress value={92} className="h-2" />
                    <p className="text-caption">Almost reached your goal!</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-analytics">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-purple-500" />
                    Trends
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-caption">Improvement</span>
                      <span className="font-semibold text-green-600">+12%</span>
                    </div>
                    <Progress value={78} className="h-2" />
                    <p className="text-caption">Positive trend detected</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-premium">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-amber-500" />
                    Community
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-caption">Engagement</span>
                      <span className="font-semibold">High</span>
                    </div>
                    <Progress value={95} className="h-2" />
                    <p className="text-caption">Active community member</p>
                  </div>
                </CardContent>
              </Card>
            </ResponsiveCardGrid>
          </ResponsiveSection>

          {/* Responsive Stack Test */}
          <ResponsiveSection title="Responsive Stack Layout" spacing="sm">
            <Card className="card-professional">
              <CardContent className="p-6">
                <ResponsiveStack direction="responsive" spacing="lg" align="center">
                  <div className="flex-1 space-y-4">
                    <ResponsiveText variant="heading" color="health">
                      Flexible Layout
                    </ResponsiveText>
                    <ResponsiveText variant="body" color="muted">
                      This layout automatically stacks vertically on mobile devices and 
                      arranges horizontally on larger screens. The spacing and alignment 
                      adjust based on the current breakpoint.
                    </ResponsiveText>
                    <div className="flex flex-wrap gap-2">
                      <Button className="btn-health">Primary Action</Button>
                      <Button variant="outline">Secondary</Button>
                    </div>
                  </div>
                  
                  <div className="flex-shrink-0">
                    <div className="grid grid-cols-2 gap-4 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl">
                      <div className="text-center">
                        <BarChart3 className="h-8 w-8 mx-auto text-blue-500 mb-2" />
                        <p className="text-caption">Analytics</p>
                      </div>
                      <div className="text-center">
                        <PieChart className="h-8 w-8 mx-auto text-green-500 mb-2" />
                        <p className="text-caption">Reports</p>
                      </div>
                      <div className="text-center">
                        <LineChart className="h-8 w-8 mx-auto text-purple-500 mb-2" />
                        <p className="text-caption">Trends</p>
                      </div>
                      <div className="text-center">
                        <Calendar className="h-8 w-8 mx-auto text-amber-500 mb-2" />
                        <p className="text-caption">Schedule</p>
                      </div>
                    </div>
                  </div>
                </ResponsiveStack>
              </CardContent>
            </Card>
          </ResponsiveSection>

          {/* Typography Test */}
          <ResponsiveSection title="Responsive Typography" spacing="sm">
            <Card className="card-gradient">
              <CardContent className="p-6 space-y-6">
                <ResponsiveText variant="hero" align="responsive" className="gradient-text-primary">
                  Hero Heading
                </ResponsiveText>
                <ResponsiveText variant="heading" align="responsive" color="health">
                  Section Heading
                </ResponsiveText>
                <ResponsiveText variant="subheading" align="responsive" color="wellness">
                  Subheading Text
                </ResponsiveText>
                <ResponsiveText variant="body" align="responsive">
                  This is body text that demonstrates how typography scales across different 
                  screen sizes. The text size, line height, and spacing automatically adjust 
                  to provide optimal readability on all devices.
                </ResponsiveText>
                <ResponsiveText variant="caption" align="responsive" color="muted">
                  Caption text for additional information and context.
                </ResponsiveText>
              </CardContent>
            </Card>
          </ResponsiveSection>

          {/* Button Test */}
          <ResponsiveSection title="Responsive Buttons" spacing="sm">
            <Card className="card-professional">
              <CardContent className="p-6">
                <ResponsiveStack direction="responsive" spacing="md" justify="center">
                  <Button className="btn-gradient mobile-full">
                    Gradient Button
                  </Button>
                  <Button className="btn-health mobile-full">
                    Health Action
                  </Button>
                  <Button className="btn-wellness mobile-full">
                    Wellness Action
                  </Button>
                  <Button className="btn-premium mobile-full">
                    Premium Feature
                  </Button>
                  <Button variant="outline" className="mobile-full">
                    Outline Button
                  </Button>
                </ResponsiveStack>
              </CardContent>
            </Card>
          </ResponsiveSection>

          {/* Responsive Visibility Test */}
          <ResponsiveSection title="Responsive Visibility" spacing="sm">
            <div className="grid gap-4">
              <Card className="card-professional">
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div className="block sm:hidden">
                      <Badge variant="secondary" className="mb-2">Mobile Only</Badge>
                      <p className="text-body">This content is only visible on mobile devices (below 640px).</p>
                    </div>
                    
                    <div className="hidden sm:block md:hidden">
                      <Badge variant="secondary" className="mb-2">Small Screens Only</Badge>
                      <p className="text-body">This content is only visible on small screens (640px - 768px).</p>
                    </div>
                    
                    <div className="hidden md:block lg:hidden">
                      <Badge variant="secondary" className="mb-2">Medium Screens Only</Badge>
                      <p className="text-body">This content is only visible on medium screens (768px - 1024px).</p>
                    </div>
                    
                    <div className="hidden lg:block">
                      <Badge variant="secondary" className="mb-2">Large Screens Only</Badge>
                      <p className="text-body">This content is only visible on large screens (1024px and above).</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </ResponsiveSection>

          {/* Test Summary */}
          {/* Mobile Touch Testing */}
          <ResponsiveSection 
            title="Mobile Touch Testing" 
            spacing="lg"
          >
            <MobileTouchTest />
          </ResponsiveSection>

          <ResponsiveSection title="Test Summary" spacing="sm">
            <Card className="card-floating">
              <CardContent className="p-6">
                <div className="text-center space-y-4">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                    <Monitor className="h-8 w-8 text-green-600" />
                  </div>
                  <ResponsiveText variant="heading" color="wellness">
                    Responsive Design Test Complete
                  </ResponsiveText>
                  <ResponsiveText variant="body" color="muted">
                    All responsive components are working correctly across different screen sizes. 
                    The layout adapts seamlessly from mobile to desktop viewports.
                  </ResponsiveText>
                  <div className="flex justify-center">
                    <Button className="btn-wellness">
                      Return to Dashboard
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </ResponsiveSection>
        </ResponsiveContainer>
      </ResponsiveSection>
    </ResponsiveLayout>
  );
}