'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'react-hot-toast';
import { 
  Share2, 
  Mail, 
  MessageCircle, 
  Send, 
  Twitter, 
  Facebook, 
  Linkedin, 
  Copy, 
  Link,
  Eye,
  Calendar,
  Shield,
  CheckCircle,
  AlertCircle,
  X
} from 'lucide-react';
// Import the ReportData interface from the reports page
interface MLPrediction {
  risk_level: 'low' | 'medium' | 'moderate' | 'high';
  confidence: number;
  next_flare_probability: number;
  predicted_severity: number;
  timeline: string;
  key_factors: string[];
}

interface PersonalizedRecommendations {
  immediate_actions: Array<{
    action: string;
    priority: 'high' | 'medium' | 'low';
    explanation: string;
    expected_benefit: string;
  }>;
  dietary_suggestions: Array<{
    type: 'avoid' | 'include' | 'moderate';
    foods: string[];
    reason: string;
    timeline: string;
  }>;
  lifestyle_changes: Array<{
    category: string;
    suggestion: string;
    difficulty: 'easy' | 'moderate' | 'challenging';
    impact: string;
  }>;
  medical_advice: {
    should_consult_doctor: boolean;
    urgency: 'low' | 'medium' | 'high';
    reasons: string[];
    suggested_specialists: string[];
  };
}

interface ReportData {
  user_summary: {
    name: string;
    tracking_days: number;
    last_updated: string;
    overall_trend: 'improving' | 'stable' | 'declining';
  };
  severity_assessment: {
    current_level: 'low' | 'medium' | 'moderate' | 'high';
    trend: 'improving' | 'stable' | 'worsening';
    score: number;
    description: string;
  };
  ml_predictions: MLPrediction;
  recommendations: PersonalizedRecommendations;
  insights: Array<{
    type: 'positive' | 'warning' | 'info';
    title: string;
    description: string;
    action_required: boolean;
  }>;
  progress_metrics: {
    symptom_control: number;
    quality_of_life: number;
    goal_achievement: number;
    consistency_score: number;
  };
}
import { 
  shareReport, 
  generateShareableLink, 
  copyReportLink, 
  ShareableReport,
  ShareOptions 
} from '@/lib/report-sharing';

interface ShareReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportData: ReportData;
}

