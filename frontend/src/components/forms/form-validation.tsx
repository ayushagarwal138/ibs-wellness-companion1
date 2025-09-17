'use client';

import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';
import { Badge } from '../ui/badge';

// Validation rule types
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  min?: number;
  max?: number;
  custom?: (value: any) => string | null;
}

export interface ValidationError {
  field: string;
  message: string;
  type: 'error' | 'warning' | 'info';
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'number' | 'select' | 'textarea' | 'checkbox' | 'date' | 'time';
  rules?: ValidationRule;
  options?: { value: string; label: string }[];
  placeholder?: string;
  helpText?: string;
}

// Validation utility functions
export class FormValidator {
  static validateField(value: any, rules: ValidationRule, fieldName: string): ValidationError | null {
    if (rules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
      return {
        field: fieldName,
        message: `${fieldName} is required`,
        type: 'error'
      };
    }

    if (value && typeof value === 'string') {
      if (rules.minLength && value.length < rules.minLength) {
        return {
          field: fieldName,
          message: `${fieldName} must be at least ${rules.minLength} characters`,
          type: 'error'
        };
      }

      if (rules.maxLength && value.length > rules.maxLength) {
        return {
          field: fieldName,
          message: `${fieldName} must not exceed ${rules.maxLength} characters`,
          type: 'error'
        };
      }

      if (rules.pattern && !rules.pattern.test(value)) {
        return {
          field: fieldName,
          message: `${fieldName} format is invalid`,
          type: 'error'
        };
      }
    }

    if (value && typeof value === 'number') {
      if (rules.min !== undefined && value < rules.min) {
        return {
          field: fieldName,
          message: `${fieldName} must be at least ${rules.min}`,
          type: 'error'
        };
      }

      if (rules.max !== undefined && value > rules.max) {
        return {
          field: fieldName,
          message: `${fieldName} must not exceed ${rules.max}`,
          type: 'error'
        };
      }
    }

    if (rules.custom && value) {
      const customError = rules.custom(value);
      if (customError) {
        return {
          field: fieldName,
          message: customError,
          type: 'error'
        };
      }
    }

    return null;
  }

  static validateForm(data: Record<string, any>, fields: FormField[]): ValidationError[] {
    const errors: ValidationError[] = [];

    fields.forEach(field => {
      if (field.rules) {
        const error = this.validateField(data[field.name], field.rules, field.label);
        if (error) {
          errors.push(error);
        }
      }
    });

    return errors;
  }

  // IBS-specific validation rules
  static ibsValidationRules = {
    symptomSeverity: {
      required: true,
      min: 1,
      max: 10,
      custom: (value: number) => {
        if (!Number.isInteger(value)) {
          return 'Severity must be a whole number';
        }
        return null;
      }
    },
    
    email: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      custom: (value: string) => {
        if (value && !value.includes('.')) {
          return 'Please enter a valid email address';
        }
        return null;
      }
    },

    password: {
      required: true,
      minLength: 8,
      custom: (value: string) => {
        if (value && !/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          return 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
        }
        return null;
      }
    },

    foodName: {
      required: true,
      minLength: 2,
      maxLength: 50,
      custom: (value: string) => {
        if (value && /[0-9]/.test(value)) {
          return 'Food name should not contain numbers';
        }
        return null;
      }
    },

    medicationDosage: {
      required: true,
      pattern: /^\d+(\.\d+)?\s*(mg|g|ml|tablets?|capsules?)$/i,
      custom: (value: string) => {
        if (value && !value.match(/^\d+(\.\d+)?\s*(mg|g|ml|tablets?|capsules?)$/i)) {
          return 'Please specify dosage with unit (e.g., "10 mg", "2 tablets")';
        }
        return null;
      }
    },

    phoneNumber: {
      pattern: /^[\+]?[1-9][\d]{0,15}$/,
      custom: (value: string) => {
        if (value && value.length < 10) {
          return 'Phone number must be at least 10 digits';
        }
        return null;
      }
    }
  };
}

// Error display component
interface ErrorDisplayProps {
  errors: ValidationError[];
  className?: string;
}

export function ErrorDisplay({ errors, className = '' }: ErrorDisplayProps) {
  if (errors.length === 0) return null;

  return (
    <div className={`space-y-2 ${className}`}>
      {errors.map((error, index) => (
        <div
          key={index}
          className={`flex items-start space-x-2 p-3 rounded-md text-sm ${
            error.type === 'error'
              ? 'bg-red-50 border border-red-200 text-red-700'
              : error.type === 'warning'
              ? 'bg-yellow-50 border border-yellow-200 text-yellow-700'
              : 'bg-blue-50 border border-blue-200 text-blue-700'
          }`}
        >
          {error.type === 'error' && <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />}
          {error.type === 'warning' && <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />}
          {error.type === 'info' && <Info size={16} className="mt-0.5 flex-shrink-0" />}
          <span>{error.message}</span>
        </div>
      ))}
    </div>
  );
}

// Success message component
interface SuccessMessageProps {
  message: string;
  onDismiss?: () => void;
  className?: string;
}

