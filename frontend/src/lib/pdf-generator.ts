import jsPDF from 'jspdf';

export interface SymptomLog {
  symptom_name: string;
  severity: string;
  logged_at: string;
  stress_level?: number;
  sleep_quality?: number;
  potential_triggers?: string;
  notes?: string;
}

export interface ReportData {
  user_summary: {
    name: string;
    ibs_type?: string;
    diagnosis_date?: string;
    last_updated: string;
    overall_trend: string;
    age?: number;
    gender?: string;
    email?: string;
    height_cm?: number;
    weight_kg?: number;
    bmi?: number;
  };
  severity_assessment: {
    current_score?: number;
    trend: string;
    risk_level: string;
    description?: string;
  };
  ml_predictions: {
    flareup_risk: number;
    severity_forecast: number[];
    confidence_score: number;
    key_factors?: string[];
    timeline?: string;
  };
  recommendations?: {
    immediate_actions?: Array<{
      action: string;
      priority: string;
      explanation?: string;
      expected_benefit?: string;
    }>;
    dietary_suggestions?: Array<{
      type: string;
      foods: string[];
      reason: string;
      timeline?: string;
    }>;
    lifestyle_changes?: Array<{
      category: string;
      suggestion: string;
      difficulty: string;
      impact?: string;
    }>;
    medical_advice?: {
      should_consult_doctor: boolean;
      urgency: string;
      reasons: string[];
      suggested_specialists: string[];
    };
  };
  progress_metrics: {
    symptom_control?: number;
    quality_of_life?: number;
    goal_achievement?: number;
    consistency_score?: number;
  };
  symptom_logs?: SymptomLog[];
  symptom_stats?: {
    total_logs: number;
    average_severity: number;
    most_common_symptoms: string[];
    severity_distribution: Record<string, number>;
  };
}

const C = {
  brand:   [37, 99, 235]   as [number,number,number],
  dark:    [17, 24, 39]    as [number,number,number],
  gray:    [107,114,128]   as [number,number,number],
  light:   [248,250,252]   as [number,number,number],
  green:   [22, 163, 74]   as [number,number,number],
  amber:   [217,119,6]     as [number,number,number],
  red:     [220, 38, 38]   as [number,number,number],
  white:   [255,255,255]   as [number,number,number],
  border:  [226,232,240]   as [number,number,number],
  navy:    [15, 23, 42]    as [number,number,number],
  purple:  [124, 58, 237]  as [number,number,number],
};

export class PDFReportGenerator {
  private doc: jsPDF;
  private pH: number = 297;
  private pW: number = 210;
  private y: number = 0;
  private m = 18;
  private lh = 6.5;
  private pg = 1;

  constructor() {
    this.doc = new jsPDF({ unit: 'mm', format: 'a4' });
    this.pH = this.doc.internal.pageSize.height;
    this.pW = this.doc.internal.pageSize.width;
  }

  async generateReport(data: ReportData): Promise<Blob> {
    this.doc = new jsPDF({ unit: 'mm', format: 'a4' });
    this.pH = this.doc.internal.pageSize.height;
    this.pW = this.doc.internal.pageSize.width;
    this.y = 0;
    this.pg = 1;

    this.coverPage(data);
    this.newPage();
    this.patientSection(data);
    this.severitySection(data);
    this.predictionsSection(data);
    this.symptomSummarySection(data);
    this.recommendationsSection(data);
    this.progressSection(data);
    this.recentLogsSection(data);
    this.disclaimerPage();

    return new Blob([this.doc.output('blob')], { type: 'application/pdf' });
  }

  // ── helpers ──────────────────────────────────────────────────────────────

  private rgb(c: [number,number,number]) { return { r: c[0], g: c[1], b: c[2] }; }

  private fill(c: [number,number,number]) {
    this.doc.setFillColor(c[0], c[1], c[2]);
  }

  private stroke(c: [number,number,number]) {
    this.doc.setDrawColor(c[0], c[1], c[2]);
  }

  private textColor(c: [number,number,number]) {
    this.doc.setTextColor(c[0], c[1], c[2]);
  }

  private font(style: 'normal'|'bold'|'italic', size: number) {
    this.doc.setFont('helvetica', style);
    this.doc.setFontSize(size);
  }

