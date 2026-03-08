/**
 * PDF Generation Service for IBS Analytics Reports
 * Generates personalized PDF reports with Indian diet recommendations
 */

import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export interface ReportData {
  user_summary: {
    name: string;
    ibs_type: string;
    diagnosis_date: string;
    last_updated: string;
    overall_trend: string;
  };
  severity_assessment: {
    current_score?: number;
    trend: string;
    risk_level: string;
  };
  ml_predictions: {
    flareup_risk: number;
    severity_forecast: number[];
    confidence_score: number;
  };
  indian_recommendations?: {
    recommended_dishes: Array<{
      dish_name: string;
      region: string;
      ibs_friendly_score: number;
      spice_level: number;
    }>;
    beneficial_spices: Array<{
      spice_name: string;
      digestive_benefit: string;
      recommended_amount: string;
    }>;
    lifestyle_tips: string[];
    personalization_score: number;
  };
  progress_metrics: {
    symptom_control?: number;
    quality_of_life?: number;
    goal_achievement?: number;
    consistency_score?: number;
  };
}

export class PDFReportGenerator {
  private doc: jsPDF;
  private pageHeight: number;
  private pageWidth: number;
  private currentY: number;
  private margin: number;
  private lineHeight: number;

  constructor() {
    this.doc = new jsPDF();
    this.pageHeight = this.doc.internal.pageSize.height;
    this.pageWidth = this.doc.internal.pageSize.width;
    this.currentY = 20;
    this.margin = 20;
    this.lineHeight = 7;
  }

  async generateReport(reportData: ReportData): Promise<Blob> {
    try {
      // Reset document
      this.doc = new jsPDF();
      this.currentY = 20;

      // Generate report sections
      this.addHeader(reportData.user_summary);
      this.addSeverityAssessment(reportData.severity_assessment);
      this.addMLPredictions(reportData.ml_predictions);
      
      if (reportData.indian_recommendations) {
        this.addIndianRecommendations(reportData.indian_recommendations);
      }
      
      this.addProgressMetrics(reportData.progress_metrics);
      this.addFooter();

      // Return PDF as blob
      return new Blob([this.doc.output('blob')], { type: 'application/pdf' });
    } catch (error) {
      console.error('Error generating PDF report:', error);
      throw new Error('Failed to generate PDF report');
    }
  }

  private addHeader(userSummary: ReportData['user_summary']): void {
    // Title
    this.doc.setFontSize(24);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('IBS Wellness Report', this.margin, this.currentY);
    this.currentY += 15;

    // Subtitle with personalization
    this.doc.setFontSize(16);
    this.doc.setFont('helvetica', 'normal');
    this.doc.text('Personalized Indian Diet & Lifestyle Recommendations', this.margin, this.currentY);
    this.currentY += 15;

    // User info
    this.doc.setFontSize(12);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Patient Information:', this.margin, this.currentY);
    this.currentY += this.lineHeight;

    this.doc.setFont('helvetica', 'normal');
    this.doc.text(`Name: ${userSummary.name}`, this.margin + 5, this.currentY);
    this.currentY += this.lineHeight;
    this.doc.text(`IBS Type: ${userSummary.ibs_type}`, this.margin + 5, this.currentY);
    this.currentY += this.lineHeight;
    this.doc.text(`Diagnosis Date: ${userSummary.diagnosis_date}`, this.margin + 5, this.currentY);
    this.currentY += this.lineHeight;
    this.doc.text(`Report Generated: ${new Date().toLocaleDateString()}`, this.margin + 5, this.currentY);
    this.currentY += this.lineHeight;
    this.doc.text(`Overall Trend: ${userSummary.overall_trend}`, this.margin + 5, this.currentY);
    this.currentY += 15;

    // Add separator line
    this.doc.setDrawColor(200, 200, 200);
    this.doc.line(this.margin, this.currentY, this.pageWidth - this.margin, this.currentY);
    this.currentY += 10;
  }

