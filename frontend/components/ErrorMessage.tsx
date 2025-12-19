/**
 * ErrorMessage Component
 *
 * Displays validation and server errors with proper ARIA attributes.
 * Automatically associated with form fields via htmlFor prop.
 *
 * @example
 * <ErrorMessage message="Email is required" />
 * <ErrorMessage message={error} htmlFor="email-input" />
 */

import { HTMLAttributes } from 'react';

interface ErrorMessageProps extends HTMLAttributes<HTMLDivElement> {
  /** Error message to display */
  message?: string | null;
  /** ID of associated form field for accessibility */
  htmlFor?: string;
}

/**
 * Error message component for form validation
 * Only renders when message is provided
 */
export function ErrorMessage({
  message,
  htmlFor,
  className = '',
  ...props
}: ErrorMessageProps) {
  if (!message) return null;

  return (
    <div
      role="alert"
      aria-live="polite"
      id={htmlFor ? `${htmlFor}-error` : undefined}
      className={`
        mt-1.5
        text-sm
        text-red-600
        dark:text-red-400
        ${className}
      `}
      {...props}
    >
      {message}
    </div>
  );
}