  private needSpace(h: number) {
    if (this.y + h > this.pH - 25) this.newPage();
  }

  private newPage() {
    this.doc.addPage();
    this.pg++;
    this.y = this.m;
    this.pageFooter();
  }

  private pageFooter() {
    const fy = this.pH - 10;
    this.fill(C.brand);
    this.doc.rect(0, this.pH - 15, this.pW, 15, 'F');
    this.textColor(C.white);
    this.font('italic', 7);
    this.doc.text('IBS Wellness Companion — Confidential Medical Report', this.m, fy);
    this.font('bold', 8);
    this.doc.text(`Page ${this.pg}`, this.pW - this.m, fy, { align: 'right' });
  }

  private sectionTitle(title: string, icon = '') {
    this.needSpace(20);
    this.fill(C.brand);
    this.doc.rect(this.m, this.y, this.pW - this.m * 2, 9, 'F');
    this.textColor(C.white);
    this.font('bold', 11);
    this.doc.text(`${icon}  ${title}`, this.m + 3, this.y + 6.2);
    this.y += 13;
    this.textColor(C.dark);
  }

  private badge(label: string, color: [number,number,number], x: number, y: number) {
    this.fill(color);
    const w = this.doc.getTextWidth(label) + 6;
    this.doc.roundedRect(x, y - 4, w, 6, 1.5, 1.5, 'F');
    this.textColor(C.white);
    this.font('bold', 7.5);
    this.doc.text(label.toUpperCase(), x + 3, y);
    this.textColor(C.dark);
  }

  private progressBar(x: number, y: number, w: number, value: number, max: number, color: [number,number,number]) {
    this.fill(C.border);
    this.doc.roundedRect(x, y, w, 4, 1, 1, 'F');
    const fillW = Math.max(0, Math.min((value / max) * w, w));
    this.fill(color);
    this.doc.roundedRect(x, y, fillW, 4, 1, 1, 'F');
  }

  private infoRow(label: string, value: string, x: number, indent = 0) {
    this.font('bold', 9);
    this.textColor(C.gray);
    this.doc.text(label + ':', x + indent, this.y);
    this.font('normal', 9);
    this.textColor(C.dark);
    this.doc.text(value, x + indent + 38, this.y);
    this.y += this.lh;
  }

  private divider() {
    this.stroke(C.border);
    this.doc.setLineWidth(0.3);
    this.doc.line(this.m, this.y, this.pW - this.m, this.y);
    this.y += 4;
  }

  private wrapText(text: string, maxW: number): string[] {
    return this.doc.splitTextToSize(text, maxW);
  }

  // ── COVER PAGE ───────────────────────────────────────────────────────────

