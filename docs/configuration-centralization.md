# Configuration Centralization Documentation

## Overview
This document outlines the comprehensive configuration centralization implemented across the IBS Wellness Companion application. All hard-coded values have been moved to centralized configuration files to improve maintainability, consistency, and deployment flexibility.

## Configuration Files Created

### 1. Frontend Configuration (`frontend/src/lib/config.ts`)

#### API Configuration
```typescript
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}
```

#### UI Configuration
```typescript
export const UI_CONFIG = {
  DELAY_SHORT: 100,
  DELAY_MEDIUM: 500,
  DELAY_LONG: 1000,
  SYNC_CHECK_INTERVAL: 30000,
  ANIMATION_DURATION: 300,
  DEBOUNCE_DELAY: 300
}
```

#### Pagination Configuration
```typescript
export const PAGINATION_CONFIG = {
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  ITEMS_PER_PAGE_OPTIONS: [5, 10, 20, 50]
}
```

#### Validation Configuration
```typescript
export const VALIDATION_CONFIG = {
  MIN_PASSWORD_LENGTH: 8,
  MAX_PASSWORD_LENGTH: 128,
  MIN_USERNAME_LENGTH: 3,
  MAX_USERNAME_LENGTH: 50,
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE_REGEX: /^\+?[\d\s\-\(\)]+$/
}
```

## Files Modified

### Service Files
All service files in `frontend/src/services/` were updated to use centralized API configuration:

1. **analytics-service.ts**
   - Replaced hard-coded `API_BASE_URL` with `API_CONFIG.BASE_URL`
   - Added import: `import { API_CONFIG } from '../lib/config'`

2. **goals-service.ts**
   - Replaced hard-coded `API_BASE_URL` with `API_CONFIG.BASE_URL`
   - Added import: `import { API_CONFIG } from '../lib/config'`

3. **personalization-service.ts**
   - Replaced hard-coded `API_BASE_URL` with `API_CONFIG.BASE_URL`
   - Added import: `import { API_CONFIG } from '../lib/config'`

4. **appointments-service.ts**
   - Replaced hard-coded `API_BASE_URL` with `API_CONFIG.BASE_URL`
   - Added import: `import { API_CONFIG } from '../lib/config'`

5. **ml-service.ts**
   - Replaced hard-coded `API_BASE_URL` with `API_CONFIG.BASE_URL`
   - Added import: `import { API_CONFIG } from '../lib/config'`

6. **dynamic-dashboard-service.ts**
   - Replaced hard-coded `API_BASE_URL` with `API_CONFIG.BASE_URL`
   - Added import: `import { API_CONFIG } from '../lib/config'`

7. **dashboard-analytics-service.ts**
   - Replaced hard-coded `API_BASE_URL` with `API_CONFIG.BASE_URL`
   - Added import: `import { API_CONFIG } from '../lib/config'`

### Hook Files
1. **useUserSync.ts**
   - Replaced hard-coded `30000ms` interval with `UI_CONFIG.SYNC_CHECK_INTERVAL`
   - Added import: `import { UI_CONFIG } from '../lib/config'`

### Library Files
1. **report-sharing.ts**
   - Replaced hard-coded `500ms` delay with `UI_CONFIG.DELAY_MEDIUM`
   - Added import: `import { UI_CONFIG } from '../lib/config'`

### Component Files
1. **test-data-generator.tsx**
   - Replaced hard-coded `100ms` delay with `UI_CONFIG.DELAY_SHORT`
   - Replaced hard-coded `500ms` delay with `UI_CONFIG.DELAY_MEDIUM`
   - Added import: `import { UI_CONFIG } from '../lib/config'`

2. **diet-stats.tsx**
   - Replaced hard-coded `500ms` delay with `UI_CONFIG.DELAY_MEDIUM`
   - Added import: `import { UI_CONFIG } from '../lib/config'`

### Context Files
1. **auth-context.tsx**
   - Added direct `User` interface definition to resolve import dependencies
   - Ensured API configuration uses `API_CONFIG`

## Benefits of Centralization

### 1. Maintainability
- All configuration values are in one place
- Easy to update timeouts, delays, and API endpoints
- Consistent naming conventions across the application

### 2. Environment Management
- Easy to configure different values for development, staging, and production
- Environment variables are properly handled through centralized config

### 3. Type Safety
- All configuration objects are properly typed
- IDE autocomplete and error checking for configuration values

### 4. Consistency
- Standardized delay values across components
- Consistent API timeout and retry configurations
- Uniform pagination settings

### 5. Testing
- Easy to mock configuration values in tests
- Centralized place to adjust test timeouts and delays

## Usage Examples

### Using API Configuration
```typescript
import { API_CONFIG } from '../lib/config'

const response = await fetch(`${API_CONFIG.BASE_URL}/api/endpoint`, {
  timeout: API_CONFIG.TIMEOUT
})
```

### Using UI Configuration
```typescript
import { UI_CONFIG } from '../lib/config'

setTimeout(() => {
  // Action after medium delay
}, UI_CONFIG.DELAY_MEDIUM)
```

### Using Validation Configuration
```typescript
import { VALIDATION_CONFIG } from '../lib/config'

if (password.length < VALIDATION_CONFIG.MIN_PASSWORD_LENGTH) {
  // Handle validation error
}
```

## Environment Variables

The configuration system respects the following environment variables:

- `NEXT_PUBLIC_API_URL`: Base URL for API calls (defaults to `http://localhost:8000`)

## Testing Results

✅ **Frontend Application**: Successfully compiling and running
✅ **Backend Integration**: API calls working with centralized configuration
✅ **No Breaking Changes**: All existing functionality preserved
✅ **Type Safety**: All configuration values properly typed

## Future Enhancements

1. **Theme Configuration**: Centralize color schemes and UI themes
2. **Feature Flags**: Add configuration for enabling/disabling features
3. **Monitoring Configuration**: Centralize logging and analytics settings
4. **Cache Configuration**: Add centralized cache timeout and size settings

## Conclusion

The configuration centralization successfully eliminates hard-coded values throughout the application while maintaining full functionality. The system is now more maintainable, consistent, and ready for different deployment environments.