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

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Brand Section */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="bg-indigo-600 p-2 rounded-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <span className="text-xl font-bold text-gray-900 dark:text-white">TodoPro</span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Professional task management for modern teams. Built with Next.js, FastAPI, and PostgreSQL.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Quick Links</h3>
              <ul className="space-y-3">
                <li>
                  <Link href="/auth/signup" className="text-sm text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                    Get Started
                  </Link>
                </li>
                <li>
                  <Link href="/auth/signin" className="text-sm text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                    Sign In
                  </Link>
                </li>
                <li>
                  <Link href="https://github.com/SheikhMuhammadHamza-HS/hackathon-full-stack-template" target="_blank" className="text-sm text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                    Documentation
                  </Link>
                </li>
              </ul>
            </div>

            {/* Social Links */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Connect</h3>
              <div className="flex gap-4">
                {/* LinkedIn */}
                <Link
                  href="https://www.linkedin.com/in/mrhamzasheikh/"
                  target="_blank"
                  className="group"
                  aria-label="LinkedIn Profile"
                >
                  <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center group-hover:bg-[#0077B5] transition-colors duration-200">
                    <svg className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-white transition-colors" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                  </div>
                </Link>

                {/* X (Twitter) */}
                <Link
                  href="https://x.com/HamzaSheikh8866"
                  target="_blank"
                  className="group"
                  aria-label="X Profile"
                >
                  <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center group-hover:bg-black dark:group-hover:bg-white transition-colors duration-200">
                    <svg className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-white dark:group-hover:text-black transition-colors" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                  </div>
                </Link>

                {/* GitHub */}
                <Link
                  href="https://github.com/SheikhMuhammadHamza-HS"
                  target="_blank"
                  className="group"
                  aria-label="GitHub Profile"
                >
                  <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center group-hover:bg-gray-900 dark:group-hover:bg-white transition-colors duration-200">
                    <svg className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-white dark:group-hover:text-black transition-colors" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                  </div>
                </Link>
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-800">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                © {new Date().getFullYear()} TodoPro. Built with ❤️ by{' '}
                <Link
                  href="https://www.linkedin.com/in/mrhamzasheikh/"
                  target="_blank"
                  className="text-indigo-600 dark:text-indigo-400 hover:underline"
                >
                  Hamza Sheikh
                </Link>
              </p>
              <div className="flex items-center gap-6 text-sm">
                <Link href="https://github.com/SheikhMuhammadHamza-HS/hackathon-full-stack-template" target="_blank" className="text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                  GitHub
                </Link>
                <span className="text-gray-300 dark:text-gray-700">•</span>
                <span className="text-gray-600 dark:text-gray-400">
                  Hackathon II Project
                </span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
