/**
 * Dashboard Page
 *
 * Protected landing page displayed after successful authentication.
 * Shows user information, task management, and sign-out functionality.
 * Features a modern, clean design with improved visual hierarchy and interactions.
 *
 * Features:
 * - JWT token validation and auto-redirect if unauthenticated
 * - User profile display (name, email)
 * - Task management (list, create, update, delete, toggle complete)
 * - Sign out with localStorage cleanup
 * - Responsive layout with dark mode support
 * - Loading and error states for better UX
 * - Optimistic UI updates for tasks
 * - Accessible navigation and actions
 * - Modern UI with enhanced visual design and interactions
 *
 * Security:
 * - Client-side route protection (redirects if no token)
 * - Token expiration checking
 * - User-scoped task operations (user_id from JWT)
 * - Secure sign-out flow
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser, clearAuthToken, type JWTPayload } from '@/lib/auth';
import { api } from '@/lib/api-client';
import { Task, CreateTaskPayload, UpdateTaskPayload } from '@/types/task';
import { TaskList } from '@/components/TaskList';
import { AddTaskForm } from '@/components/AddTaskForm';

/**
 * Dashboard page component with modern UI design
 */
export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<JWTPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSigningOut, setIsSigningOut] = useState(false);

  // Task management state
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [tasksError, setTasksError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  /**
   * Check authentication status on mount
   * Redirect to signin if no valid token
   */
  useEffect(() => {
    const currentUser = getCurrentUser();

    if (!currentUser) {
      // No valid token - redirect to signin
      router.push('/auth/signin');
      return;
    }

    setUser(currentUser);
    setIsLoading(false);

    // Load tasks after authentication is confirmed
    loadTasks(currentUser.user_id);
  }, [router]);

  /**
   * Load tasks from backend
   */
  const loadTasks = async (userId: string) => {
    setIsLoadingTasks(true);
    setTasksError(null);

    try {
      const response = await api.get<Task[]>(`/api/${userId}/tasks`);
      // Backend returns Task[] directly, filter out any null/undefined tasks
      const filteredTasks = Array.isArray(response)
        ? response.filter(task => task != null)
        : [];
      setTasks(filteredTasks);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      setTasksError(error instanceof Error ? error.message : 'Failed to load tasks');
    } finally {
      setIsLoadingTasks(false);
    }
  };

  /**
   * Create a new task
   */
  const handleCreateTask = async (data: CreateTaskPayload) => {
    if (!user) return;

    try {
      const response = await api.post<Task>(
        `/api/${user.user_id}/tasks`,
        data
      );

      // Add new task to the beginning of the list (optimistic UI)
      if (response) {
        setTasks((prev) => [response, ...(prev || [])]);
      }

      // Hide form
      setShowAddForm(false);
    } catch (error) {
      console.error('Failed to create task:', error);
      throw error; // Re-throw to let form handle the error
    }
  };

  /**
   * Toggle task completion
   */
  const handleToggleComplete = async (taskId: number, completed: boolean) => {
    if (!user) return;

    // Optimistic update
    setTasks((prev) =>
      (prev || [])
        .filter(task => task != null) // Filter out any null/undefined tasks
        .map((task) =>
          task.id === taskId ? { ...task, completed } : task
        )
    );

    try {
      await api.post(`/api/${user.user_id}/tasks/${taskId}/complete`);
    } catch (error) {
      console.error('Failed to toggle task:', error);

      // Revert on error
      setTasks((prev) =>
        (prev || [])
          .filter(task => task != null) // Filter out any null/undefined tasks
          .map((task) =>
            task.id === taskId ? { ...task, completed: !completed } : task
          )
      );

      throw error;
    }
  };

  /**
   * Update task
   */
  const handleUpdateTask = async (taskId: number, data: UpdateTaskPayload) => {
    if (!user) return;

    // Store old task for rollback
    const oldTask = tasks.filter(task => task != null).find((t) => t.id === taskId);

    // Optimistic update
    setTasks((prev) =>
      (prev || [])
        .filter(task => task != null) // Filter out any null/undefined tasks
        .map((task) =>
          task.id === taskId
            ? { ...task, ...data, updated_at: new Date().toISOString() }
            : task
        )
    );

    try {
      await api.patch(`/api/${user.user_id}/tasks/${taskId}`, data);
    } catch (error) {
      console.error('Failed to update task:', error);

      // Revert on error
      if (oldTask) {
        setTasks((prev) =>
          (prev || [])
            .filter(task => task != null) // Filter out any null/undefined tasks
            .map((task) => (task.id === taskId ? oldTask : task))
        );
      }

      throw error;
    }
  };

  /**
   * Delete task
   */
  const handleDeleteTask = async (taskId: number) => {
    if (!user) return;

    // Store old task for rollback
    const oldTask = tasks.filter(task => task != null).find((t) => t.id === taskId);

    // Optimistic update
    setTasks((prev) =>
      (prev || [])
        .filter(task => task != null) // Filter out any null/undefined tasks
        .filter((task) => task.id !== taskId)
    );

    try {
      await api.delete(`/api/${user.user_id}/tasks/${taskId}`);
    } catch (error) {
      console.error('Failed to delete task:', error);

      // Revert on error
      if (oldTask) {
        setTasks((prev) => [
          ...(prev || []).filter(task => task != null), // Filter out any null/undefined tasks
          oldTask
        ]);
      }

      throw error;
    }
  };

  /**
   * Handle sign out
   * - Remove token from localStorage
   * - Redirect to signin page
   */
  const handleSignOut = () => {
    setIsSigningOut(true);

    // Clear authentication token
    clearAuthToken();

    // Optional: Show confirmation message
    // Could be implemented with toast notification

    // Redirect to signin page
    router.push('/auth/signin');
  };

  /**
   * Loading state
   */
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div
            className="
              inline-block
              w-12
              h-12
              border-4
              border-blue-600
              border-t-transparent
              rounded-full
              animate-spin
            "
            role="status"
            aria-label="Loading dashboard"
          />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  /**
   * No user state (should not happen due to redirect)
   */
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-transparent transition-colors duration-300">
      {/* Header */}
      <header
        className="
          bg-white/5
          backdrop-blur-xl
          border-b
          border-white/10
          sticky
          top-0
          z-50
        "
      >
        <div
          className="
            max-w-7xl
            mx-auto
            px-4
            sm:px-6
            lg:px-8
            py-4
            flex
            items-center
            justify-between
          "
        >
          <div className="flex items-center space-x-4">
            <div className="bg-white/10 backdrop-blur-sm p-2 rounded-lg border border-white/20">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              TodoPro
            </h1>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center gap-3">
            {/* AI Chat Button */}
            <button
              onClick={() => router.push('/chat')}
              className="
                px-4
                py-2
                text-sm
                font-medium
                text-cyan-300
                hover:text-cyan-200
                border
                border-cyan-500/30
                hover:bg-cyan-500/10
                rounded-lg
                transition-all
                duration-200
                focus:outline-none
                focus:ring-2
                focus:ring-cyan-500/50
                flex
                items-center
                gap-2
              "
              aria-label="Open AI chat assistant"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
              <span className="hidden sm:inline">AI Chat</span>
            </button>

            {/* Admin Panel Link - Only show for admin users */}
            {user?.email === 'sheikhmhamza37@gmail.com' && (
              <button
                onClick={() => router.push('/admin')}
                className="
                  px-4
                  py-2
                  text-sm
                  font-medium
                  text-purple-300
                  hover:text-purple-200
                  border
                  border-purple-500/30
                  hover:bg-purple-500/10
                  rounded-lg
                  transition-all
                  duration-200
                  focus:outline-none
                  focus:ring-2
                  focus:ring-purple-500/50
                  flex
                  items-center
                  gap-2
                "
                aria-label="Go to admin panel"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <span className="hidden sm:inline">Admin Panel</span>
              </button>
            )}

            {/* Sign Out Button */}
            <button
              onClick={handleSignOut}
              disabled={isSigningOut}
              className="
                px-4
                py-2
                text-sm
                font-medium
                text-gray-300
                hover:text-white
                border
                border-white/20
                hover:bg-white/10
                rounded-lg
                transition-all
                duration-200
                focus:outline-none
                focus:ring-2
                focus:ring-white/50
                disabled:opacity-50
                disabled:cursor-not-allowed
              "
              aria-label="Sign out of account"
            >
              {isSigningOut ? 'Signing Out...' : 'Sign Out'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-2">
            Welcome back, {user.name}
          </h2>
          <p className="text-gray-300">
            Manage your daily tasks with focus and clarity.
          </p>
        </div>

        {/* User Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {/* Name Card */}
          <div className="p-6 rounded-xl border border-white/20 bg-white/5 backdrop-blur-xl hover:border-white/40 hover:bg-white/10 transition-all duration-300 shadow-xl">
            <p className="text-sm font-medium text-gray-400 mb-1">Full Name</p>
            <p className="text-lg font-semibold text-white">{user.name}</p>
          </div>

          {/* Email Card */}
          <div className="p-6 rounded-xl border border-white/20 bg-white/5 backdrop-blur-xl hover:border-white/40 hover:bg-white/10 transition-all duration-300 shadow-xl">
            <p className="text-sm font-medium text-gray-400 mb-1">Email Address</p>
            <p className="text-lg font-semibold text-white break-all">{user.email}</p>
          </div>

          {/* Tasks Count Card */}
          <div className="p-6 rounded-xl border border-white/20 bg-white/5 backdrop-blur-xl hover:border-white/40 hover:bg-white/10 transition-all duration-300 shadow-xl">
            <p className="text-sm font-medium text-gray-400 mb-1">Total Tasks</p>
            <p className="text-4xl font-bold text-white">{tasks.length}</p>
          </div>
        </div>

        {/* Task Management Section */}
        <section>
          {/* Section Header */}
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4 border-b border-white/20 pb-6">
            <div>
              <h3 className="text-2xl font-bold text-white">
                Your Tasks
              </h3>
            </div>

            {/* Add Task Button */}
            {!showAddForm && (
              <button
                onClick={() => setShowAddForm(true)}
                className="
                  px-5
                  py-2.5
                  text-sm
                  font-medium
                  text-white
                  bg-white/10
                  backdrop-blur-sm
                  border
                  border-white/20
                  hover:bg-white/20
                  rounded-full
                  transition-all
                  duration-200
                  focus:outline-none
                  focus:ring-2
                  focus:ring-white/50
                  flex
                  items-center
                  gap-2
                  shadow-lg
                  hover:shadow-xl
                "
                aria-label="Add new task"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                <span>Add New Task</span>
              </button>
            )}
          </div>

          {/* Add Task Form */}
          {showAddForm && (
            <div className="mb-8 p-6 border border-white/20 rounded-xl bg-white/5 backdrop-blur-xl shadow-2xl max-h-[80vh] overflow-y-auto">
              <AddTaskForm
                onSubmit={handleCreateTask}
                onCancel={() => setShowAddForm(false)}
              />
            </div>
          )}

          {/* Task List */}
          <TaskList
            tasks={tasks}
            isLoading={isLoadingTasks}
            error={tasksError}
            onToggleComplete={handleToggleComplete}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteTask}
            onRetry={() => user && loadTasks(user.user_id)}
          />
        </section>
      </main>

      {/* Footer */}
      <footer
        className="
          max-w-7xl
          mx-auto
          px-4
          sm:px-6
          lg:px-8
          py-8
          text-center
          text-sm
          text-gray-400
          border-t
          border-white/10
          mt-12
        "
      >
        <p>Hackathon Todo Application - Phase II: User Authentication</p>
        <p className="mt-1">© {new Date().getFullYear()} All rights reserved</p>
      </footer>
    </div>
  );
}