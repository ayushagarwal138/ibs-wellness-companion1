'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { SeverityIndicator } from '@/components/ui/severity-indicator';
import { 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  Calendar,
  Heart,
  Utensils,
  Activity,
  Brain,
  Clock,
  TrendingUp,
  FileText,
  Download
} from 'lucide-react';

interface AssessmentResult {
  risk_assessment: {
    overall_risk_score: number;
    risk_level: 'low' | 'moderate' | 'high' | 'severe';
    confidence_score: number;
    severity_classification: string;
    primary_risk_factors: string[];
    clinical_flags: string[];
  };
  recommendations: {
    dietary: Array<{
      category: string;
      recommendation: string;
      priority: 'high' | 'medium' | 'low';
      evidence_level: string;
    }>;
    lifestyle: Array<{
      category: string;
      recommendation: string;
      priority: 'high' | 'medium' | 'low';
      evidence_level: string;
    }>;
    medical: Array<{
      category: string;
      recommendation: string;
      priority: 'high' | 'medium' | 'low';
      evidence_level: string;
    }>;
  };
  next_assessment_date: string;
  flareup_probability: {
    next_week: number;
    next_month: number;
    next_3_months: number;
  };
}

interface IBSAssessmentResultsProps {
  result: AssessmentResult;
  onNewAssessment: () => void;
}

const getRiskColor = (level: string) => {
  switch (level) {
    case 'low': return 'bg-green-100 text-green-800 border-green-200';
    case 'moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'severe': return 'bg-red-100 text-red-800 border-red-200';
    default: return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getRiskIcon = (level: string) => {
  switch (level) {
    case 'low': return <CheckCircle className="h-5 w-5 text-green-600" />;
    case 'moderate': return <Info className="h-5 w-5 text-yellow-600" />;
    case 'high': return <AlertTriangle className="h-5 w-5 text-orange-600" />;
    case 'severe': return <AlertTriangle className="h-5 w-5 text-red-600" />;
    default: return <Info className="h-5 w-5 text-gray-600" />;
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return 'bg-red-100 text-red-800';
    case 'medium': return 'bg-yellow-100 text-yellow-800';
    case 'low': return 'bg-green-100 text-green-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

export default function IBSAssessmentResults({ result, onNewAssessment }: IBSAssessmentResultsProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const downloadReport = () => {
    // Implementation for downloading PDF report
    console.log('Downloading assessment report...');
  };

  return (
    <div className="space-y-6">
      {/* Risk Assessment Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getRiskIcon(result.risk_assessment.risk_level)}
            IBS Risk Assessment Results
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Overall Risk Level</h3>
              <p className="text-sm text-gray-600">
                Severity: {result.risk_assessment.severity_classification}
              </p>
            </div>
            <Badge className={`${getRiskColor(result.risk_assessment.risk_level)} text-lg px-4 py-2`}>
              {result.risk_assessment.risk_level.toUpperCase()}
            </Badge>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Risk Score</span>
              <span>{result.risk_assessment.overall_risk_score}/100</span>
            </div>
            <Progress value={result.risk_assessment.overall_risk_score} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Confidence Level</span>
              <span>{result.risk_assessment.confidence_score}%</span>
            </div>
            <Progress value={result.risk_assessment.confidence_score} className="h-2" />
          </div>

          {result.risk_assessment.clinical_flags.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="font-semibold text-red-800 flex items-center gap-2 mb-2">
                <AlertTriangle className="h-4 w-4" />
                Clinical Attention Required
              </h4>
              <ul className="text-sm text-red-700 space-y-1">
                {result.risk_assessment.clinical_flags.map((flag, index) => (
                  <li key={index}>• {flag}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Flare-up Probability */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Flare-up Probability
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {result.flareup_probability.next_week}%
              </div>
              <div className="text-sm text-gray-600">Next Week</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {result.flareup_probability.next_month}%
              </div>
              <div className="text-sm text-gray-600">Next Month</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {result.flareup_probability.next_3_months}%
              </div>
              <div className="text-sm text-gray-600">3 Months</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Primary Risk Factors */}
      <Card>
        <CardHeader>
          <CardTitle>Primary Risk Factors</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {result.risk_assessment.primary_risk_factors.map((factor, index) => (
              <Badge key={index} variant="outline" className="text-sm">
                {factor}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dietary Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            Dietary Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {result.recommendations.dietary.map((rec, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-semibold">{rec.category}</h4>
                  <Badge className={`${getPriorityColor(rec.priority)} text-xs mt-1`}>
                    {rec.priority} priority
                  </Badge>
                </div>
                <Badge variant="outline" className="text-xs">
                  {rec.evidence_level}
                </Badge>
              </div>
              <p className="text-sm text-gray-700">{rec.recommendation}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Lifestyle Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Lifestyle Modifications
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {result.recommendations.lifestyle.map((rec, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-semibold">{rec.category}</h4>
                  <Badge className={`${getPriorityColor(rec.priority)} text-xs mt-1`}>
                    {rec.priority} priority
                  </Badge>
                </div>
                <Badge variant="outline" className="text-xs">
                  {rec.evidence_level}
                </Badge>
              </div>
              <p className="text-sm text-gray-700">{rec.recommendation}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Medical Recommendations */}
      {result.recommendations.medical.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5" />
              Medical Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {result.recommendations.medical.map((rec, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-semibold">{rec.category}</h4>
                    <Badge className={`${getPriorityColor(rec.priority)} text-xs mt-1`}>
                      {rec.priority} priority
                    </Badge>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {rec.evidence_level}
                  </Badge>
                </div>
                <p className="text-sm text-gray-700">{rec.recommendation}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Next Assessment */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Follow-up Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Recommended next assessment:</p>
              <p className="font-semibold">{formatDate(result.next_assessment_date)}</p>
            </div>
            <Clock className="h-8 w-8 text-gray-400" />
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <Button onClick={downloadReport} variant="outline" className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Download Report
        </Button>
        <Button onClick={onNewAssessment} className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          New Assessment
        </Button>
      </div>
    </div>
  );
}