  private coverPage(data: ReportData) {
    // Navy header band
    this.fill(C.navy);
    this.doc.rect(0, 0, this.pW, 80, 'F');

    // Brand accent strip
    this.fill(C.brand);
    this.doc.rect(0, 80, this.pW, 4, 'F');

    // App name
    this.textColor(C.white);
    this.font('bold', 22);
    this.doc.text('IBS Wellness Companion', this.pW / 2, 30, { align: 'center' });

    this.font('normal', 11);
    this.textColor([180, 200, 240] as [number,number,number]);
    this.doc.text('AI-Powered Gut Health Management Platform', this.pW / 2, 40, { align: 'center' });

    // Report title box
    this.fill(C.brand);
    this.doc.roundedRect(30, 52, this.pW - 60, 20, 3, 3, 'F');
    this.textColor(C.white);
    this.font('bold', 14);
    this.doc.text('PERSONALIZED IBS HEALTH REPORT', this.pW / 2, 64, { align: 'center' });

    // Patient card
    this.fill(C.white);
    this.doc.roundedRect(this.m, 95, this.pW - this.m * 2, 70, 4, 4, 'F');
    this.stroke(C.border);
    this.doc.setLineWidth(0.4);
    this.doc.roundedRect(this.m, 95, this.pW - this.m * 2, 70, 4, 4, 'S');

    this.textColor(C.brand);
    this.font('bold', 10);
    this.doc.text('PATIENT INFORMATION', this.m + 8, 107);

    this.textColor(C.dark);
    this.font('bold', 16);
    this.doc.text(data.user_summary.name || 'Patient', this.m + 8, 118);

    this.font('normal', 9);
    this.textColor(C.gray);
    const details: string[] = [];
    if (data.user_summary.age) details.push(`Age: ${data.user_summary.age}`);
    if (data.user_summary.gender) details.push(`Gender: ${data.user_summary.gender}`);
    if (data.user_summary.ibs_type) details.push(`IBS Type: ${data.user_summary.ibs_type}`);
    this.doc.text(details.join('   |   '), this.m + 8, 125);

    // IBS type badge
    if (data.user_summary.ibs_type) {
      this.badge(data.user_summary.ibs_type, C.brand, this.pW - 60, 120);
    }

    // Divider inside card
    this.stroke(C.border);
    this.doc.setLineWidth(0.3);
    this.doc.line(this.m + 8, 130, this.pW - this.m - 8, 130);

    // Report meta
    this.font('normal', 8.5);
    this.textColor(C.gray);
    this.doc.text(`Report Date: ${new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })}`, this.m + 8, 138);
    this.doc.text(`Tracking Period: Last 30 days`, this.m + 8, 145);
    if (data.user_summary.diagnosis_date && data.user_summary.diagnosis_date !== '2023-01-01') {
      this.doc.text(`Diagnosis Date: ${new Date(data.user_summary.diagnosis_date).toLocaleDateString('en-IN')}`, this.m + 8, 152);
    }

    // Trend badge
    const trend = data.user_summary.overall_trend;
    const trendColor = trend === 'improving' ? C.green : trend === 'declining' ? C.red : C.amber;
    this.badge(`Trend: ${trend}`, trendColor, this.m + 8, 163);

    // Summary boxes
    const metrics = [
      { label: 'Flare Risk', value: `${Math.round(data.ml_predictions.flareup_risk * 100)}%`, color: data.ml_predictions.flareup_risk > 0.6 ? C.red : data.ml_predictions.flareup_risk > 0.35 ? C.amber : C.green },
      { label: 'AI Confidence', value: `${Math.round(data.ml_predictions.confidence_score * 100)}%`, color: C.brand },
      { label: 'Symptom Control', value: `${data.progress_metrics.symptom_control ?? 0}%`, color: C.green },
      { label: 'Risk Level', value: data.severity_assessment.risk_level?.toUpperCase() ?? 'N/A', color: C.purple },
    ];

    const bx = this.m;
    const bw = (this.pW - this.m * 2 - 12) / 4;
    metrics.forEach((m, i) => {
      const mx = bx + i * (bw + 4);
      const my = 180;
      this.fill(m.color);
      this.doc.roundedRect(mx, my, bw, 28, 3, 3, 'F');
      this.textColor(C.white);
      this.font('bold', 13);
      this.doc.text(m.value, mx + bw / 2, my + 13, { align: 'center' });
      this.font('normal', 7);
      this.doc.text(m.label, mx + bw / 2, my + 22, { align: 'center' });
    });

    // Confidentiality notice
    this.fill([254, 243, 199] as [number,number,number]);
    this.doc.roundedRect(this.m, 218, this.pW - this.m * 2, 14, 2, 2, 'F');
    this.textColor(C.amber);
    this.font('bold', 8);
    this.doc.text('CONFIDENTIAL MEDICAL DOCUMENT', this.pW / 2, 224, { align: 'center' });
    this.textColor(C.dark);
    this.font('normal', 7.5);
    this.doc.text('This report contains personal health information. Please share only with authorized healthcare providers.', this.pW / 2, 230, { align: 'center' });

    // Footer
    this.fill(C.navy);
    this.doc.rect(0, this.pH - 18, this.pW, 18, 'F');
    this.textColor([160, 180, 220] as [number,number,number]);
    this.font('italic', 7.5);
    this.doc.text('Generated by IBS Wellness Companion AI — For medical consultation purposes', this.pW / 2, this.pH - 8, { align: 'center' });
  }
  // ── PATIENT INFO ─────────────────────────────────────────────────────────

