/**
 * Frontend Configuration Management
 * Centralized access to all environment variables and configuration settings
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000',
  WS_URL: process.env['NEXT_PUBLIC_WS_URL'] || 'ws://localhost:8000',
  TIMEOUT: parseInt(process.env['NEXT_PUBLIC_API_TIMEOUT'] || '30000'),
  RETRY_ATTEMPTS: parseInt(process.env['NEXT_PUBLIC_API_RETRY_ATTEMPTS'] || '3'),
} as const;

// Authentication Configuration
export const AUTH_CONFIG = {
  NEXTAUTH_URL: process.env['NEXTAUTH_URL'] || 'http://localhost:3000',
  NEXTAUTH_SECRET: process.env['NEXTAUTH_SECRET'] || '',
  AUTH_PROVIDER: process.env['NEXT_PUBLIC_AUTH_PROVIDER'] || 'oauth2',
  GOOGLE_CLIENT_ID: process.env['GOOGLE_CLIENT_ID'] || '',
  GOOGLE_CLIENT_SECRET: process.env['GOOGLE_CLIENT_SECRET'] || '',
  GITHUB_CLIENT_ID: process.env['GITHUB_CLIENT_ID'] || '',
  GITHUB_CLIENT_SECRET: process.env['GITHUB_CLIENT_SECRET'] || '',
} as const;

// Firebase Configuration
export const FIREBASE_CONFIG = {
  API_KEY: process.env['NEXT_PUBLIC_FIREBASE_API_KEY'] || '',
  AUTH_DOMAIN: process.env['NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN'] || '',
  PROJECT_ID: process.env['NEXT_PUBLIC_FIREBASE_PROJECT_ID'] || '',
  STORAGE_BUCKET: process.env['NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET'] || '',
  MESSAGING_SENDER_ID: process.env['NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID'] || '',
  APP_ID: process.env['NEXT_PUBLIC_FIREBASE_APP_ID'] || '',
  VAPID_KEY: process.env['NEXT_PUBLIC_FIREBASE_VAPID_KEY'] || '',
  MEASUREMENT_ID: process.env['NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID'] || '',
} as const;

// Analytics Configuration
export const ANALYTICS_CONFIG = {
  GA_MEASUREMENT_ID: process.env['NEXT_PUBLIC_GA_MEASUREMENT_ID'] || '',
  GTAG_ID: process.env['NEXT_PUBLIC_GTAG_ID'] || '',
  ENABLE_ANALYTICS: process.env['NEXT_PUBLIC_ENABLE_ANALYTICS'] === 'true',
} as const;

// Application Settings
export const APP_CONFIG = {
  NAME: process.env['NEXT_PUBLIC_APP_NAME'] || 'IBS Wellness Companion',
  VERSION: process.env['NEXT_PUBLIC_APP_VERSION'] || '1.0.0',
  DESCRIPTION: process.env['NEXT_PUBLIC_APP_DESCRIPTION'] || 'AI-powered IBS management platform',
  ENVIRONMENT: process.env['NEXT_PUBLIC_ENVIRONMENT'] || 'development',
  DEBUG: process.env['NEXT_PUBLIC_DEBUG'] === 'true',
} as const;

// UI/UX Configuration
export const UI_CONFIG = {
  DEFAULT_PAGE_SIZE: parseInt(process.env['NEXT_PUBLIC_DEFAULT_PAGE_SIZE'] || '10'),
  MAX_PAGE_SIZE: parseInt(process.env['NEXT_PUBLIC_MAX_PAGE_SIZE'] || '50'),
  MAX_FILE_SIZE: parseInt(process.env['NEXT_PUBLIC_MAX_FILE_SIZE'] || '10485760'),
  ALLOWED_FILE_TYPES: process.env['NEXT_PUBLIC_ALLOWED_FILE_TYPES']?.split(',') || ['jpg', 'jpeg', 'png', 'pdf', 'txt', 'csv'],
  CHART_ANIMATION_DURATION: parseInt(process.env['NEXT_PUBLIC_CHART_ANIMATION_DURATION'] || '750'),
  CHART_COLORS: process.env['NEXT_PUBLIC_CHART_COLORS']?.split(',') || ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'],
  DASHBOARD_REFRESH_INTERVAL: parseInt(process.env['NEXT_PUBLIC_DASHBOARD_REFRESH_INTERVAL'] || '300000'),
  REALTIME_UPDATE_INTERVAL: parseInt(process.env['NEXT_PUBLIC_REALTIME_UPDATE_INTERVAL'] || '5000'),
  DELAY_SHORT: parseInt(process.env['NEXT_PUBLIC_UI_DELAY_SHORT'] || '100'),
  DELAY_MEDIUM: parseInt(process.env['NEXT_PUBLIC_UI_DELAY_MEDIUM'] || '500'),
  SYNC_CHECK_INTERVAL: parseInt(process.env['NEXT_PUBLIC_SYNC_CHECK_INTERVAL'] || '30000'),
} as const;

// Feature Flags
export const FEATURE_FLAGS = {
  ENABLE_ANALYTICS: process.env['NEXT_PUBLIC_ENABLE_ANALYTICS'] === 'true',
  ENABLE_NOTIFICATIONS: process.env['NEXT_PUBLIC_ENABLE_NOTIFICATIONS'] === 'true',
  ENABLE_CHATBOT: process.env['NEXT_PUBLIC_ENABLE_CHATBOT'] === 'true',
  ENABLE_ML_PREDICTIONS: process.env['NEXT_PUBLIC_ENABLE_ML_PREDICTIONS'] === 'true',
  ENABLE_DARK_MODE: process.env['NEXT_PUBLIC_ENABLE_DARK_MODE'] === 'true',
  ENABLE_OFFLINE_MODE: process.env['NEXT_PUBLIC_ENABLE_OFFLINE_MODE'] === 'true',
} as const;

// External Services
export const EXTERNAL_SERVICES = {
  CDN_URL: process.env['NEXT_PUBLIC_CDN_URL'] || '',
  ASSETS_URL: process.env['NEXT_PUBLIC_ASSETS_URL'] || '',
  GOOGLE_MAPS_API_KEY: process.env['NEXT_PUBLIC_GOOGLE_MAPS_API_KEY'] || '',
} as const;

// Security Settings
export const SECURITY_CONFIG = {
  CSP_REPORT_URI: process.env['NEXT_PUBLIC_CSP_REPORT_URI'] || '',
} as const;

// Performance Settings
export const PERFORMANCE_CONFIG = {
  IMAGE_DOMAINS: process.env['NEXT_PUBLIC_IMAGE_DOMAINS']?.split(',') || ['localhost'],
  IMAGE_QUALITY: parseInt(process.env['NEXT_PUBLIC_IMAGE_QUALITY'] || '75'),
  ENABLE_PERFORMANCE_MONITORING: process.env['NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING'] === 'true',
} as const;

// Monitoring and Error Tracking
export const MONITORING_CONFIG = {
  SENTRY_DSN: process.env['NEXT_PUBLIC_SENTRY_DSN'] || '',
  SENTRY_ENVIRONMENT: process.env['NEXT_PUBLIC_SENTRY_ENVIRONMENT'] || 'development',
} as const;

// Localization
export const LOCALIZATION_CONFIG = {
  DEFAULT_LOCALE: process.env['NEXT_PUBLIC_DEFAULT_LOCALE'] || 'en',
  SUPPORTED_LOCALES: process.env['NEXT_PUBLIC_SUPPORTED_LOCALES']?.split(',') || ['en'],
} as const;

// Testing Configuration
export const TEST_CONFIG = {
  TEST_MODE: process.env['NEXT_PUBLIC_TEST_MODE'] === 'true',
  MOCK_API: process.env['NEXT_PUBLIC_MOCK_API'] === 'true',
} as const;

// Development Settings
export const DEV_CONFIG = {
  ANALYZE: process.env['ANALYZE'] === 'true',
  BUNDLE_ANALYZE: process.env['BUNDLE_ANALYZE'] === 'true',
} as const;

// Consolidated configuration object
export const CONFIG = {
  API: API_CONFIG,
  AUTH: AUTH_CONFIG,
  FIREBASE: FIREBASE_CONFIG,
  ANALYTICS: ANALYTICS_CONFIG,
  APP: APP_CONFIG,
  UI: UI_CONFIG,
  FEATURES: FEATURE_FLAGS,
  EXTERNAL: EXTERNAL_SERVICES,
  SECURITY: SECURITY_CONFIG,
  PERFORMANCE: PERFORMANCE_CONFIG,
  MONITORING: MONITORING_CONFIG,
  LOCALIZATION: LOCALIZATION_CONFIG,
  TEST: TEST_CONFIG,
  DEV: DEV_CONFIG,
} as const;

export default CONFIG;