export function SuccessMessage({ message, onDismiss, className = '' }: SuccessMessageProps) {
  return (
    <div className={`flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-md text-green-700 ${className}`}>
      <div className="flex items-center space-x-2">
        <CheckCircle size={20} />
        <span className="font-medium">{message}</span>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-green-500 hover:text-green-700"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}

// Loading state component
interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({ message = 'Processing...', className = '' }: LoadingStateProps) {
  return (
    <div className={`flex items-center justify-center space-x-3 p-6 ${className}`}>
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
      <span className="text-gray-600">{message}</span>
    </div>
  );
}

// Form field wrapper with validation
interface ValidatedFieldProps {
  field: FormField;
  value: any;
  onChange: (value: any) => void;
  error?: ValidationError;
  className?: string;
}

export function ValidatedField({ field, value, onChange, error, className = '' }: ValidatedFieldProps) {
  const [touched, setTouched] = useState(false);
  const [localError, setLocalError] = useState<ValidationError | null>(null);

  useEffect(() => {
    if (touched && field.rules) {
      const validationError = FormValidator.validateField(value, field.rules, field.label);
      setLocalError(validationError);
    }
  }, [value, touched, field.rules, field.label]);

  const displayError = error || localError;
  const hasError = displayError && touched;

  const handleBlur = () => {
    setTouched(true);
  };

  const renderField = () => {
    const baseClasses = `w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
      hasError ? 'border-red-300 bg-red-50' : 'border-gray-300'
    }`;

    switch (field.type) {
      case 'textarea':
        return (
          <textarea
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            onBlur={handleBlur}
            placeholder={field.placeholder}
            className={`${baseClasses} min-h-[100px] resize-vertical`}
            rows={4}
          />
        );

      case 'select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            onBlur={handleBlur}
            className={baseClasses}
          >
            <option value="">{field.placeholder || `Select ${field.label}`}</option>
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'checkbox':
        return (
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={value || false}
              onChange={(e) => onChange(e.target.checked)}
              onBlur={handleBlur}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">{field.label}</span>
          </div>
        );

      case 'number':
        return (
          <input
            type="number"
            value={value || ''}
            onChange={(e) => onChange(parseFloat(e.target.value) || '')}
            onBlur={handleBlur}
            placeholder={field.placeholder}
            className={baseClasses}
            min={field.rules?.min}
            max={field.rules?.max}
          />
        );

      default:
        return (
          <input
            type={field.type}
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            onBlur={handleBlur}
            placeholder={field.placeholder}
            className={baseClasses}
          />
        );
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {field.type !== 'checkbox' && (
        <label className="block text-sm font-medium text-gray-700">
          {field.label}
          {field.rules?.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {renderField()}
      
      {field.helpText && !hasError && (
        <p className="text-sm text-gray-500">{field.helpText}</p>
      )}
      
      {hasError && (
        <p className="text-sm text-red-600 flex items-center space-x-1">
          <AlertCircle size={14} />
          <span>{displayError.message}</span>
        </p>
      )}
    </div>
  );
}

// Form progress indicator
interface FormProgressProps {
  currentStep: number;
  totalSteps: number;
  stepLabels?: string[];
  className?: string;
}

export function FormProgress({ currentStep, totalSteps, stepLabels, className = '' }: FormProgressProps) {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">
          Step {currentStep} of {totalSteps}
        </span>
        <span className="text-sm text-gray-500">{Math.round(progress)}% complete</span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      {stepLabels && (
        <div className="flex justify-between text-xs text-gray-500">
          {stepLabels.map((label, index) => (
            <span
              key={index}
              className={`${
                index < currentStep ? 'text-blue-600 font-medium' : ''
              }`}
            >
              {label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

// Real-time validation hook
export function useFormValidation(fields: FormField[], initialData: Record<string, any> = {}) {
  const [data, setData] = useState(initialData);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [isValid, setIsValid] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const validationErrors = FormValidator.validateForm(data, fields);
    setErrors(validationErrors);
    setIsValid(validationErrors.length === 0);
  }, [data, fields]);

  const updateField = (fieldName: string, value: any) => {
    setData(prev => ({ ...prev, [fieldName]: value }));
  };

  const validateField = (fieldName: string) => {
    const field = fields.find(f => f.name === fieldName);
    if (field && field.rules) {
      const error = FormValidator.validateField(data[fieldName], field.rules, field.label);
      return error;
    }
    return null;
  };

  const reset = () => {
    setData(initialData);
    setErrors([]);
    setIsSubmitting(false);
  };

  return {
    data,
    errors,
    isValid,
    isSubmitting,
    setIsSubmitting,
    updateField,
    validateField,
    reset
  };
}

// Example usage component
export function FormValidationExample() {
  const fields: FormField[] = [
    {
      name: 'email',
      label: 'Email Address',
      type: 'email',
      rules: FormValidator.ibsValidationRules.email,
      placeholder: 'Enter your email',
      helpText: 'We\'ll use this to send you updates'
    },
    {
      name: 'severity',
      label: 'Symptom Severity',
      type: 'number',
      rules: FormValidator.ibsValidationRules.symptomSeverity,
      placeholder: 'Rate from 1-10',
      helpText: '1 = Very mild, 10 = Severe'
    },
    {
      name: 'food',
      label: 'Food Item',
      type: 'text',
      rules: FormValidator.ibsValidationRules.foodName,
      placeholder: 'Enter food name'
    }
  ];

  const { data, errors, isValid, updateField, reset } = useFormValidation(fields);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isValid) {
      console.log('Form submitted:', data);
      // Handle form submission
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white border rounded-lg">
      <h2 className="text-xl font-semibold mb-6">Form Validation Example</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {fields.map(field => (
          <ValidatedField
            key={field.name}
            field={field}
            value={data[field.name]}
            onChange={(value) => updateField(field.name, value)}
          />
        ))}
        
        <ErrorDisplay errors={errors} />
        
        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={!isValid}
            className={`flex-1 py-2 px-4 rounded-md font-medium ${
              isValid
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Submit
          </button>
          
          <button
            type="button"
            onClick={reset}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Reset
          </button>
        </div>
      </form>
    </div>
  );
}