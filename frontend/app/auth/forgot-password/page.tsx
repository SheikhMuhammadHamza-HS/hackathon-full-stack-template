'use client';

import Link from 'next/link';

export default function ForgotPasswordPage() {
    return (
        <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50 dark:bg-gray-900">
            <div className="w-full max-w-md space-y-8 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-lg text-center">
                <h2 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Forgot Password?</h2>
                <p className="text-gray-600 dark:text-gray-400">
                    This feature is currently under development. Please contact support if you need assistance.
                </p>
                <Link
                    href="/auth/signin"
                    className="inline-flex items-center justify-center w-full px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
                >
                    <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    Back to Sign In
                </Link>
            </div>
        </div>
    );
}
