# Hard-Coded Values Analysis: ML-Driven Alternatives

## Overview
This document identifies hard-coded values throughout the IBS Wellness Companion codebase that should be replaced with dynamic, ML-predicted values to improve personalization and accuracy.

## 1. ML Service Thresholds and Scoring

### 1.1 Personalization Service (`frontend/src/services/personalization-service.ts`)
**Current Hard-Coded Values:**
```typescript
ml_thresholds: {
  high_risk_threshold: 0.7,        // Should be user-specific
  medium_risk_threshold: 0.4,      // Should adapt based on user history
  flare_prediction_threshold: 0.6, // Should be personalized
  severity_threshold: 0.5          // Should be dynamic
},
adaptive_settings: {
  confidence_threshold: 0.6,       // Should be ML-optimized
  learning_rate: 0.1,              // Should be adaptive
  personalization_score: 0.5       // Should be calculated dynamically
}
```

**ML Alternative:** These thresholds should be dynamically calculated based on:
- User's historical symptom patterns
- Response to previous recommendations
- Severity tolerance levels
- Prediction accuracy feedback

### 1.2 ML Service (`frontend/src/services/ml-service.ts`)
**Current Hard-Coded Values:**
```typescript
// Medication effectiveness mock data
effectiveness_score: 0.85,
confidence: 0.92,
optimal_dosage: "10mg twice daily",
stress_impact_score: 0.7,
sleep_impact_score: 0.6,
tolerance_score: 0.8,
overall_risk_score: 0.65
```

**ML Alternative:** These should be predicted using:
- Individual medication response history
- Genetic factors (if available)
- Symptom severity patterns
- Side effect tolerance
- Drug interaction analysis

## 2. Dashboard Analytics and Health Metrics

### 2.1 Dashboard Analytics Service (`frontend/src/services/dashboard-analytics-service.ts`)
**Current Hard-Coded Values:**
```typescript
avgWellnessScore: 7.2  // Should be calculated from user data
```

**ML Alternative:** Calculate based on:
- Recent symptom logs
- Medication adherence
- Lifestyle factors
- Sleep quality
- Stress levels

### 2.2 Data Visualization (`frontend/src/components/dashboard/data-visualization.tsx`)
**Current Hard-Coded Values:**
```typescript
// Food reaction patterns
{ food_name: 'Dairy', reaction_count: 15, avg_severity: 7.2 },
{ food_name: 'Gluten', reaction_count: 12, avg_severity: 6.8 },
{ food_name: 'Spicy Food', reaction_count: 8, avg_severity: 5.5 },

// Weekly summary
total_symptoms: Math.floor(Math.random() * 20) + 5,
avg_severity: Math.random() * 5 + 3,
```

**ML Alternative:** Generate from:
- User's actual food logs
- Symptom tracking data
- Personalized trigger analysis
- Temporal pattern recognition

## 3. Recommendation Algorithms and Scoring

### 3.1 Profile Completion Tracker (`frontend/src/components/profile/profile-completion-tracker.tsx`)
**Current Hard-Coded Values:**
```typescript
// Profile section weights
{ name: 'Basic Information', weight: 15 },
{ name: 'Medical History', weight: 25 },
{ name: 'Dietary Preferences', weight: 20 },
{ name: 'Symptom Patterns', weight: 20 },
{ name: 'Lifestyle Factors', weight: 10 },
{ name: 'Goals & Preferences', weight: 10 }
```

**ML Alternative:** Weights should be determined by:
- Impact on prediction accuracy
- User engagement patterns
- Correlation with health outcomes
- Personalized importance scoring

### 3.2 ML Insights Dashboard (`frontend/src/components/ml/ml-insights-dashboard.tsx`)
**Current Hard-Coded Values:**
```typescript
effectiveness_score: 0.85,
pain_level: 6,
abdominal_pain: 6
```

**ML Alternative:** Predict using:
- Real-time symptom data
- Treatment response patterns
- Comparative effectiveness research
- Personalized pain sensitivity models

## 4. Symptom Analysis and Scoring

### 4.1 Trigger Food Analysis (`frontend/src/components/analysis/trigger-food-analysis.tsx`)
**Current Hard-Coded Values:**
```typescript
confidence: 0.8,                    // Should be calculated
correlation_strength: 0.7,          // Should be data-driven
safe_foods: ['Rice', 'Bananas', 'Lean chicken', 'Herbal tea']  // Should be personalized
```

**ML Alternative:** Calculate based on:
- Statistical significance of food-symptom correlations
- Sample size and data quality
- Individual dietary patterns
- Cross-validation accuracy

