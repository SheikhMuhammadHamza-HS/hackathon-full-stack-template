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

  /**
   * Handle Google OAuth login
   */
  const handleGoogleLogin = () => {
    // Use placeholder for Docker runtime injection, or env var for local dev
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'RUNTIME_API_URL_PLACEHOLDER';
    window.location.href = `${apiUrl}/api/auth/google/login`;
  };

  /**
   * Handle GitHub OAuth login
   */
  const handleGitHubLogin = () => {
    // Use placeholder for Docker runtime injection, or env var for local dev
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'RUNTIME_API_URL_PLACEHOLDER';
    window.location.href = `${apiUrl}/api/auth/github/login`;
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

      {/* Social Sign In */}
      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300 dark:border-gray-700"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
              Or continue with
            </span>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="
              w-full
              inline-flex
              justify-center
              py-2.5
              px-4
              border
              border-gray-300
              dark:border-gray-600
              rounded-lg
              shadow-sm
              bg-white
              dark:bg-gray-700
              text-sm
              font-medium
              text-gray-700
              dark:text-gray-300
              hover:bg-gray-50
              dark:hover:bg-gray-600
              transition-colors
              duration-200
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
              focus:ring-offset-2
              dark:focus:ring-offset-gray-800
            "
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            <span className="ml-2">Google</span>
          </button>

          <button
            type="button"
            onClick={handleGitHubLogin}
            className="
              w-full
              inline-flex
              justify-center
              py-2.5
              px-4
              border
              border-gray-300
              dark:border-gray-600
              rounded-lg
              shadow-sm
              bg-white
              dark:bg-gray-700
              text-sm
              font-medium
              text-gray-700
              dark:text-gray-300
              hover:bg-gray-50
              dark:hover:bg-gray-600
              transition-colors
              duration-200
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
              focus:ring-offset-2
              dark:focus:ring-offset-gray-800
            "
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            <span className="ml-2">GitHub</span>
          </button>
        </div>
      </div>
    </AuthForm>
  );
}