  private patientSection(data: ReportData) {
    this.sectionTitle('Patient Information', '👤');

    const half = (this.pW - this.m * 2 - 8) / 2;

    // Left card
    this.fill(C.light);
    this.doc.roundedRect(this.m, this.y, half, 42, 3, 3, 'F');

    const ly = this.y + 8;
    this.y = ly;
    this.infoRow('Full Name', data.user_summary.name || 'N/A', this.m + 4);
    if (data.user_summary.email) this.infoRow('Email', data.user_summary.email, this.m + 4);
    if (data.user_summary.age) this.infoRow('Age', `${data.user_summary.age} years`, this.m + 4);
    if (data.user_summary.gender) this.infoRow('Gender', data.user_summary.gender, this.m + 4);

    // Right card
    const rx = this.m + half + 8;
    this.fill(C.light);
    this.y = ly;
    this.doc.roundedRect(rx, this.y - 8, half, 42, 3, 3, 'F');

    if (data.user_summary.height_cm) this.infoRow('Height', `${data.user_summary.height_cm} cm`, rx + 4);
    if (data.user_summary.weight_kg) this.infoRow('Weight', `${data.user_summary.weight_kg} kg`, rx + 4);
    if (data.user_summary.bmi) this.infoRow('BMI', data.user_summary.bmi.toFixed(1), rx + 4);
    if (data.user_summary.ibs_type) this.infoRow('IBS Type', data.user_summary.ibs_type, rx + 4);
    if (data.user_summary.diagnosis_date && data.user_summary.diagnosis_date !== '2023-01-01') {
      this.infoRow('Diagnosed', new Date(data.user_summary.diagnosis_date).toLocaleDateString('en-IN'), rx + 4);
    }

    this.y = ly + 36;
    this.y += 8;
  }

  // ── SEVERITY ─────────────────────────────────────────────────────────────

  private severitySection(data: ReportData) {
    this.needSpace(55);
    this.sectionTitle('IBS Severity Assessment', '📊');

    const sa = data.severity_assessment;
    const score = sa.current_score ?? 5;
    const rl = sa.risk_level ?? 'medium';
    const color = rl === 'low' ? C.green : rl === 'high' ? C.red : C.amber;

    // Score circle area
    this.fill(C.light);
    this.doc.roundedRect(this.m, this.y, 55, 40, 3, 3, 'F');
    this.textColor(color);
    this.font('bold', 26);
    this.doc.text(`${score.toFixed(1)}`, this.m + 27.5, this.y + 19, { align: 'center' });
    this.font('normal', 8);
    this.textColor(C.gray);
    this.doc.text('/ 10', this.m + 27.5, this.y + 27, { align: 'center' });
    this.font('bold', 9);
    this.textColor(color);
    this.doc.text(rl.toUpperCase() + ' SEVERITY', this.m + 27.5, this.y + 35, { align: 'center' });

    // Progress bar
    this.progressBar(this.m + 5, this.y + 38, 45, score, 10, color);

    // Description
    const descX = this.m + 60;
    const descW = this.pW - this.m - descX;
    this.textColor(C.gray);
    this.font('bold', 9);
    this.doc.text(`Trend: ${sa.trend?.toUpperCase() ?? 'STABLE'}`, descX, this.y + 8);
    this.font('normal', 8.5);
    this.textColor(C.dark);
    if (sa.description) {
      const lines = this.wrapText(sa.description, descW);
      lines.forEach((line, i) => {
        this.doc.text(line, descX, this.y + 18 + i * 5.5);
      });
    }

    this.y += 50;
    this.divider();
  }

  // ── ML PREDICTIONS ───────────────────────────────────────────────────────

