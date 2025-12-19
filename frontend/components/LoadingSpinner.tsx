/**
 * LoadingSpinner Component
 *
 * A reusable loading spinner component with different sizes.
 * Features a modern, clean design that matches the application's style.
 * Uses SVG for better accessibility and performance.
 *
 * Features:
 * - Different size options (sm, md, lg)
 * - Customizable color
 * - Accessible with proper ARIA attributes
 * - Smooth animation
 * - Responsive design
 *
 * @example
 * <LoadingSpinner size="md" className="text-blue-600" />
 */

import React from 'react';

interface LoadingSpinnerProps {
  /** Size of the spinner */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
}

export function LoadingSpinner({ size = 'md', className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <svg
      className={`${sizeClasses[size]} animate-spin ${className}`}
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}