### 4.2 Stress Correlation (`frontend/src/components/ml/stress-correlation.tsx`)
**Current Hard-Coded Values:**
```typescript
stress_levels: [3, 7, 5, 8, 4, 6, 9, 2, 7, 5],
symptom_severity: [2, 6, 4, 8, 3, 5, 9, 1, 6, 4]
```

**ML Alternative:** Use actual user data:
- Real stress level inputs
- Actual symptom severity logs
- Temporal correlation analysis
- Individual stress response patterns

### 4.3 Severity Thresholds (`frontend/src/components/dashboard/dashboard.tsx`)
**Current Hard-Coded Values:**
```typescript
if (severity <= 3) return 'bg-green-500';    // Low severity
if (severity <= 6) return 'bg-yellow-500';   // Medium severity
// else return 'bg-red-500';                  // High severity
```

**ML Alternative:** Personalized severity categories based on:
- Individual pain tolerance
- Historical severity distributions
- Functional impact assessment
- Comparative severity analysis

## 5. Prediction and Risk Assessment

### 5.1 Prediction Visualizations (`frontend/src/components/ml/prediction-visualizations.tsx`)
**Current Hard-Coded Values:**
```typescript
const baseValue = mlPredictions?.predicted_severity || 3.0;
value: riskFactors.includes('abdominal_pain') ? 35 + Math.random() * 10 : 25 + Math.random() * 15,
{ label: 'Severity Prediction', value: 94.2, color: '#10b981' }
```

**ML Alternative:** Real-time predictions using:
- Current symptom patterns
- Environmental factors
- Medication timing
- Lifestyle variables
- Historical prediction accuracy

### 5.2 Test Data Generator (`frontend/src/components/testing/test-data-generator.tsx`)
**Current Hard-Coded Values:**
```typescript
severity: Math.floor(Math.random() * 10) + 1,
severityPrediction: Math.random() * 10,
flareupRisk: Math.random()
```

**ML Alternative:** Generate realistic test data using:
- Statistical distributions from real user data
- Clinically validated severity patterns
- Realistic correlation structures
- Temporal dependencies

## 6. Form Validation and Scoring

### 6.1 Profile Validation (`frontend/src/hooks/useProfileValidation.ts`)
**Current Hard-Coded Values:**
```typescript
// Scoring weights for profile completeness
totalScore: calculated from fixed weights,
sectionScore: based on static importance values
```

**ML Alternative:** Dynamic scoring based on:
- Predictive importance of each field
- User engagement optimization
- Health outcome correlation
- Personalized priority weighting

## 7. Medication and Treatment Scoring

### 7.1 Medication Form (`frontend/src/components/forms/medication-form.tsx`)
**Current Hard-Coded Values:**
```typescript
effectiveness_rating: static scale,
adherence_rating: fixed scoring system
```

**ML Alternative:** Intelligent rating systems using:
- Comparative effectiveness data
- Individual response patterns
- Side effect profiles
- Adherence prediction models

## Implementation Recommendations

### Phase 1: Core ML Infrastructure
1. **Personalization Engine**: Replace static thresholds with adaptive algorithms
2. **Prediction Models**: Implement real-time severity and flare prediction
3. **Risk Assessment**: Dynamic risk scoring based on individual patterns

### Phase 2: Advanced Analytics
1. **Correlation Analysis**: Real-time stress-symptom correlation calculation
2. **Trigger Detection**: ML-powered food trigger identification
3. **Effectiveness Tracking**: Personalized treatment response modeling

### Phase 3: Intelligent Recommendations
1. **Adaptive Weights**: ML-optimized profile completion importance
2. **Dynamic Thresholds**: User-specific severity categorization
3. **Predictive Insights**: Proactive health recommendations

### Benefits of ML-Driven Approach
- **Personalization**: Tailored to individual user patterns
- **Accuracy**: Improved prediction quality over time
- **Adaptability**: Self-improving algorithms
- **Clinical Relevance**: Evidence-based recommendations
- **User Engagement**: More relevant and actionable insights

### Technical Considerations
- **Data Quality**: Ensure sufficient data for reliable predictions
- **Model Validation**: Cross-validation and clinical validation
- **Fallback Mechanisms**: Default values when ML predictions unavailable
- **Privacy**: Secure handling of sensitive health data
- **Performance**: Efficient real-time prediction capabilities

## Conclusion
Replacing these hard-coded values with ML-driven alternatives will significantly enhance the application's ability to provide personalized, accurate, and clinically relevant insights for IBS management. The implementation should be phased to ensure stability while progressively improving the intelligence of the system.