  private predictionsSection(data: ReportData) {
    this.needSpace(60);
    this.sectionTitle('AI-Powered Flare-Up Predictions', '🤖');

    const ml = data.ml_predictions;
    const flareColor = ml.flareup_risk > 0.6 ? C.red : ml.flareup_risk > 0.35 ? C.amber : C.green;
    const confColor = ml.confidence_score > 0.75 ? C.green : ml.confidence_score > 0.5 ? C.amber : C.red;

    const bw = (this.pW - this.m * 2 - 8) / 3;

    // 3 metric cards
    [
      { label: 'Flare-Up Risk', value: `${Math.round(ml.flareup_risk * 100)}%`, sub: ml.timeline ?? 'Next 7 days', color: flareColor, bar: ml.flareup_risk * 100 },
      { label: 'AI Confidence', value: `${Math.round(ml.confidence_score * 100)}%`, sub: 'Prediction accuracy', color: confColor, bar: ml.confidence_score * 100 },
      { label: 'Predicted Severity', value: `${(ml.severity_forecast[0] ?? 5).toFixed(1)}/10`, sub: 'If flare occurs', color: C.purple, bar: (ml.severity_forecast[0] ?? 5) * 10 },
    ].forEach((item, i) => {
      const x = this.m + i * (bw + 4);
      this.fill(C.light);
      this.doc.roundedRect(x, this.y, bw, 34, 3, 3, 'F');

      this.textColor(item.color);
      this.font('bold', 18);
      this.doc.text(item.value, x + bw / 2, this.y + 14, { align: 'center' });

      this.font('bold', 8);
      this.textColor(C.dark);
      this.doc.text(item.label, x + bw / 2, this.y + 22, { align: 'center' });

      this.font('normal', 7);
      this.textColor(C.gray);
      this.doc.text(item.sub, x + bw / 2, this.y + 28, { align: 'center' });

      this.progressBar(x + 4, this.y + 31, bw - 8, item.bar, 100, item.color);
    });

    this.y += 40;

    // Key factors
    if (ml.key_factors && ml.key_factors.length > 0) {
      this.needSpace(20);
      this.font('bold', 9);
      this.textColor(C.dark);
      this.doc.text('Key Contributing Factors:', this.m, this.y);
      this.y += 6;

      let fx = this.m;
      ml.key_factors.forEach(factor => {
        const fw = this.doc.getTextWidth(factor) + 10;
        if (fx + fw > this.pW - this.m) { fx = this.m; this.y += 8; }
        this.fill([219, 234, 254] as [number,number,number]);
        this.doc.roundedRect(fx, this.y - 4, fw, 6, 1.5, 1.5, 'F');
        this.textColor(C.brand);
        this.font('normal', 8);
        this.doc.text(factor, fx + 5, this.y);
        fx += fw + 4;
      });
      this.y += 10;
    }

    this.divider();
  }

  // ── SYMPTOM SUMMARY ──────────────────────────────────────────────────────

  private symptomSummarySection(data: ReportData) {
    if (!data.symptom_stats) return;
    this.needSpace(55);
    this.sectionTitle('Symptom Statistics Summary', '📈');

    const ss = data.symptom_stats;

    // Stats row
    const items = [
      { label: 'Total Logs', value: String(ss.total_logs) },
      { label: 'Avg Severity', value: ss.average_severity.toFixed(2) },
      { label: 'Most Common', value: ss.most_common_symptoms[0] ?? 'N/A' },
    ];

    const bw = (this.pW - this.m * 2 - 8) / 3;
    items.forEach((item, i) => {
      const x = this.m + i * (bw + 4);
      this.fill(C.brand);
      this.doc.roundedRect(x, this.y, bw, 22, 3, 3, 'F');
      this.textColor(C.white);
      this.font('bold', 14);
      this.doc.text(item.value, x + bw / 2, this.y + 12, { align: 'center' });
      this.font('normal', 7.5);
      this.doc.text(item.label, x + bw / 2, this.y + 19, { align: 'center' });
    });
    this.y += 28;

    // Severity distribution
    if (ss.severity_distribution) {
      this.font('bold', 9);
      this.textColor(C.dark);
      this.doc.text('Severity Distribution:', this.m, this.y);
      this.y += 6;

      const total = Object.values(ss.severity_distribution).reduce((a, b) => a + b, 0) || 1;
      const colorMap: Record<string, [number,number,number]> = {
        none: [156,163,175], mild: C.green, moderate: C.amber, severe: C.red, very_severe: [126,34,206]
      };

      Object.entries(ss.severity_distribution).forEach(([sev, count]) => {
        if (!count) return;
        const pct = (count / total) * 100;
        const barW = this.pW - this.m * 2 - 55;
        const col = colorMap[sev] ?? C.gray;

        this.font('normal', 8);
        this.textColor(C.dark);
        this.doc.text(sev.replace('_', ' ').toUpperCase(), this.m, this.y + 3);
        this.progressBar(this.m + 30, this.y, barW, pct, 100, col);
        this.font('bold', 8);
        this.textColor(col);
        this.doc.text(`${count} (${pct.toFixed(0)}%)`, this.m + 30 + barW + 3, this.y + 3);
        this.y += 8;
      });
    }

    this.y += 4;
    this.divider();
  }