  private addSeverityAssessment(severityData: ReportData['severity_assessment']): void {
    this.checkPageBreak(40);

    this.doc.setFontSize(16);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Current Severity Assessment', this.margin, this.currentY);
    this.currentY += 10;

    // Current score with visual indicator
    this.doc.setFontSize(12);
    this.doc.setFont('helvetica', 'normal');
    const currentScore = severityData.current_score || 0;
    this.doc.text(`Current Severity Score: ${currentScore}/10`, this.margin, this.currentY);
    
    // Add severity bar
    const barWidth = 100;
    const barHeight = 8;
    const barX = this.margin + 120;
    const barY = this.currentY - 4;
    
    // Background bar
    this.doc.setFillColor(240, 240, 240);
    this.doc.rect(barX, barY, barWidth, barHeight, 'F');
    
    // Severity bar
    const severityWidth = (currentScore / 10) * barWidth;
    const color: [number, number, number] = currentScore <= 3 ? [76, 175, 80] : 
                  currentScore <= 6 ? [255, 193, 7] : [244, 67, 54];
    this.doc.setFillColor(color[0], color[1], color[2]);
    this.doc.rect(barX, barY, severityWidth, barHeight, 'F');
    
    this.currentY += 15;

    this.doc.text(`Trend: ${severityData.trend}`, this.margin, this.currentY);
    this.currentY += this.lineHeight;
    this.doc.text(`Risk Level: ${severityData.risk_level}`, this.margin, this.currentY);
    this.currentY += 15;
  }

  private addMLPredictions(mlData: ReportData['ml_predictions']): void {
    this.checkPageBreak(50);

    this.doc.setFontSize(16);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('AI-Powered Predictions', this.margin, this.currentY);
    this.currentY += 10;

    this.doc.setFontSize(12);
    this.doc.setFont('helvetica', 'normal');
    this.doc.text(`Flare-up Risk (Next 7 Days): ${mlData.flareup_risk}%`, this.margin, this.currentY);
    this.currentY += this.lineHeight;
    
    this.doc.text(`Prediction Confidence: ${mlData.confidence_score}%`, this.margin, this.currentY);
    this.currentY += this.lineHeight;

    // Severity forecast
    this.doc.text('7-Day Severity Forecast:', this.margin, this.currentY);
    this.currentY += this.lineHeight;
    
    const forecastText = mlData.severity_forecast.map((score, index) => 
      `Day ${index + 1}: ${score.toFixed(1)}`
    ).join(', ');
    
    this.doc.text(forecastText, this.margin + 5, this.currentY);
    this.currentY += 15;
  }

  private addIndianRecommendations(indianData: ReportData['indian_recommendations']): void {
    if (!indianData) return;
    
    this.checkPageBreak(100);

    this.doc.setFontSize(16);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Personalized Indian Diet Recommendations', this.margin, this.currentY);
    this.currentY += 5;

    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'italic');
    this.doc.text(`Personalization Score: ${indianData.personalization_score.toFixed(1)}%`, this.margin, this.currentY);
    this.currentY += 15;

