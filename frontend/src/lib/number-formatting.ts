/**
 * Formats a number with appropriate decimal places based on its magnitude.
 * - For values close to zero (< 0.1), shows up to 2 decimal places
 * - For larger values, shows 0 decimal places (rounded to nearest whole number)
 * 
 * @param value - The number to format
 * @param asPercentage - Whether to multiply by 100 and add % symbol (default: false)
 * @returns Formatted string representation of the number
 */
export function formatSmartNumber(value: number, asPercentage: boolean = false): string {
  if (typeof value !== 'number' || isNaN(value)) {
    return '0';
  }

  // Convert to percentage if requested
  const displayValue = asPercentage ? value * 100 : value;
  
  // Always show up to 2 decimal places for better precision
  const formatted = displayValue.toFixed(2);
  // Remove trailing zeros after decimal point
  const cleaned = parseFloat(formatted).toString();
  return asPercentage ? `${cleaned}%` : cleaned;
}

/**
 * Formats a confidence score (0-1 range) as a percentage with smart decimal places
 * 
 * @param confidence - Confidence value between 0 and 1
 * @returns Formatted percentage string
 */
export function formatConfidence(confidence: number): string {
  return formatSmartNumber(confidence, true);
}

/**
 * Formats a risk score (0-1 range) as a percentage with smart decimal places
 * 
 * @param riskScore - Risk score value between 0 and 1
 * @returns Formatted percentage string
 */
export function formatRiskScore(riskScore: number): string {
  return formatSmartNumber(riskScore, true);
}

/**
 * Formats a probability (0-1 range) as a percentage with smart decimal places
 * 
 * @param probability - Probability value between 0 and 1
 * @returns Formatted percentage string
 */
export function formatProbability(probability: number): string {
  return formatSmartNumber(probability, true);
}

/**
 * Formats a decimal score (0-1 range) as a percentage with smart decimal places
 * 
 * @param score - Score value between 0 and 1
 * @returns Formatted percentage string
 */
export function formatScore(score: number): string {
  return formatSmartNumber(score, true);
}