  // ── RECOMMENDATIONS ──────────────────────────────────────────────────────

  private recommendationsSection(data: ReportData) {
    if (!data.recommendations) return;
    this.needSpace(30);
    this.sectionTitle('Personalized Recommendations', '💡');

    const rec = data.recommendations;

    // Immediate Actions
    if (rec.immediate_actions && rec.immediate_actions.length > 0) {
      this.font('bold', 10);
      this.textColor(C.brand);
      this.doc.text('Immediate Actions:', this.m, this.y);
      this.y += 6;

      rec.immediate_actions.slice(0, 4).forEach((action, i) => {
        this.needSpace(22);
        const priColor = action.priority === 'high' ? C.red : action.priority === 'medium' ? C.amber : C.green;

        this.fill(C.light);
        this.doc.roundedRect(this.m, this.y, this.pW - this.m * 2, 20, 2, 2, 'F');
        this.stroke(priColor);
        this.doc.setLineWidth(0.6);
        this.doc.line(this.m, this.y, this.m, this.y + 20);

        this.badge(action.priority, priColor, this.pW - this.m - 22, this.y + 6);

        this.font('bold', 9);
        this.textColor(C.dark);
        const titleLines = this.wrapText(action.action, this.pW - this.m * 2 - 30);
        this.doc.text(titleLines[0] ?? action.action, this.m + 4, this.y + 7);

        if (action.expected_benefit) {
          this.font('italic', 7.5);
          this.textColor(C.green);
          const benefitLines = this.wrapText(`→ ${action.expected_benefit}`, this.pW - this.m * 2 - 10);
          this.doc.text(benefitLines[0] ?? '', this.m + 4, this.y + 14);
        }

        this.y += 24;
      });
    }

    // Dietary Suggestions
    if (rec.dietary_suggestions && rec.dietary_suggestions.length > 0) {
      this.needSpace(30);
      this.font('bold', 10);
      this.textColor(C.brand);
      this.doc.text('Dietary Guidance:', this.m, this.y);
      this.y += 6;

      rec.dietary_suggestions.slice(0, 3).forEach(ds => {
        this.needSpace(18);
        const col = ds.type === 'avoid' ? C.red : ds.type === 'include' ? C.green : C.amber;
        this.fill(C.light);
        this.doc.roundedRect(this.m, this.y, this.pW - this.m * 2, 16, 2, 2, 'F');
        this.badge(ds.type.toUpperCase(), col, this.m + 3, this.y + 7);
        this.font('normal', 8);
        this.textColor(C.dark);
        const foods = (ds.foods || []).slice(0, 5).join(', ');
        this.doc.text(foods, this.m + 28, this.y + 7);
        this.font('italic', 7.5);
        this.textColor(C.gray);
        this.doc.text(ds.reason, this.m + 4, this.y + 13);
        this.y += 20;
      });
    }

    // Lifestyle Changes
    if (rec.lifestyle_changes && rec.lifestyle_changes.length > 0) {
      this.needSpace(25);
      this.font('bold', 10);
      this.textColor(C.brand);
      this.doc.text('Lifestyle Changes:', this.m, this.y);
      this.y += 6;

      rec.lifestyle_changes.slice(0, 3).forEach(lc => {
        this.needSpace(16);
        const diffColor = lc.difficulty === 'easy' ? C.green : lc.difficulty === 'challenging' ? C.red : C.amber;
        this.fill(C.light);
        this.doc.roundedRect(this.m, this.y, this.pW - this.m * 2, 14, 2, 2, 'F');
        this.font('bold', 8.5);
        this.textColor(C.dark);
        this.doc.text(`[${lc.category}]`, this.m + 3, this.y + 6);
        this.font('normal', 8.5);
        this.doc.text(lc.suggestion, this.m + 35, this.y + 6);
        this.badge(lc.difficulty, diffColor, this.pW - this.m - 24, this.y + 7);
        if (lc.impact) {
          this.font('italic', 7.5);
          this.textColor(C.green);
          this.doc.text(`Impact: ${lc.impact}`, this.m + 3, this.y + 12);
        }
        this.y += 18;
      });
    }

    // Medical Advice box
    if (rec.medical_advice) {
      this.needSpace(25);
      const ma = rec.medical_advice;
      const maColor = ma.should_consult_doctor ? C.red : C.green;
      this.fill(ma.should_consult_doctor ? [254,242,242] as [number,number,number] : [240,253,244] as [number,number,number]);
      this.stroke(maColor);
      this.doc.setLineWidth(0.4);
      this.doc.roundedRect(this.m, this.y, this.pW - this.m * 2, 22, 3, 3, 'FD');
      this.font('bold', 9.5);
      this.textColor(maColor);
      const maTitle = ma.should_consult_doctor ? '⚠  Medical Consultation Recommended' : '✓  No Immediate Medical Consultation Required';
      this.doc.text(maTitle, this.m + 5, this.y + 8);
      if (ma.suggested_specialists.length > 0) {
        this.font('normal', 8);
        this.textColor(C.dark);
        this.doc.text(`Suggested: ${ma.suggested_specialists.join(', ')}`, this.m + 5, this.y + 16);
      } else if (ma.reasons.length > 0) {
        this.font('normal', 8);
        this.textColor(C.dark);
        this.doc.text(ma.reasons[0], this.m + 5, this.y + 16);
      }
      this.y += 28;
    }

    this.divider();
  }