export function ShareReportModal({ isOpen, onClose, reportData }: ShareReportModalProps) {
  const [activeTab, setActiveTab] = useState('quick-share');
  const [isSharing, setIsSharing] = useState(false);
  const [shareableLink, setShareableLink] = useState<ShareableReport | null>(null);
  const [emailRecipient, setEmailRecipient] = useState('');
  const [customMessage, setCustomMessage] = useState('');
  const [includePersonalData, setIncludePersonalData] = useState(false);
  const [linkExpiryDays, setLinkExpiryDays] = useState(7);

  const handleQuickShare = async (platform: ShareOptions['platform']) => {
    setIsSharing(true);
    try {
      // Create a simplified report data for sharing
      const shareableData = {
        user_summary: {
          name: reportData.user_summary.name,
          ibs_type: 'Mixed IBS', // Default value
          diagnosis_date: '2024-01-01', // Default value
          last_updated: reportData.user_summary.last_updated,
          overall_trend: reportData.user_summary.overall_trend,
        },
        severity_assessment: {
          current_score: reportData.severity_assessment.score,
          trend: reportData.severity_assessment.trend,
          risk_level: reportData.severity_assessment.current_level,
        },
        ml_predictions: {
          flareup_risk: reportData.ml_predictions.risk_level === "high" ? 0.8 : reportData.ml_predictions.risk_level === "medium" ? 0.5 : 0.2,
          severity_forecast: [reportData.ml_predictions.predicted_severity],
          confidence_score: reportData.ml_predictions.confidence,
        },
        progress_metrics: reportData.progress_metrics,
      };
      
      const success = await shareReport({
        platform,
        reportData: shareableData,
        recipientEmail: platform === 'email' ? emailRecipient : undefined,
        message: customMessage,
        includePersonalData
      });

      if (success) {
        toast.success(`Report shared successfully via ${platform}!`);
        
        if (platform === 'copy-link') {
          toast.success('Link copied to clipboard!');
        }
      } else {
        throw new Error('Sharing failed');
      }
    } catch (error) {
      toast.error(`Failed to share report via ${platform}. Please try again.`);
    } finally {
      setIsSharing(false);
    }
  };

  const handleGenerateLink = async () => {
    try {
      setIsSharing(true);
      // Create a simplified report data for sharing
      const shareableData = {
        user_summary: {
          name: reportData.user_summary.name,
          ibs_type: 'Mixed IBS', // Default value
          diagnosis_date: '2024-01-01', // Default value
          last_updated: reportData.user_summary.last_updated,
          overall_trend: reportData.user_summary.overall_trend,
        },
        severity_assessment: {
          current_score: reportData.severity_assessment.score,
          trend: reportData.severity_assessment.trend,
          risk_level: reportData.severity_assessment.current_level,
        },
        ml_predictions: {
          flareup_risk: reportData.ml_predictions.risk_level === "high" ? 0.8 : reportData.ml_predictions.risk_level === "medium" ? 0.5 : 0.2,
          severity_forecast: [reportData.ml_predictions.predicted_severity],
          confidence_score: reportData.ml_predictions.confidence,
        },
        progress_metrics: reportData.progress_metrics,
      };
      
      const link = await generateShareableLink(shareableData, {
        expiresInDays: linkExpiryDays,
        isPublic: false,
        includePersonalData
      });
      setShareableLink(link);
      toast.success('Shareable link generated successfully!');
    } catch (error) {
      console.error('Error generating link:', error);
      toast.error('Failed to generate shareable link');
    } finally {
      setIsSharing(false);
    }
  };

  const handleCopyLink = async () => {
    if (shareableLink) {
      try {
        await navigator.clipboard.writeText(shareableLink.shareUrl);
        toast.success('Link copied to clipboard!');
      } catch (error) {
        toast.error('Failed to copy link. Please try again.');
      }
    }
  };

  const socialPlatforms = [
    { 
      id: 'whatsapp' as const, 
      name: 'WhatsApp', 
      icon: MessageCircle, 
      color: 'bg-green-500 hover:bg-green-600',
      description: 'Share with family and friends'
    },
    { 
      id: 'telegram' as const, 
      name: 'Telegram', 
      icon: Send, 
      color: 'bg-blue-500 hover:bg-blue-600',
      description: 'Share via Telegram'
    },
    { 
      id: 'twitter' as const, 
      name: 'Twitter', 
      icon: Twitter, 
      color: 'bg-sky-500 hover:bg-sky-600',
      description: 'Share your progress publicly'
    },
    { 
      id: 'facebook' as const, 
      name: 'Facebook', 
      icon: Facebook, 
      color: 'bg-blue-600 hover:bg-blue-700',
      description: 'Share with your network'
    },
    { 
      id: 'linkedin' as const, 
      name: 'LinkedIn', 
      icon: Linkedin, 
      color: 'bg-blue-700 hover:bg-blue-800',
      description: 'Professional health sharing'
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Share2 className="h-5 w-5" />
              Share Your IBS Wellness Report
            </CardTitle>
            <Button variant="outline" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="quick-share" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="quick-share">Quick Share</TabsTrigger>
              <TabsTrigger value="email">Email</TabsTrigger>
              <TabsTrigger value="link">Generate Link</TabsTrigger>
            </TabsList>

            <TabsContent value="quick-share" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="message">Custom Message (Optional)</Label>
                  <Textarea
                    id="message"
                    placeholder="Add a personal message to share with your report..."
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    className="mt-1"
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="include-personal"
                    checked={includePersonalData}
                    onChange={(e) => setIncludePersonalData(e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="include-personal" className="text-sm">
                    Include personal information
                  </Label>
                  <Badge variant={includePersonalData ? "destructive" : "secondary"}>
                    {includePersonalData ? "Personal" : "Anonymous"}
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {socialPlatforms.map((platform) => (
                    <Button
                      key={platform.id}
                      variant="outline"
                      className={`h-auto p-4 flex flex-col items-center gap-2 ${platform.color} text-white border-0`}
                      onClick={() => handleQuickShare(platform.id)}
                      disabled={isSharing}
                    >
                      <platform.icon className="h-6 w-6" />
                      <div className="text-center">
                        <div className="font-medium">{platform.name}</div>
                        <div className="text-xs opacity-90">{platform.description}</div>
                      </div>
                    </Button>
                  ))}
                </div>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => handleQuickShare('copy-link')}
                  disabled={isSharing}
                >
                  <Copy className="h-4 w-4 mr-2" />
                  Copy Shareable Link
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="email" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="email-recipient">Recipient Email</Label>
                  <Input
                    id="email-recipient"
                    type="email"
                    placeholder="doctor@example.com"
                    value={emailRecipient}
                    onChange={(e) => setEmailRecipient(e.target.value)}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="email-message">Message</Label>
                  <Textarea
                    id="email-message"
                    placeholder="I wanted to share my IBS wellness report with you..."
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    className="mt-1"
                    rows={4}
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="email-include-personal"
                    checked={includePersonalData}
                    onChange={(e) => setIncludePersonalData(e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="email-include-personal" className="text-sm">
                    Include personal information in email
                  </Label>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div className="text-sm text-blue-800">
                      <p className="font-medium">Privacy Notice</p>
                      <p>Your report will be sent securely. Personal data can be excluded for privacy.</p>
                    </div>
                  </div>
                </div>

                <Button
                  className="w-full"
                  onClick={() => handleQuickShare('email')}
                  disabled={isSharing || !emailRecipient}
                >
                  <Mail className="h-4 w-4 mr-2" />
                  {isSharing ? 'Sending...' : 'Send Email'}
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="link" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="expiry-days">Link Expiry (Days)</Label>
                  <Input
                    id="expiry-days"
                    type="number"
                    min="1"
                    max="30"
                    value={linkExpiryDays}
                    onChange={(e) => setLinkExpiryDays(parseInt(e.target.value) || 7)}
                    className="mt-1"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Link will expire after {linkExpiryDays} days for security
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="link-include-personal"
                    checked={includePersonalData}
                    onChange={(e) => setIncludePersonalData(e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="link-include-personal" className="text-sm">
                    Include personal information in shared report
                  </Label>
                </div>

                {!shareableLink ? (
                  <Button
                    className="w-full"
                    onClick={handleGenerateLink}
                    disabled={isSharing}
                  >
                    <Link className="h-4 w-4 mr-2" />
                    {isSharing ? 'Generating...' : 'Generate Shareable Link'}
                  </Button>
                ) : (
                  <div className="space-y-4">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="flex items-start gap-2">
                        <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                        <div className="flex-1">
                          <p className="font-medium text-green-800">Link Generated Successfully!</p>
                          <p className="text-sm text-green-700 mt-1">
                            Your report is ready to share. The link will expire on{' '}
                            {shareableLink.expiresAt.toLocaleDateString()}.
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Shareable Link</Label>
                      <div className="flex gap-2">
                        <Input
                          value={shareableLink.shareUrl}
                          readOnly
                          className="font-mono text-sm"
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleCopyLink}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <Eye className="h-5 w-5 mx-auto mb-1 text-gray-600" />
                        <p className="text-sm font-medium">{shareableLink.accessCount}</p>
                        <p className="text-xs text-gray-500">Views</p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <Calendar className="h-5 w-5 mx-auto mb-1 text-gray-600" />
                        <p className="text-sm font-medium">{linkExpiryDays}</p>
                        <p className="text-xs text-gray-500">Days Left</p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <Shield className="h-5 w-5 mx-auto mb-1 text-gray-600" />
                        <p className="text-sm font-medium">{includePersonalData ? 'Personal' : 'Anonymous'}</p>
                        <p className="text-xs text-gray-500">Privacy</p>
                      </div>
                    </div>

                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={handleGenerateLink}
                      disabled={isSharing}
                    >
                      Generate New Link
                    </Button>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>

          <div className="flex justify-end gap-2 pt-4 border-t mt-6">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}