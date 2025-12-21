/**
 * OAuth Callback Page
 *
 * Handles OAuth redirects from Google and GitHub.
 * Extracts token from URL, stores it, and redirects to dashboard.
 */

'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function OAuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Get token and provider from URL params
    const token = searchParams.get('token');
    const provider = searchParams.get('provider');

    if (token) {
      // Store token in localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', token);
        console.log(`✅ Successfully authenticated with ${provider || 'OAuth'}`);
      }

      // Redirect to dashboard
      router.push('/dashboard');
    } else {
      // No token - redirect to signin with error
      console.error('❌ No token received from OAuth callback');
      router.push('/auth/signin?error=oauth_failed');
    }
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600 dark:text-gray-400">
          Completing authentication...
        </p>
      </div>
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Loading...
          </p>
        </div>
      </div>
    }>
      <OAuthCallbackContent />
    </Suspense>
  );
}