    // Recommended dishes
    this.doc.setFontSize(14);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Recommended Indian Dishes:', this.margin, this.currentY);
    this.currentY += 8;

    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'normal');
    
    indianData.recommended_dishes.slice(0, 8).forEach((dish, index) => {
      this.checkPageBreak(15);
      const dishText = `${index + 1}. ${dish.dish_name} (${dish.region}) - IBS Score: ${dish.ibs_friendly_score}/10`;
      this.doc.text(dishText, this.margin + 5, this.currentY);
      this.currentY += this.lineHeight;
    });

    this.currentY += 5;

    // Beneficial spices
    this.doc.setFontSize(14);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Beneficial Spices for IBS Management:', this.margin, this.currentY);
    this.currentY += 8;

    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'normal');
    
    indianData.beneficial_spices.slice(0, 6).forEach((spice, index) => {
      this.checkPageBreak(15);
      const spiceText = `${index + 1}. ${spice.spice_name} - ${spice.digestive_benefit} (${spice.recommended_amount})`;
      this.doc.text(spiceText, this.margin + 5, this.currentY);
      this.currentY += this.lineHeight;
    });

    this.currentY += 5;

    // Lifestyle tips
    this.doc.setFontSize(14);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Indian Lifestyle Tips:', this.margin, this.currentY);
    this.currentY += 8;

    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'normal');
    
    indianData.lifestyle_tips.slice(0, 6).forEach((tip, index) => {
      this.checkPageBreak(20);
      const wrappedTip = this.wrapText(tip, this.pageWidth - this.margin * 2 - 10);
      this.doc.text(`${index + 1}. ${wrappedTip}`, this.margin + 5, this.currentY);
      this.currentY += this.lineHeight * Math.ceil(wrappedTip.length / 80); // Approximate line breaks
    });

    this.currentY += 15;
  }

  private addProgressMetrics(progressData: ReportData['progress_metrics']): void {
    this.checkPageBreak(60);

    this.doc.setFontSize(16);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Progress Metrics', this.margin, this.currentY);
    this.currentY += 10;

    const metrics = [
      { label: 'Symptom Control', value: progressData.symptom_control },
      { label: 'Quality of Life', value: progressData.quality_of_life },
      { label: 'Goal Achievement', value: progressData.goal_achievement },
      { label: 'Consistency Score', value: progressData.consistency_score }
    ];

    metrics.forEach(metric => {
      this.doc.setFontSize(12);
      this.doc.setFont('helvetica', 'normal');
      this.doc.text(`${metric.label}: ${metric.value}%`, this.margin, this.currentY);
      
      // Add progress bar
      const barWidth = 80;
      const barHeight = 6;
      const barX = this.margin + 100;
      const barY = this.currentY - 3;
      
      // Background
      this.doc.setFillColor(240, 240, 240);
      this.doc.rect(barX, barY, barWidth, barHeight, 'F');
      
      // Progress
      const safeValue = metric.value || 0;
      const progressWidth = (safeValue / 100) * barWidth;
      const color: [number, number, number] = safeValue >= 80 ? [76, 175, 80] : 
                    safeValue >= 60 ? [255, 193, 7] : [244, 67, 54];
      this.doc.setFillColor(color[0], color[1], color[2]);
      this.doc.rect(barX, barY, progressWidth, barHeight, 'F');
      
      this.currentY += 12;
    });

    this.currentY += 10;
  }

  private addFooter(): void {
    const footerY = this.pageHeight - 30;
    
    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'italic');
    this.doc.text('This report is generated using AI and machine learning based on your personal health data.', 
                  this.margin, footerY);
    this.doc.text('Always consult with healthcare professionals for medical decisions.', 
                  this.margin, footerY + 7);
    this.doc.text('This report is for informational purposes only.', 
                  this.margin, footerY + 14);
    
    // Add page number
    this.doc.setFont('helvetica', 'normal');
    this.doc.text(`Page 1`, this.pageWidth - this.margin - 20, footerY + 14);
  }

  private checkPageBreak(requiredSpace: number): void {
    if (this.currentY + requiredSpace > this.pageHeight - 40) {
      this.doc.addPage();
      this.currentY = 20;
    }
  }

  private wrapText(text: string, maxWidth: number): string {
    // Simple text wrapping - in production, use proper text measurement
    if (text.length <= maxWidth / 2) return text;
    
    const words = text.split(' ');
    let line = '';
    let result = '';
    
    for (const word of words) {
      if ((line + word).length > maxWidth / 2) {
        result += line.trim() + '\n';
        line = word + ' ';
      } else {
        line += word + ' ';
      }
    }
    
    result += line.trim();
    return result;
  }

  // Method to generate PDF from HTML element (alternative approach)
  async generateFromHTML(elementId: string, filename: string = 'ibs-report.pdf'): Promise<void> {
    try {
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error(`Element with ID '${elementId}' not found`);
      }

      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF();
      
      const imgWidth = 210;
      const pageHeight = 295;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;

      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      pdf.save(filename);
    } catch (error) {
      console.error('Error generating PDF from HTML:', error);
      throw new Error('Failed to generate PDF from HTML');
    }
  }
}

// Utility functions for PDF generation
export const downloadPDFReport = async (reportData: ReportData, filename?: string): Promise<void> => {
  try {
    const generator = new PDFReportGenerator();
    const pdfBlob = await generator.generateReport(reportData);
    
    // Create download link
    const url = URL.createObjectURL(pdfBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `ibs-report-${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error downloading PDF report:', error);
    throw error;
  }
};

export const generatePDFBlob = async (reportData: ReportData): Promise<Blob> => {
  const generator = new PDFReportGenerator();
  return await generator.generateReport(reportData);
};