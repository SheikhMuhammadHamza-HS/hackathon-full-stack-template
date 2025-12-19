/**
 * AuthForm Component
 *
 * Reusable authentication form container with consistent styling.
 * Provides a clean, accessible form layout with header and footer slots.
 * Features a modern, clean design with improved visual hierarchy and interactions.
 *
 * @example
 * <AuthForm
 *   title="Sign Up"
 *   description="Create your account"
 *   onSubmit={handleSubmit}
 * >
 *   <InputField />
 *   <Button type="submit">Submit</Button>
 * </AuthForm>
 */

'use client';

import { FormHTMLAttributes, ReactNode } from 'react';
import Link from 'next/link';

interface AuthFormProps extends Omit<FormHTMLAttributes<HTMLFormElement>, 'className'> {
  /** Form title displayed at the top */
  title: string;
  /** Optional description text below title */
  description?: string;
  /** Form content (inputs, buttons, etc.) */
  children: ReactNode;
  /** Optional footer content (links, additional text) */
  footer?: ReactNode;
  /** Optional back link */
  backLink?: { href: string; label: string };
}

/**
 * Authentication form container with consistent styling
 * Handles responsive layout and accessibility
 */
export function AuthForm({
  title,
  description,
  children,
  footer,
  backLink,
  ...formProps
}: AuthFormProps) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 transition-colors duration-300">
      <div className="w-full max-w-md space-y-8">
        {/* Form Header */}
        <div className="text-center">
          {backLink && (
            <Link
              href={backLink.href}
              className="
                inline-flex
                items-center
                gap-2
                mb-6
                text-sm
                font-medium
                text-gray-400
                hover:text-white
                transition-colors
              "
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              {backLink.label}
            </Link>
          )}
          <div className="flex justify-center mb-6">
            <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </div>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            {title}
          </h1>
          {description && (
            <p className="mt-2 text-sm text-gray-400">
              {description}
            </p>
          )}
        </div>

        {/* Form Card */}
        <div
          className="
            bg-white/5
            backdrop-blur-xl
            rounded-xl
            border
            border-white/10
            p-8
            shadow-2xl
            transition-all
            duration-300
          "
        >
          <form className="space-y-6" {...formProps}>
            {children}
          </form>
        </div>

        {/* Footer */}
        {footer && (
          <div className="text-center text-sm text-gray-400">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Input Field Component
 * Reusable form input with label, error handling, and accessibility
 */
interface InputFieldProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'className'> {
  label: string;
  error?: string | null;
  helperText?: string;
}

export function InputField({
  label,
  error,
  helperText,
  id,
  required,
  ...inputProps
}: InputFieldProps) {
  const inputId = id || `input-${label.toLowerCase().replace(/\s+/g, '-')}`;
  const hasError = !!error;

  return (
    <div>
      <label
        htmlFor={inputId}
        className="
          block
          text-sm
          font-medium
          text-gray-900
          dark:text-gray-100
          mb-2
        "
      >
        {label}
        {required && (
          <span className="text-red-500 ml-1" aria-label="required">
            *
          </span>
        )}
      </label>
      <input
        id={inputId}
        aria-invalid={hasError}
        aria-describedby={
          hasError
            ? `${inputId}-error`
            : helperText
              ? `${inputId}-helper`
              : undefined
        }
        className={`
          block
          w-full
          px-4
          py-3
          text-base
          rounded-lg
          border
          transition-all
          duration-200
          shadow-sm
          focus:shadow-md
          ${hasError
            ? 'border-red-500 dark:border-red-500 focus:border-red-500 focus:ring-red-500'
            : 'border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500'
          }
          bg-white
          dark:bg-gray-900
          text-gray-900
          dark:text-gray-100
          placeholder:text-gray-400
          dark:placeholder:text-gray-500
          focus:outline-none
          focus:ring-2
          focus:ring-offset-0
          disabled:opacity-50
          disabled:cursor-not-allowed
        `}
        {...inputProps}
      />
      {helperText && !error && (
        <p
          id={`${inputId}-helper`}
          className="mt-2 text-sm text-gray-600 dark:text-gray-400"
        >
          {helperText}
        </p>
      )}
      {error && (
        <p
          id={`${inputId}-error`}
          role="alert"
          aria-live="polite"
          className="mt-2 text-sm text-red-600 dark:text-red-400 flex items-start gap-1"
        >
          <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}

/**
 * Submit Button Component
 * Primary button for form submissions with loading state
 */
interface SubmitButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'className'> {
  isLoading?: boolean;
  loadingText?: string;
  children: ReactNode;
}

export function SubmitButton({
  isLoading = false,
  loadingText = 'Loading...',
  children,
  disabled,
  ...buttonProps
}: SubmitButtonProps) {
  return (
    <button
      type="submit"
      disabled={disabled || isLoading}
      className={`
        w-full
        flex
        items-center
        justify-center
        gap-2
        px-4
        py-3
        text-sm
        font-medium
        text-white
        dark:text-black
        bg-black
        hover:bg-gray-800
        dark:bg-white
        dark:hover:bg-gray-200
        disabled:bg-gray-400
        disabled:cursor-not-allowed
        rounded-lg
        transition-all
        duration-200
        focus:outline-none
        focus:ring-2
        focus:ring-gray-900
        dark:focus:ring-white
        focus:ring-offset-2
        dark:focus:ring-offset-black
        min-h-[48px]
        shadow-sm
        hover:shadow-md
      `}
      {...buttonProps}
    >
      {isLoading ? (
        <>
          <svg
            className="w-5 h-5 animate-spin"
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
          <span>{loadingText}</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}