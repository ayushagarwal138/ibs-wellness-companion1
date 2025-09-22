/**
 * Profile validation hook for comprehensive frontend validation and data handling.
 */

import { useState, useCallback, useMemo } from 'react';

export interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  date_of_birth?: string;
  gender?: string;
  height_cm?: number;
  weight_kg?: number;
  ibs_type?: string;
  diagnosis_date?: string;
  medical_notes?: string;
  [key: string]: any;
}

export interface ValidationError {
  field: string;
  message: string;
  section?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  suggestions: string[];
}

export interface ProfileCompletionStatus {
  overallCompletion: number;
  sectionCompletion: Record<string, number>;
  missingRequiredFields: string[];
  recommendedNextSteps: string[];
}

interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  min?: number;
  max?: number;
  options?: string[];
  validate?: (value: any) => boolean;
  message?: string;
}

export const useProfileValidation = () => {
  const [validationState, setValidationState] = useState<ValidationResult>({
    isValid: true,
    errors: [],
    warnings: [],
    suggestions: []
  });

  const [isValidating, setIsValidating] = useState(false);

  // Field validation rules
  const validationRules = useMemo((): Record<string, ValidationRule> => ({
    // Basic Information
    first_name: {
      required: true,
      minLength: 2,
      maxLength: 50,
      pattern: /^[a-zA-Z\s'-]+$/,
      message: 'First name must be 2-50 characters and contain only letters, spaces, hyphens, and apostrophes'
    },
    last_name: {
      required: true,
      minLength: 2,
      maxLength: 50,
      pattern: /^[a-zA-Z\s'-]+$/,
      message: 'Last name must be 2-50 characters and contain only letters, spaces, hyphens, and apostrophes'
    },
    email: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      message: 'Please enter a valid email address'
    },
    phone_number: {
      required: false,
      pattern: /^[\+]?[1-9][\d]{0,15}$/,
      message: 'Please enter a valid phone number'
    },
    date_of_birth: {
      required: true,
      validate: (value: string) => {
        if (!value) return false;
        const date = new Date(value);
        const today = new Date();
        const age = today.getFullYear() - date.getFullYear();
        return age >= 13 && age <= 120;
      },
      message: 'Age must be between 13 and 120 years'
    },
    gender: {
      required: true,
      options: ['male', 'female', 'other', 'prefer_not_to_say'],
      message: 'Please select a gender option'
    },
    height_cm: {
      required: false,
      min: 50,
      max: 300,
      message: 'Height must be between 50 and 300 cm'
    },
    weight_kg: {
      required: false,
      min: 20,
      max: 500,
      message: 'Weight must be between 20 and 500 kg'
    },

    // Medical History
    ibs_type: {
      required: true,
      options: ['ibs-d', 'ibs-c', 'ibs-m', 'ibs-u'],
      message: 'Please select your IBS type'
    },
    diagnosis_date: {
      required: false,
      validate: (value: string) => {
        if (!value) return true;
        const date = new Date(value);
        const today = new Date();
        return date <= today;
      },
      message: 'Diagnosis date cannot be in the future'
    },
    severity_level: {
      required: false,
      min: 1,
      max: 10,
      message: 'Severity level must be between 1 and 10'
    },

    // Lifestyle Factors
    sleep_quality: {
      required: false,
      min: 1,
      max: 10,
      message: 'Sleep quality must be between 1 and 10'
    },
    stress_level: {
      required: false,
      min: 1,
      max: 10,
      message: 'Stress level must be between 1 and 10'
    },
    exercise_frequency: {
      required: false,
      min: 0,
      max: 7,
      message: 'Exercise frequency must be between 0 and 7 days per week'
    },

    // Dietary Preferences
    meal_frequency: {
      required: false,
      min: 1,
      max: 10,
      message: 'Meal frequency must be between 1 and 10 meals per day'
    },
    water_intake_goal: {
      required: false,
      min: 0.5,
      max: 8,
      message: 'Water intake goal must be between 0.5 and 8 liters per day'
    }
  }), []);

  // Validate individual field
  const validateField = useCallback((fieldName: string, value: any): ValidationError[] => {
    const errors: ValidationError[] = [];
    const rule = validationRules[fieldName];
    
    if (!rule) return errors;

    // Required field validation
    if (rule.required && (!value || value === '')) {
      errors.push({
        field: fieldName,
        message: `${fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} is required`
      });
      return errors;
    }

    // Skip other validations if field is empty and not required
    if (!value && !rule.required) return errors;

    // String validations
    if (typeof value === 'string') {
      if (rule.minLength && value.length < rule.minLength) {
        errors.push({
          field: fieldName,
          message: rule.message || `Minimum length is ${rule.minLength} characters`
        });
      }

      if (rule.maxLength && value.length > rule.maxLength) {
        errors.push({
          field: fieldName,
          message: rule.message || `Maximum length is ${rule.maxLength} characters`
        });
      }

      if (rule.pattern && !rule.pattern.test(value)) {
        errors.push({
          field: fieldName,
          message: rule.message || 'Invalid format'
        });
      }
    }

    // Number validations
    if (typeof value === 'number' || !isNaN(Number(value))) {
      const numValue = Number(value);
      
      if (rule.min !== undefined && numValue < rule.min) {
        errors.push({
          field: fieldName,
          message: rule.message || `Minimum value is ${rule.min}`
        });
      }

      if (rule.max !== undefined && numValue > rule.max) {
        errors.push({
          field: fieldName,
          message: rule.message || `Maximum value is ${rule.max}`
        });
      }
    }

    // Options validation
    if (rule.options && !rule.options.includes(value)) {
      errors.push({
        field: fieldName,
        message: rule.message || 'Invalid option selected'
      });
    }

    // Custom validation function
    if (rule.validate && !rule.validate(value)) {
      errors.push({
        field: fieldName,
        message: rule.message || 'Invalid value'
      });
    }

    return errors;
  }, [validationRules]);

  // Validate entire profile
  const validateProfile = useCallback((profileData: Partial<ProfileData>): ValidationResult => {
    const errors: ValidationError[] = [];
    const warnings: ValidationError[] = [];
    const suggestions: string[] = [];

    // Validate each field
    Object.entries(profileData).forEach(([fieldName, value]) => {
      const fieldErrors = validateField(fieldName, value);
      errors.push(...fieldErrors);
    });

    // Cross-field validations
    if (profileData.height_cm && profileData.weight_kg) {
      const bmi = profileData.weight_kg / Math.pow(profileData.height_cm / 100, 2);
      if (bmi < 15 || bmi > 50) {
        warnings.push({
          field: 'bmi',
          message: 'BMI appears to be outside normal range. Please verify height and weight.'
        });
      }
    }

    // Age and diagnosis date cross-validation
    if (profileData.date_of_birth && profileData.diagnosis_date) {
      const birthDate = new Date(profileData.date_of_birth);
      const diagDate = new Date(profileData.diagnosis_date);
      const ageAtDiagnosis = diagDate.getFullYear() - birthDate.getFullYear();
      
      if (ageAtDiagnosis < 5) {
        warnings.push({
          field: 'diagnosis_date',
          message: 'IBS diagnosis at very young age is uncommon'
        });
      }
    }

    // Generate suggestions
    if (!profileData.height_cm || !profileData.weight_kg) {
      suggestions.push('Adding height and weight helps provide more accurate health insights');
    }

    if (!profileData.ibs_type) {
      suggestions.push('Specifying your IBS type helps personalize recommendations');
    }

    if (!profileData.diagnosis_date) {
      suggestions.push('Adding diagnosis date helps track your health journey');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions
    };
  }, [validateField]);

  // Real-time field validation
  const validateFieldRealTime = useCallback((fieldName: string, value: any) => {
    const fieldErrors = validateField(fieldName, value);
    
    setValidationState(prev => ({
      ...prev,
      errors: [
        ...prev.errors.filter(error => error.field !== fieldName),
        ...fieldErrors
      ]
    }));

    return fieldErrors.length === 0;
  }, [validateField]);

  // Calculate profile completion
  const calculateCompletion = useCallback((profileData: Partial<ProfileData>): ProfileCompletionStatus => {
    const sectionWeights = {
      basicInfo: {
        first_name: 5, last_name: 5, email: 5, phone_number: 3,
        date_of_birth: 8, gender: 5, height_cm: 4, weight_kg: 4
      },
      medicalHistory: {
        ibs_type: 15, diagnosis_date: 10, severity_level: 8,
        known_triggers: 6, common_symptoms: 6, current_medications: 5
      },
      dietaryPreferences: {
        dietary_restrictions: 4, food_allergies: 5, meal_frequency: 3,
        water_intake_goal: 2, trigger_foods: 6, safe_foods: 4
      },
      lifestyleFactors: {
        exercise_frequency: 4, sleep_quality: 5, stress_level: 5,
        smoking_status: 3, alcohol_consumption: 3
      },
      goalsPreferences: {
        primary_goals: 8, preferred_treatments: 4, communication_preferences: 2
      }
    };

    const sectionCompletion: Record<string, number> = {};
    let totalWeight = 0;
    let totalScore = 0;
    const missingRequiredFields: string[] = [];

    Object.entries(sectionWeights).forEach(([section, fields]) => {
      const sectionWeight = Object.values(fields).reduce((sum, weight) => sum + weight, 0);
      let sectionScore = 0;

      Object.entries(fields).forEach(([field, weight]) => {
        const value = profileData[field as keyof ProfileData];
        if (value !== undefined && value !== '' && value !== null) {
          sectionScore += weight;
        } else {
          const rule = validationRules[field];
          if (rule?.required) {
            missingRequiredFields.push(`${section}.${field}`);
          }
        }
      });

      const sectionPercentage = sectionWeight > 0 ? (sectionScore / sectionWeight) * 100 : 0;
      sectionCompletion[section] = Math.round(sectionPercentage * 10) / 10;

      totalWeight += sectionWeight;
      totalScore += sectionScore;
    });

    const overallCompletion = totalWeight > 0 ? (totalScore / totalWeight) * 100 : 0;

    // Generate recommendations
    const recommendedNextSteps: string[] = [];
    if (overallCompletion < 50) {
      recommendedNextSteps.push('Complete basic information to unlock personalized features');
    }
    if (missingRequiredFields.includes('medicalHistory.ibs_type')) {
      recommendedNextSteps.push('Add IBS type for better symptom tracking');
    }
    if (overallCompletion < 80) {
      recommendedNextSteps.push('Complete more sections for comprehensive health insights');
    }

    return {
      overallCompletion: Math.round(overallCompletion * 10) / 10,
      sectionCompletion,
      missingRequiredFields,
      recommendedNextSteps
    };
  }, [validationRules]);

  // Transform data for backend
  const transformForBackend = useCallback((profileData: Partial<ProfileData>) => {
    const transformed = { ...profileData };

    // Transform gender
    if (transformed.gender) {
      const genderMapping: Record<string, string> = {
        'male': 'MALE',
        'female': 'FEMALE',
        'other': 'OTHER',
        'prefer_not_to_say': 'PREFER_NOT_TO_SAY'
      };
      transformed.gender = genderMapping[transformed.gender] || transformed.gender;
    }

    // Transform IBS type
    if (transformed.ibs_type) {
      const ibsMapping: Record<string, string> = {
        'ibs-d': 'IBS_D',
        'ibs-c': 'IBS_C',
        'ibs-m': 'IBS_M',
        'ibs-u': 'IBS_U'
      };
      transformed.ibs_type = ibsMapping[transformed.ibs_type] || transformed.ibs_type;
    }

    // Keep date strings as strings - backend will handle the conversion
    // The backend expects date strings in ISO format (YYYY-MM-DD)
    if (transformed.date_of_birth && typeof transformed.date_of_birth === 'string') {
      // Ensure the date is in the correct format
      try {
        const dateObj = new Date(transformed.date_of_birth);
        if (!isNaN(dateObj.getTime())) {
          // Convert to ISO date string (YYYY-MM-DD)
          transformed.date_of_birth = dateObj.toISOString().split('T')[0];
        }
      } catch (error) {
        console.warn('Invalid date_of_birth format:', transformed.date_of_birth);
      }
    }

    if (transformed.diagnosis_date && typeof transformed.diagnosis_date === 'string') {
      // Ensure the date is in the correct format
      try {
        const dateObj = new Date(transformed.diagnosis_date);
        if (!isNaN(dateObj.getTime())) {
          // Convert to ISO date string (YYYY-MM-DD)
          transformed.diagnosis_date = dateObj.toISOString().split('T')[0];
        }
      } catch (error) {
        console.warn('Invalid diagnosis_date format:', transformed.diagnosis_date);
      }
    }

    return transformed;
  }, []);

  // Transform data from backend
  const transformFromBackend = useCallback((backendData: any) => {
    const transformed = { ...backendData };

    // Transform gender
    if (transformed.gender) {
      const genderMapping: Record<string, string> = {
        'MALE': 'male',
        'FEMALE': 'female',
        'OTHER': 'other',
        'PREFER_NOT_TO_SAY': 'prefer_not_to_say'
      };
      transformed.gender = genderMapping[transformed.gender] || transformed.gender.toLowerCase();
    }

    // Transform IBS type
    if (transformed.ibs_type || transformed.ibsType) {
      const ibsValue = transformed.ibs_type || transformed.ibsType;
      const ibsMapping: Record<string, string> = {
        'IBS_D': 'ibs-d',
        'IBS_C': 'ibs-c',
        'IBS_M': 'ibs-m',
        'IBS_U': 'ibs-u'
      };
      transformed.ibs_type = ibsMapping[ibsValue] || ibsValue.toLowerCase().replace('_', '-');
    }

    return transformed;
  }, []);

  return {
    validationState,
    isValidating,
    setIsValidating,
    validateField: validateFieldRealTime,
    validateProfile,
    calculateCompletion,
    transformForBackend,
    transformFromBackend,
    setValidationState
  };
};