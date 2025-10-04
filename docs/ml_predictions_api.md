# ML Predictions API Documentation

## Overview

The ML Predictions API provides advanced machine learning capabilities for IBS wellness management, including symptom prediction, dietary analysis, stress correlation, sleep impact assessment, exercise tolerance, symptom progression forecasting, and treatment response prediction.

## Base URL
```
/api/v1/ml-predictions
```

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Symptom Risk Prediction
**POST** `/symptom-risk`

Predicts the likelihood of symptom flare-ups based on user data and patterns.

#### Request Body
```json
{
  "user_id": 123,
  "timeframe_hours": 24,
  "include_triggers": true,
  "severity_threshold": "medium"
}
```

#### Response
```json
{
  "risk_score": 0.75,
  "confidence": 0.85,
  "predicted_symptoms": ["abdominal_pain", "bloating"],
  "risk_factors": ["high_stress", "trigger_food_consumed"],
  "recommendations": [
    {
      "type": "dietary",
      "action": "Avoid high-FODMAP foods",
      "priority": "high"
    }
  ],
  "timeframe": "next_24_hours",
  "model_version": "enhanced_v1.0",
  "prediction_timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Dietary Trigger Analysis
**POST** `/dietary-triggers`

Analyzes food diary data to identify potential dietary triggers and correlations with symptoms.

#### Request Body
```json
{
  "user_id": 123,
  "analysis_period_days": 30,
  "include_meal_timing": true,
  "severity_filter": "all"
}
```

#### Response
```json
{
  "trigger_foods": [
    {
      "food": "wheat_bread",
      "correlation_score": 0.82,
      "confidence": 0.78,
      "frequency": 15,
      "avg_symptom_severity": 7.2
    }
  ],
  "safe_foods": ["rice", "chicken", "carrots"],
  "meal_timing_patterns": {
    "optimal_meal_times": ["07:00", "12:30", "18:00"],
    "problematic_patterns": ["late_night_eating", "skipping_breakfast"]
  },
  "recommendations": [
    {
      "type": "elimination",
      "foods": ["wheat_bread", "dairy"],
      "duration_days": 14
    }
  ],
  "confidence": 0.85,
  "model_version": "enhanced_v1.0"
}
```

### 3. Stress-Symptom Correlation
**POST** `/stress-correlation`

Analyzes the relationship between stress levels and IBS symptoms.

#### Request Body
```json
{
  "user_id": 123,
  "analysis_period_days": 60,
  "include_lifestyle_factors": true,
  "stress_sources": ["work", "personal", "health"]
}
```

#### Response
```json
{
  "correlation_strength": 0.73,
  "stress_impact_score": 8.2,
  "peak_stress_periods": [
    {
      "time_range": "09:00-11:00",
      "avg_stress_level": 8.5,
      "symptom_correlation": 0.78
    }
  ],
  "stress_patterns": [
    {
      "pattern": "work_deadline_stress",
      "frequency": "weekly",
      "impact_severity": "high"
    }
  ],
  "interventions": [
    {
      "type": "mindfulness",
      "technique": "deep_breathing",
      "recommended_times": ["morning", "before_meals"]
    }
  ],
  "confidence": 0.82,
  "model_version": "enhanced_v1.0"
}
```

### 4. Sleep Quality Impact
**POST** `/sleep-impact`

Assesses how sleep quality affects IBS symptoms and provides optimization recommendations.

#### Request Body
```json
{
  "user_id": 123,
  "sleep_data_days": 30,
  "include_sleep_patterns": true,
  "target_improvement": "symptom_reduction"
}
```

#### Response
```json
{
  "sleep_quality_score": 6.8,
  "symptom_correlation": 0.65,
  "optimal_sleep_duration": 8.2,
  "sleep_patterns": {
    "bedtime_consistency": 0.72,
    "wake_time_consistency": 0.68,
    "sleep_efficiency": 0.85
  },
  "recommendations": [
    {
      "type": "sleep_hygiene",
      "action": "Maintain consistent bedtime",
      "target_time": "22:30"
    }
  ],
  "impact_level": "moderate",
  "confidence": 0.79,
  "model_version": "enhanced_v1.0"
}
```

### 5. Exercise Tolerance Prediction
**POST** `/exercise-tolerance`

Predicts safe exercise levels and types based on current symptoms and fitness history.

#### Request Body
```json
{
  "user_id": 123,
  "current_symptoms": ["mild_bloating"],
  "fitness_level": "intermediate",
  "preferred_activities": ["walking", "yoga", "swimming"],
  "time_available": 45
}
```

#### Response
```json
{
  "tolerance_score": 7.5,
  "recommended_intensity": "moderate",
  "safe_exercises": [
    {
      "activity": "walking",
      "duration": 30,
      "intensity": "moderate",
      "precautions": ["avoid_immediately_after_meals"]
    }
  ],
  "exercise_plan": {
    "weekly_schedule": {
      "monday": {"activity": "yoga", "duration": 45},
      "wednesday": {"activity": "walking", "duration": 30},
      "friday": {"activity": "swimming", "duration": 40}
    }
  },
  "precautions": ["Monitor symptoms during exercise", "Stay hydrated"],
  "progression_timeline": {
    "week_1": "maintain_current_level",
    "week_4": "increase_duration_10_percent",
    "week_8": "add_strength_training"
  },
  "confidence": 0.83,
  "model_version": "enhanced_v1.0"
}
```

### 6. Medication Effectiveness Prediction
**POST** `/medication-effectiveness`

Predicts how effective medications will be based on user history and current symptoms.

#### Request Body
```json
{
  "user_id": 123,
  "medication_history": [
    {
      "name": "loperamide",
      "dosage": "2mg",
      "effectiveness": 7,
      "side_effects": ["mild_drowsiness"]
    }
  ],
  "current_symptoms": {
    "diarrhea": 6,
    "abdominal_pain": 4
  }
}
```

#### Response
```json
{
  "effectiveness_score": 0.78,
  "confidence": 0.85,
  "predicted_improvement": 0.62,
  "time_to_effect": 2,
  "side_effect_risk": 0.25,
  "recommendations": [
    {
      "medication": "loperamide",
      "dosage": "2mg",
      "timing": "as_needed",
      "effectiveness_prediction": 0.78
    }
  ],
  "alternative_suggestions": [
    {
      "medication": "probiotics",
      "type": "supplement",
      "effectiveness_prediction": 0.65
    }
  ],
  "model_version": "enhanced_v1.0",
  "prediction_timestamp": "2024-01-15T10:30:00Z"
}
```

### 7. Symptom Progression Forecasting
**POST** `/symptom-progression`

Forecasts how symptoms may progress over time based on historical patterns and current factors.

#### Request Body
```json
{
  "user_id": 123,
  "forecast_days": 30,
  "include_risk_factors": true,
  "intervention_scenarios": ["medication", "dietary_changes"]
}
```

#### Response
```json
{
  "progression_forecast": {
    "week_1": {
      "predicted_severity": 5.2,
      "confidence": 0.82,
      "dominant_symptoms": ["bloating", "abdominal_pain"]
    },
    "week_2": {
      "predicted_severity": 4.8,
      "confidence": 0.78,
      "dominant_symptoms": ["bloating"]
    }
  },
  "risk_periods": [
    {
      "start_date": "2024-01-20",
      "end_date": "2024-01-22",
      "risk_level": "high",
      "triggers": ["work_stress", "dietary_indiscretion"]
    }
  ],
  "trend_analysis": {
    "overall_direction": "improving",
    "severity_change": -0.8,
    "frequency_change": -0.3
  },
  "intervention_impact": {
    "medication": {
      "severity_reduction": 1.2,
      "confidence": 0.75
    },
    "dietary_changes": {
      "severity_reduction": 0.8,
      "confidence": 0.82
    }
  },
  "confidence": 0.79,
  "model_version": "enhanced_v1.0"
}
```

### 8. Treatment Response Prediction
**POST** `/treatment-response`

Predicts how well a user will respond to specific treatments based on their profile and history.

#### Request Body
```json
{
  "user_id": 123,
  "treatment_type": "dietary_modification",
  "treatment_details": {
    "type": "low_fodmap",
    "duration_weeks": 6,
    "compliance_expected": 0.85
  },
  "baseline_severity": 6.5
}
```

#### Response
```json
{
  "response_probability": 0.78,
  "predicted_improvement": 0.65,
  "response_timeline": {
    "week_2": {
      "improvement_percentage": 0.25,
      "confidence": 0.72
    },
    "week_4": {
      "improvement_percentage": 0.55,
      "confidence": 0.78
    },
    "week_6": {
      "improvement_percentage": 0.65,
      "confidence": 0.75
    }
  },
  "side_effect_risk": {
    "overall_risk": 0.15,
    "common_effects": ["initial_symptom_increase", "nutritional_concerns"],
    "risk_factors": ["restrictive_diet", "compliance_challenges"]
  },
  "alternative_treatments": [
    {
      "treatment": "probiotic_therapy",
      "response_probability": 0.68,
      "advantages": ["fewer_restrictions", "gut_health_benefits"]
    }
  ],
  "monitoring_recommendations": [
    "Track symptom severity daily",
    "Monitor nutritional status",
    "Regular follow-up appointments"
  ],
  "confidence": 0.81,
  "model_version": "enhanced_v1.0"
}
```

## Error Responses

All endpoints return standardized error responses:

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": {
    "field": "user_id",
    "issue": "required field missing"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "authentication_error",
  "message": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "error": "user_not_found",
  "message": "User with specified ID not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "prediction_error",
  "message": "ML model prediction failed",
  "fallback_used": true
}
```

## Rate Limiting

- **Rate Limit**: 100 requests per hour per user
- **Burst Limit**: 10 requests per minute
- **Headers**: 
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time (Unix timestamp)

## Model Versions and Updates

- **Current Version**: enhanced_v1.0
- **Update Frequency**: Monthly model retraining
- **Backward Compatibility**: Maintained for 6 months
- **Performance Metrics**: Available via `/model-health` endpoint

## Data Privacy and Security

- All predictions are processed securely and not stored permanently
- User data is anonymized for model training
- HIPAA compliant data handling
- Encryption in transit and at rest

## Support and Feedback

For API support or to report issues:
- Email: api-support@ibswellness.com
- Documentation: https://docs.ibswellness.com/ml-api
- Status Page: https://status.ibswellness.com