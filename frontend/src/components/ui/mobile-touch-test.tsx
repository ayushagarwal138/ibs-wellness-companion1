'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ClientOnly } from '@/components/ui/client-only';
import { useTouchDevice } from '@/hooks/useResponsive';
import { 
  Smartphone, 
  MousePointer, 
  Fingerprint, 
  Move, 
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Hand
} from 'lucide-react';

interface TouchEvent {
  type: string;
  timestamp: number;
  touches: number;
  x?: number;
  y?: number;
}

export function MobileTouchTest() {
  const [touchEvents, setTouchEvents] = useState<TouchEvent[]>([]);
  const [swipeDirection, setSwipeDirection] = useState<string>('');
  const [pinchScale, setPinchScale] = useState(1);
  const [tapCount, setTapCount] = useState(0);
  const touchAreaRef = useRef<HTMLDivElement>(null);
  const isTouchDevice = useTouchDevice();
  
  const [startTouch, setStartTouch] = useState<{ x: number; y: number } | null>(null);
  const [lastTapTime, setLastTapTime] = useState(0);

  const addTouchEvent = (type: string, touches: number, x?: number, y?: number) => {
    const event: TouchEvent = {
      type,
      timestamp: Date.now(),
      touches,
      x,
      y,
    };
    
    setTouchEvents(prev => [...prev.slice(-9), event]); // Keep last 10 events
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    const touch = e.touches[0];
    if (!touch) return;
    setStartTouch({ x: touch.clientX, y: touch.clientY });
    addTouchEvent('Touch Start', e.touches.length, touch.clientX, touch.clientY);
    
    // Handle double tap
    const now = Date.now();
    if (now - lastTapTime < 300) {
      setTapCount(prev => prev + 1);
      addTouchEvent('Double Tap', e.touches.length);
    }
    setLastTapTime(now);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    e.preventDefault();
    const touch = e.touches[0];
    if (!touch) return;
    addTouchEvent('Touch Move', e.touches.length, touch.clientX, touch.clientY);
    
    if (startTouch && e.touches.length === 1) {
      const deltaX = touch.clientX - startTouch.x;
      const deltaY = touch.clientY - startTouch.y;
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      
      if (distance > 50) {
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          setSwipeDirection(deltaX > 0 ? 'Right' : 'Left');
        } else {
          setSwipeDirection(deltaY > 0 ? 'Down' : 'Up');
        }
      }
    }
    
    // Handle pinch gesture
    if (e.touches.length === 2) {
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      if (!touch1 || !touch2) return;
      const distance = Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) + 
        Math.pow(touch2.clientY - touch1.clientY, 2)
      );
      setPinchScale(distance / 100); // Normalize scale
      addTouchEvent('Pinch', e.touches.length);
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    addTouchEvent('Touch End', e.changedTouches.length);
    setStartTouch(null);
    
    // Reset swipe direction after a delay
    setTimeout(() => setSwipeDirection(''), 1000);
  };

  const clearEvents = () => {
    setTouchEvents([]);
    setSwipeDirection('');
    setPinchScale(1);
    setTapCount(0);
  };

  return (
    <div className="space-y-6">
      {/* Device Detection */}
      <Card className="card-professional">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smartphone className="h-5 w-5 text-blue-500" />
            Touch Device Detection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <ClientOnly fallback={<Badge variant="outline">Unknown</Badge>}>
              <Badge variant={isTouchDevice ? "default" : "secondary"}>
                {isTouchDevice ? "Touch Device" : "Non-Touch Device"}
              </Badge>
            </ClientOnly>
            <p className="text-caption">
              {isTouchDevice 
                ? "Touch interactions are supported on this device" 
                : "This device doesn't support touch interactions"
              }
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Touch Test Area */}
      <Card className="card-wellness">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MousePointer className="h-5 w-5 text-green-500" />
            Touch Interaction Test Area
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            ref={touchAreaRef}
            className="relative bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-8 min-h-[200px] border-2 border-dashed border-blue-300 touch-none select-none"
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
          >
            <div className="text-center space-y-4">
              <Hand className="h-12 w-12 mx-auto text-blue-500" />
              <p className="text-lg font-semibold text-blue-700">
                Touch, Swipe, or Pinch Here
              </p>
              <p className="text-caption text-blue-600">
                Try single touch, multi-touch, swipe gestures, and pinch to zoom
              </p>
            </div>
            
            {/* Visual feedback */}
            {swipeDirection && (
              <div className="absolute top-4 right-4">
                <Badge className="bg-green-500 text-white animate-bounce">
                  Swipe {swipeDirection}
                </Badge>
              </div>
            )}
            
            {pinchScale !== 1 && (
              <div className="absolute bottom-4 left-4">
                <Badge className="bg-purple-500 text-white">
                  Scale: {pinchScale.toFixed(2)}x
                </Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Touch Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="card-health">
          <CardContent className="p-4 text-center">
            <Fingerprint className="h-8 w-8 mx-auto text-red-500 mb-2" />
            <p className="text-2xl font-bold text-red-600">{tapCount}</p>
            <p className="text-caption">Double Taps</p>
          </CardContent>
        </Card>
        
        <Card className="card-analytics">
          <CardContent className="p-4 text-center">
            <Move className="h-8 w-8 mx-auto text-purple-500 mb-2" />
            <p className="text-2xl font-bold text-purple-600">
              {swipeDirection || 'None'}
            </p>
            <p className="text-caption">Last Swipe</p>
          </CardContent>
        </Card>
        
        <Card className="card-premium">
          <CardContent className="p-4 text-center">
            <ZoomIn className="h-8 w-8 mx-auto text-amber-500 mb-2" />
            <p className="text-2xl font-bold text-amber-600">
              {pinchScale.toFixed(1)}x
            </p>
            <p className="text-caption">Pinch Scale</p>
          </CardContent>
        </Card>
        
        <Card className="card-wellness">
          <CardContent className="p-4 text-center">
            <MousePointer className="h-8 w-8 mx-auto text-green-500 mb-2" />
            <p className="text-2xl font-bold text-green-600">{touchEvents.length}</p>
            <p className="text-caption">Touch Events</p>
          </CardContent>
        </Card>
      </div>

      {/* Touch Events Log */}
      <Card className="card-professional">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <RotateCcw className="h-5 w-5 text-gray-500" />
            Touch Events Log
          </CardTitle>
          <Button variant="outline" size="sm" onClick={clearEvents}>
            Clear Log
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {touchEvents.length === 0 ? (
              <p className="text-caption text-center py-4">
                No touch events recorded yet. Try interacting with the touch area above.
              </p>
            ) : (
              touchEvents.map((event, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm"
                >
                  <span className="font-medium">{event.type}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {event.touches} touch{event.touches !== 1 ? 'es' : ''}
                    </Badge>
                    {event.x && event.y && (
                      <span className="text-caption">
                        ({Math.round(event.x)}, {Math.round(event.y)})
                      </span>
                    )}
                    <span className="text-caption">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}