  // ── PROGRESS METRICS ─────────────────────────────────────────────────────

  private progressSection(data: ReportData) {
    this.needSpace(50);
    this.sectionTitle('Progress Metrics', '⭐');

    const pm = data.progress_metrics;
    const metrics = [
      { label: 'Symptom Control', value: pm.symptom_control ?? 0, color: C.brand },
      { label: 'Quality of Life', value: pm.quality_of_life ?? 0, color: C.green },
      { label: 'Goal Achievement', value: pm.goal_achievement ?? 0, color: C.purple },
      { label: 'Tracking Consistency', value: pm.consistency_score ?? 0, color: C.amber },
    ];

    const bw = (this.pW - this.m * 2 - 12) / 4;

    metrics.forEach((m, i) => {
      const x = this.m + i * (bw + 4);
      const col = m.value >= 80 ? C.green : m.value >= 60 ? C.amber : C.red;
      this.fill(C.light);
      this.doc.roundedRect(x, this.y, bw, 36, 3, 3, 'F');
      this.textColor(col);
      this.font('bold', 20);
      this.doc.text(`${m.value}%`, x + bw / 2, this.y + 17, { align: 'center' });
      this.font('normal', 7);
      this.textColor(C.gray);
      this.doc.text(m.label, x + bw / 2, this.y + 25, { align: 'center' });
      this.progressBar(x + 4, this.y + 30, bw - 8, m.value, 100, col);
    });

    this.y += 44;
    this.divider();
  }

  // ── RECENT LOGS ──────────────────────────────────────────────────────────

