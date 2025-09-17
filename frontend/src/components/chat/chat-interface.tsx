'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertCircle, TrendingUp, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

// Types for chat functionality
interface ChatMessage {
  id: string;
  content: string;
  message_type: 'user' | 'assistant' | 'system';
  timestamp: string;
  metadata?: {
    ibs_assessment?: {
      severity: string;
      confidence_score: number;
      symptoms_score: number;
      frequency_score: number;
      impact_score: number;
      factors: string[];
    };
    recommendations?: Array<{
      title: string;
      description: string;
      type: string;
      priority: number;
    }>;
    flareup_prediction?: {
      risk_score: number;
      risk_level: string;
      confidence: number;
      factors: string[];
      days_ahead: number;
    };
  };
}

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ChatInterfaceProps {
  className?: string;
}

export default function ChatInterface({ className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat session on component mount
  useEffect(() => {
    initializeChat();
  }, []);

  const initializeChat = async () => {
    try {
      // Create a new chat session
      const response = await fetch('/api/v1/chat/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          title: `Chat Session - ${new Date().toLocaleDateString()}`
        }),
      });

      if (response.ok) {
        const session = await response.json();
        setCurrentSession(session);
        
        // Add welcome message
        const welcomeMessage: ChatMessage = {
          id: 'welcome-' + Date.now(),
          content: "Hello! I'm your IBS wellness assistant. I can help you understand your symptoms, provide personalized recommendations, and predict potential flare-ups. How are you feeling today?",
          message_type: 'assistant',
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMessage]);
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading || !currentSession) return;

    const userMessage: ChatMessage = {
      id: 'user-' + Date.now(),
      content: currentMessage,
      message_type: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`/api/v1/chat/sessions/${currentSession.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          content: currentMessage,
          include_assessment: true,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage: ChatMessage = {
          id: 'assistant-' + Date.now(),
          content: data.message,
          message_type: 'assistant',
          timestamp: new Date().toISOString(),
          metadata: {
            ibs_assessment: data.ibs_assessment,
            recommendations: data.recommendations,
            flareup_prediction: data.flareup_prediction,
          },
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: 'error-' + Date.now(),
        content: "I'm sorry, I'm having trouble responding right now. Please try again in a moment.",
        message_type: 'system',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessageContent = (message: ChatMessage) => {
    return (
      <div className="space-y-3">
        <p className="text-sm leading-relaxed">{message.content}</p>
        
        {/* Render IBS Assessment */}
        {message.metadata?.ibs_assessment && (
          <Card className="bg-blue-50 border-blue-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                IBS Assessment
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="font-medium">Severity:</span> 
                  <span className={cn(
                    "ml-1 px-2 py-1 rounded text-xs font-medium",
                    message.metadata.ibs_assessment.severity === 'mild' && "bg-green-100 text-green-800",
                    message.metadata.ibs_assessment.severity === 'moderate' && "bg-yellow-100 text-yellow-800",
                    message.metadata.ibs_assessment.severity === 'severe' && "bg-red-100 text-red-800"
                  )}>
                    {message.metadata.ibs_assessment.severity}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Confidence:</span> 
                  <span className="ml-1">{(message.metadata.ibs_assessment.confidence_score * 100).toFixed(0)}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Render Flare-up Prediction */}
        {message.metadata?.flareup_prediction && message.metadata.flareup_prediction.risk_level !== 'low' && (
          <Card className="bg-orange-50 border-orange-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Flare-up Risk Prediction
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span>Risk Level:</span>
                  <span className={cn(
                    "px-2 py-1 rounded font-medium",
                    message.metadata.flareup_prediction.risk_level === 'moderate' && "bg-yellow-100 text-yellow-800",
                    message.metadata.flareup_prediction.risk_level === 'high' && "bg-red-100 text-red-800"
                  )}>
                    {message.metadata.flareup_prediction.risk_level} ({(message.metadata.flareup_prediction.risk_score * 100).toFixed(0)}%)
                  </span>
                </div>
                <div className="flex items-center gap-1 text-xs">
                  <Calendar className="h-3 w-3" />
                  <span>Next {message.metadata.flareup_prediction.days_ahead} days</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Render Recommendations */}
        {message.metadata?.recommendations && message.metadata.recommendations.length > 0 && (
          <Card className="bg-green-50 border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Personalized Recommendations</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                {message.metadata.recommendations.slice(0, 3).map((rec, index) => (
                  <div key={index} className="text-xs">
                    <div className="font-medium">{rec.title}</div>
                    <div className="text-gray-600">{rec.description}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
    <Card className={cn("flex flex-col h-[600px]", className)}>
      <CardHeader className="border-b">
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-blue-600" />
          IBS Wellness Assistant
          {currentSession && (
            <span className="text-sm font-normal text-gray-500">
              • {messages.filter(m => m.message_type !== 'system').length} messages
            </span>
          )}
        </CardTitle>
      </CardHeader>

      {/* Messages Area */}
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-3",
              message.message_type === 'user' && "flex-row-reverse"
            )}
          >
            {/* Avatar */}
            <div className={cn(
              "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
              message.message_type === 'user' 
                ? "bg-blue-600 text-white" 
                : message.message_type === 'assistant'
                ? "bg-green-600 text-white"
                : "bg-gray-400 text-white"
            )}>
              {message.message_type === 'user' ? (
                <User className="h-4 w-4" />
              ) : message.message_type === 'assistant' ? (
                <Bot className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
            </div>

            {/* Message Content */}
            <div className={cn(
              "flex-1 max-w-[80%]",
              message.message_type === 'user' && "flex flex-col items-end"
            )}>
              <div className={cn(
                "rounded-lg px-4 py-2",
                message.message_type === 'user' 
                  ? "bg-blue-600 text-white" 
                  : message.message_type === 'assistant'
                  ? "bg-gray-100 text-gray-900"
                  : "bg-yellow-100 text-yellow-800"
              )}>
                {message.message_type === 'user' ? (
                  <p className="text-sm">{message.content}</p>
                ) : (
                  renderMessageContent(message)
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {formatTimestamp(message.timestamp)}
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex-1">
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </CardContent>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your IBS symptoms, get recommendations, or request an assessment..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            onClick={sendMessage}
            disabled={!currentMessage.trim() || isLoading}
            size="sm"
            className="px-3"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <div className="text-xs text-gray-500 mt-2">
          Press Enter to send • Try asking: "How are my symptoms?" or "Give me recommendations"
        </div>
      </div>
    </Card>
  );
}