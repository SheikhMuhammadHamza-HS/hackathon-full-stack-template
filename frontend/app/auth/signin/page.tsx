/**
 * Signin Page
 *
 * User authentication page for existing users.
 * Handles login flow, token storage, and dashboard redirection.
 *
 * Features:
 * - Client-side form validation (email format, required fields)
 * - Server-side error handling (invalid credentials with generic message)
 * - Loading states with disabled form during submission
 * - Automatic token storage and redirect on success
 * - Accessible form with proper ARIA attributes
 * - Mobile-first responsive design
 */

'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { AuthForm, InputField, SubmitButton } from '@/components/AuthForm';
import { api } from '@/lib/api-client';

/**
 * Signin API response type
 */
interface SigninResponse {
  user: {
    id: string;
    email: string;
    name: string;
    created_at: string;
    updated_at: string;
  };
  token: string;
}

/**
 * Form validation errors
 */
interface ValidationErrors {
  email?: string;
  password?: string;
  general?: string;
}

/**
 * Signin page component
 */
export default function SigninPage() {
  const router = useRouter();

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<ValidationErrors>({});

  /**
   * Validate form data before submission
   */
  const validateForm = (): boolean => {
    const newErrors: ValidationErrors = {};

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation (only required check, no strength requirements for signin)
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call signin API
      const response = await api.post<SigninResponse>('/api/auth/signin', {
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
      });

      // Store JWT token in localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', response.token);
      }

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      // Handle API errors
      const errorMessage =
        error instanceof Error ? error.message : 'An error occurred during signin';

      // Parse specific error types
      if (
        errorMessage.toLowerCase().includes('unauthorized') ||
        errorMessage.toLowerCase().includes('invalid') ||
        errorMessage.toLowerCase().includes('401')
      ) {
        // Generic message for security (don't reveal which field is wrong)
        setErrors({ general: 'Invalid email or password' });
      } else if (
        errorMessage.toLowerCase().includes('network') ||
        errorMessage.toLowerCase().includes('fetch')
      ) {
        setErrors({ general: 'Unable to connect to server. Please try again.' });
      } else {
        setErrors({ general: errorMessage });
      }
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle input changes
   */
  const handleChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: e.target.value,
    }));

    // Clear field error on change
    if (errors[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  return (
    <AuthForm
      title="Welcome back"
      description="Sign in to your account to continue"
      onSubmit={handleSubmit}
      footer={
        <p>
          Don't have an account?{' '}
          <Link
            href="/auth/signup"
            className="
              font-medium
              text-blue-600
              hover:text-blue-700
              dark:text-blue-400
              dark:hover:text-blue-300
              transition-colors
            "
          >
            Sign up
          </Link>
        </p>
      }
    >
      {/* General Error Message */}
      {errors.general && (
        <div
          role="alert"
          className="
            p-3
            rounded-lg
            bg-red-50
            dark:bg-red-900/20
            border
            border-red-200
            dark:border-red-800
            text-sm
            text-red-800
            dark:text-red-200
          "
        >
          {errors.general}
        </div>
      )}

      {/* Email Field */}
      <InputField
        label="Email Address"
        type="email"
        id="email"
        name="email"
        autoComplete="email"
        placeholder="john@example.com"
        required
        value={formData.email}
        onChange={handleChange('email')}
        error={errors.email}
        disabled={isLoading}
      />

      {/* Password Field */}
      <InputField
        label="Password"
        type="password"
        id="password"
        name="password"
        autoComplete="current-password"
        placeholder="••••••••"
        required
        value={formData.password}
        onChange={handleChange('password')}
        error={errors.password}
        disabled={isLoading}
      />

      {/* Forgot Password Link */}
      <div className="flex items-center justify-end">
        <Link
          href="/auth/forgot-password"
          className="
            text-sm
            font-medium
            text-blue-600
            hover:text-blue-700
            dark:text-blue-400
            dark:hover:text-blue-300
            transition-colors
          "
        >
          Forgot password?
        </Link>
      </div>

      {/* Submit Button */}
      <SubmitButton isLoading={isLoading} loadingText="Signing in...">
        Sign In
      </SubmitButton>
    </AuthForm>
  );
}