  private recentLogsSection(data: ReportData) {
    if (!data.symptom_logs || data.symptom_logs.length === 0) return;
    this.needSpace(40);
    this.sectionTitle('Recent Symptom Log (Last 10 Entries)', '📋');

    const headers = ['Date & Time', 'Symptom', 'Severity', 'Stress', 'Sleep', 'Triggers'];
    const colW = [36, 38, 22, 16, 16, 44];
    let cx = this.m;

    // Table header
    this.fill(C.brand);
    this.doc.rect(this.m, this.y, this.pW - this.m * 2, 8, 'F');
    this.textColor(C.white);
    this.font('bold', 7.5);
    headers.forEach((h, i) => {
      this.doc.text(h, cx + 2, this.y + 5.5);
      cx += (colW[i] ?? 10);
    });
    this.y += 8;

    const sevColor = (sev: string): [number,number,number] => {
      if (sev === 'severe' || sev === 'very_severe') return C.red;
      if (sev === 'moderate') return C.amber;
      return C.green;
    };

    data.symptom_logs.slice(0, 10).forEach((log, idx) => {
      this.needSpace(10);
      if (idx % 2 === 0) {
        this.fill(C.light);
        this.doc.rect(this.m, this.y, this.pW - this.m * 2, 8, 'F');
      }

      cx = this.m;
      const rowData = [
        new Date(log.logged_at).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }),
        log.symptom_name,
        log.severity,
        log.stress_level ? `${log.stress_level}/10` : '-',
        log.sleep_quality ? `${log.sleep_quality}/10` : '-',
        log.potential_triggers ?? log.notes ?? '-',
      ];

      this.font('normal', 7.5);
      rowData.forEach((val, i) => {
        if (i === 2) this.textColor(sevColor(val));
        else this.textColor(C.dark);
        const w = colW[i] ?? 10;
        const truncated = val.length > (w / 2.2) ? val.slice(0, Math.floor(w / 2.2)) + '…' : val;
        this.doc.text(truncated, cx + 2, this.y + 5.5);
        cx += w;
      });

      this.y += 8;
    });

    this.y += 6;
  }

  // ── DISCLAIMER PAGE ──────────────────────────────────────────────────────

  private disclaimerPage() {
    this.newPage();

    this.fill(C.navy);
    this.doc.rect(0, 0, this.pW, 30, 'F');
    this.textColor(C.white);
    this.font('bold', 14);
    this.doc.text('Important Medical Disclaimer', this.pW / 2, 18, { align: 'center' });

    this.y = 40;
    const disclaimers = [
      { title: 'For Informational Purposes Only', body: 'This report is generated by an AI-powered wellness application and is intended solely for informational and educational purposes. It does not constitute medical advice, diagnosis, or treatment.' },
      { title: 'Consult Your Healthcare Provider', body: 'Always seek the advice of your gastroenterologist, general physician, or qualified health provider with any questions regarding a medical condition. Never disregard professional medical advice based on information from this report.' },
      { title: 'AI Limitations', body: 'The predictions and recommendations in this report are generated using machine learning algorithms trained on general IBS data. Individual responses to treatments and triggers vary significantly.' },
      { title: 'Emergency Situations', body: 'If you are experiencing severe abdominal pain, blood in stool, significant weight loss, or any other alarming symptoms, please seek immediate medical attention or go to the nearest emergency room.' },
      { title: 'Data Privacy', body: 'This report contains personal health information. It is your responsibility to ensure it is shared only with authorized healthcare professionals and kept in a secure location.' },
    ];

    disclaimers.forEach(d => {
      this.needSpace(28);
      this.fill(C.light);
      const lines = this.wrapText(d.body, this.pW - this.m * 2 - 10);
      const boxH = 14 + lines.length * 5.5;
      this.doc.roundedRect(this.m, this.y, this.pW - this.m * 2, boxH, 3, 3, 'F');
      this.font('bold', 9);
      this.textColor(C.brand);
      this.doc.text(d.title, this.m + 5, this.y + 8);
      this.font('normal', 8);
      this.textColor(C.dark);
      lines.forEach((line, i) => {
        this.doc.text(line, this.m + 5, this.y + 15 + i * 5.5);
      });
      this.y += boxH + 6;
    });

    // Signature area
    this.needSpace(40);
    this.y += 10;
    this.stroke(C.border);
    this.doc.setLineWidth(0.3);
    this.doc.line(this.m, this.y, this.m + 70, this.y);
    this.doc.line(this.pW - this.m - 70, this.y, this.pW - this.m, this.y);
    this.font('normal', 8);
    this.textColor(C.gray);
    this.doc.text('Patient Signature', this.m, this.y + 5);
    this.doc.text("Doctor's Signature", this.pW - this.m - 70, this.y + 5);
    this.y += 15;
    this.doc.text(`Report generated on: ${new Date().toLocaleString('en-IN')}`, this.m, this.y);
  }
}

// ── EXPORTS ───────────────────────────────────────────────────────────────

export const downloadPDFReport = async (reportData: ReportData, filename?: string): Promise<void> => {
  const generator = new PDFReportGenerator();
  const blob = await generator.generateReport(reportData);
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename ?? `ibs-report-${new Date().toISOString().split('T')[0]}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const generatePDFBlob = async (reportData: ReportData): Promise<Blob> => {
  const generator = new PDFReportGenerator();
  return generator.generateReport(reportData);
};
