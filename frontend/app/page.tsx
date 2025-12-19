'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ThemeToggle';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('auth_token');

    if (token) {
      // Redirect to dashboard if logged in
      router.push('/dashboard');
    }
    // If not logged in, show the hero page
  }, [router]);

  return (
    <div className="flex flex-col min-h-screen bg-transparent text-gray-100 transition-colors duration-300">
      {/* Navbar */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-gray-200 dark:border-gray-800 backdrop-blur-sm sticky top-0 z-50 bg-white/80 dark:bg-black/80">
        <div className="flex items-center gap-2">
          <div className="bg-indigo-600 p-2 rounded-lg">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <span className="text-xl font-bold tracking-tight">TodoPro</span>
        </div>
        <div className="flex gap-4 items-center">
          <ThemeToggle />
          <Link href="/auth/signin" className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors">
            Sign In
          </Link>
          <Link href="/auth/signup" className="text-sm font-medium bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-all">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 py-20 bg-gradient-to-b from-white to-gray-50 dark:from-black dark:to-gray-900">
        <div className="max-w-4xl space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 text-sm font-medium border border-gray-200 dark:border-gray-700">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            v1.0 is now live
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-balance leading-tight text-gray-900 dark:text-white">
            Manage your tasks with <span className="text-indigo-600 italic">professional</span> efficiency.
          </h1>

          <p className="text-lg md:text-xl text-gray-500 dark:text-gray-400 max-w-2xl mx-auto text-balance">
            The ultimate platform for modern teams to collaborate, track progress, and achieve goals without the clutter.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link href="/auth/signup" className="h-12 px-8 rounded-lg bg-indigo-600 text-white font-semibold flex items-center justify-center hover:bg-indigo-700 transition-all shadow-lg hover:shadow-indigo-500/25 min-w-[200px]">
              Start for free
            </Link>
            <Link href="https://github.com/SheikhMuhammadHamza-HS/hackathon-full-stack-template" target="_blank" className="h-12 px-8 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-900 dark:text-white font-medium flex items-center justify-center transition-all min-w-[200px]">
              View on GitHub
            </Link>
          </div>

          {/* Social Proof / Stats */}
          <div className="pt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-center border-t border-gray-200 dark:border-gray-800 mt-16 max-w-3xl mx-auto">
            <div>
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white">10k+</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wider font-medium mt-1">Active Users</p>
            </div>
            <div>
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white">99.9%</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wider font-medium mt-1">Uptime</p>
            </div>
            <div>
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white">24/7</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wider font-medium mt-1">Support</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
