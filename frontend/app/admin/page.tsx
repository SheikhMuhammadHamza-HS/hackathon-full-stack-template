/**
 * Admin Panel Page
 *
 * Protected admin-only page for managing users and viewing database statistics.
 * Only accessible to admin users (sheikhmhamza37@gmail.com).
 *
 * Features:
 * - Authentication and authorization checks
 * - User list with task counts
 * - Delete user functionality with confirmation
 * - Database statistics (total users, total tasks)
 * - Responsive design with mobile-friendly layout
 * - Loading and error states
 * - Dark mode support
 *
 * Security:
 * - Client-side admin check (redirects non-admin users)
 * - Backend admin validation on all admin endpoints
 * - JWT token authentication via api-client
 * - Self-deletion prevention (cannot delete own account)
 *
 * API Endpoints:
 * - GET /api/admin/users - List all users
 * - GET /api/admin/stats - Database statistics
 * - DELETE /api/admin/users/{user_id} - Delete user
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser, type JWTPayload } from '@/lib/auth';
import { api } from '@/lib/api-client';
import {
  AdminUser,
  AdminStats,
  AdminUsersResponse,
  DeleteUserResponse,
} from '@/types/admin';

const ADMIN_EMAIL = 'sheikhmhamza37@gmail.com';

/**
 * Admin Panel component
 */
export default function AdminPage() {
  const router = useRouter();
  const [user, setUser] = useState<JWTPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Admin data state
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Delete state
  const [deletingUserId, setDeletingUserId] = useState<string | null>(null);
  const [confirmDeleteUserId, setConfirmDeleteUserId] = useState<string | null>(null);
  const [deleteSuccess, setDeleteSuccess] = useState<string | null>(null);

  /**
   * Check authentication and authorization on mount
   */
  useEffect(() => {
    const currentUser = getCurrentUser();

    if (!currentUser) {
      // Not logged in - redirect to signin
      router.push('/auth/signin');
      return;
    }

    // Check if user is admin
    if (currentUser.email !== ADMIN_EMAIL) {
      // Not admin - show access denied
      setUser(null);
      setIsLoading(false);
      return;
    }

    setUser(currentUser);
    setIsLoading(false);

    // Load admin data
    loadAdminData();
  }, [router]);

  /**
   * Load users and stats from backend
   */
  const loadAdminData = async () => {
    setIsLoadingData(true);
    setError(null);

    try {
      // Fetch users and stats in parallel
      const [usersResponse, statsResponse] = await Promise.all([
        api.get<AdminUser[]>('/api/admin/users'),
        api.get<AdminStats>('/api/admin/stats'),
      ]);

      setUsers(usersResponse);
      setStats(statsResponse);
    } catch (err) {
      console.error('Failed to load admin data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load admin data');
    } finally {
      setIsLoadingData(false);
    }
  };

  /**
   * Handle user deletion with confirmation
   */
  const handleDeleteUser = async (userId: string, userName: string) => {
    if (!confirmDeleteUserId) {
      // First click - show confirmation
      setConfirmDeleteUserId(userId);
      return;
    }

    if (confirmDeleteUserId !== userId) {
      // Different user clicked
      setConfirmDeleteUserId(userId);
      return;
    }

    // Second click on same user - proceed with deletion
    setDeletingUserId(userId);
    setConfirmDeleteUserId(null);
    setDeleteSuccess(null);
    setError(null);

    try {
      await api.delete<DeleteUserResponse>(`/api/admin/users/${userId}`);

      // Show success message
      setDeleteSuccess(`User "${userName}" deleted successfully`);

      // Reload data after deletion
      await loadAdminData();

      // Clear success message after 5 seconds
      setTimeout(() => setDeleteSuccess(null), 5000);
    } catch (err) {
      console.error('Failed to delete user:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete user');
    } finally {
      setDeletingUserId(null);
    }
  };

  /**
   * Cancel delete confirmation
   */
  const cancelDelete = () => {
    setConfirmDeleteUserId(null);
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
            aria-label="Loading admin panel"
          />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  /**
   * Access denied state
   */
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-transparent">
        <div className="max-w-md w-full mx-4">
          <div
            className="
              p-8
              border
              border-red-500/30
              rounded-xl
              bg-red-500/5
              backdrop-blur-xl
              text-center
            "
          >
            <div className="mb-4 flex justify-center">
              <svg
                className="w-16 h-16 text-red-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Access Denied</h2>
            <p className="text-gray-300 mb-6">
              You do not have permission to access the admin panel.
            </p>
            <button
              onClick={() => router.push('/dashboard')}
              className="
                px-6
                py-2.5
                bg-white/10
                backdrop-blur-sm
                border
                border-white/20
                text-white
                font-medium
                rounded-lg
                hover:bg-white/20
                transition-all
                duration-200
                focus:outline-none
                focus:ring-2
                focus:ring-white/50
              "
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
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
            <div className="bg-purple-500/20 backdrop-blur-sm p-2 rounded-lg border border-purple-500/30">
              <svg
                className="w-6 h-6 text-purple-400"
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
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Admin Panel
            </h1>
          </div>

          <button
            onClick={() => router.push('/dashboard')}
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
            "
          >
            Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* Success Message */}
        {deleteSuccess && (
          <div
            className="
              mb-6
              p-4
              rounded-lg
              bg-green-500/10
              border
              border-green-500/30
              text-green-400
              flex
              items-center
              gap-3
            "
          >
            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span>{deleteSuccess}</span>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div
            className="
              mb-6
              p-4
              rounded-lg
              bg-red-500/10
              border
              border-red-500/30
              text-red-400
              flex
              items-center
              justify-between
              gap-3
            "
          >
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <span>{error}</span>
            </div>
            <button
              onClick={loadAdminData}
              className="
                px-3
                py-1
                text-sm
                bg-red-500/20
                hover:bg-red-500/30
                rounded
                transition-colors
                duration-200
              "
            >
              Retry
            </button>
          </div>
        )}

        {/* Stats Section */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            Database Statistics
          </h2>

          {isLoadingData && !stats ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {[1, 2].map((i) => (
                <div
                  key={i}
                  className="
                    p-6
                    rounded-xl
                    border
                    border-white/20
                    bg-white/5
                    backdrop-blur-xl
                    animate-pulse
                  "
                >
                  <div className="h-4 bg-white/10 rounded w-24 mb-3" />
                  <div className="h-10 bg-white/10 rounded w-16" />
                </div>
              ))}
            </div>
          ) : stats ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Total Users */}
              <div
                className="
                  p-6
                  rounded-xl
                  border
                  border-blue-500/30
                  bg-blue-500/5
                  backdrop-blur-xl
                  hover:border-blue-500/50
                  hover:bg-blue-500/10
                  transition-all
                  duration-300
                "
              >
                <p className="text-sm font-medium text-blue-400 mb-2">Total Users</p>
                <p className="text-4xl font-bold text-white">{stats.total_users}</p>
              </div>

              {/* Total Tasks */}
              <div
                className="
                  p-6
                  rounded-xl
                  border
                  border-purple-500/30
                  bg-purple-500/5
                  backdrop-blur-xl
                  hover:border-purple-500/50
                  hover:bg-purple-500/10
                  transition-all
                  duration-300
                "
              >
                <p className="text-sm font-medium text-purple-400 mb-2">Total Tasks</p>
                <p className="text-4xl font-bold text-white">{stats.total_tasks}</p>
              </div>
            </div>
          ) : null}
        </div>

        {/* Users Section */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
            All Users ({users.length})
          </h2>

          {isLoadingData && users.length === 0 ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="
                    p-6
                    rounded-xl
                    border
                    border-white/20
                    bg-white/5
                    backdrop-blur-xl
                    animate-pulse
                  "
                >
                  <div className="flex items-center justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="h-4 bg-white/10 rounded w-48" />
                      <div className="h-3 bg-white/10 rounded w-64" />
                    </div>
                    <div className="h-10 bg-white/10 rounded w-20" />
                  </div>
                </div>
              ))}
            </div>
          ) : users.length === 0 ? (
            <div
              className="
                p-12
                rounded-xl
                border
                border-white/20
                bg-white/5
                backdrop-blur-xl
                text-center
              "
            >
              <p className="text-gray-400">No users found</p>
            </div>
          ) : (
            <>
              {/* Desktop Table View */}
              <div className="hidden lg:block overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/20">
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Created
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Tasks
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {users.map((adminUser) => {
                      const isCurrentUser = adminUser.id === user.user_id;
                      const isDeleting = deletingUserId === adminUser.id;
                      const isConfirming = confirmDeleteUserId === adminUser.id;
                      const userStats = stats?.users.find(
                        (u) => u.email === adminUser.email
                      );

                      return (
                        <tr
                          key={adminUser.id}
                          className="
                            bg-white/5
                            hover:bg-white/10
                            transition-colors
                            duration-200
                          "
                        >
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className="font-medium text-white">
                                {adminUser.name}
                              </span>
                              {isCurrentUser && (
                                <span className="ml-2 px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded border border-purple-500/30">
                                  You
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-gray-300">{adminUser.email}</span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-gray-400 text-sm">
                              {new Date(adminUser.created_at).toLocaleDateString()}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-white font-medium">
                              {userStats?.task_count || 0}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {isCurrentUser ? (
                              <span className="text-gray-500 text-sm">Cannot delete yourself</span>
                            ) : (
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() =>
                                    isConfirming
                                      ? cancelDelete()
                                      : handleDeleteUser(adminUser.id, adminUser.name)
                                  }
                                  disabled={isDeleting}
                                  className={`
                                    px-4
                                    py-2
                                    text-sm
                                    font-medium
                                    rounded-lg
                                    transition-all
                                    duration-200
                                    focus:outline-none
                                    focus:ring-2
                                    disabled:opacity-50
                                    disabled:cursor-not-allowed
                                    ${
                                      isConfirming
                                        ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 hover:bg-yellow-500/30 focus:ring-yellow-500/50'
                                        : 'bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 focus:ring-red-500/50'
                                    }
                                  `}
                                >
                                  {isDeleting
                                    ? 'Deleting...'
                                    : isConfirming
                                    ? 'Cancel'
                                    : 'Delete'}
                                </button>
                                {isConfirming && (
                                  <button
                                    onClick={() =>
                                      handleDeleteUser(adminUser.id, adminUser.name)
                                    }
                                    disabled={isDeleting}
                                    className="
                                      px-4
                                      py-2
                                      text-sm
                                      font-medium
                                      bg-red-600/80
                                      text-white
                                      hover:bg-red-600
                                      rounded-lg
                                      transition-all
                                      duration-200
                                      focus:outline-none
                                      focus:ring-2
                                      focus:ring-red-500/50
                                      disabled:opacity-50
                                      disabled:cursor-not-allowed
                                    "
                                  >
                                    Confirm
                                  </button>
                                )}
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Mobile Card View */}
              <div className="lg:hidden space-y-4">
                {users.map((adminUser) => {
                  const isCurrentUser = adminUser.id === user.user_id;
                  const isDeleting = deletingUserId === adminUser.id;
                  const isConfirming = confirmDeleteUserId === adminUser.id;
                  const userStats = stats?.users.find((u) => u.email === adminUser.email);

                  return (
                    <div
                      key={adminUser.id}
                      className="
                        p-6
                        rounded-xl
                        border
                        border-white/20
                        bg-white/5
                        backdrop-blur-xl
                        hover:border-white/40
                        hover:bg-white/10
                        transition-all
                        duration-300
                      "
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-semibold text-white">
                              {adminUser.name}
                            </h3>
                            {isCurrentUser && (
                              <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded border border-purple-500/30">
                                You
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400">{adminUser.email}</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Created</p>
                          <p className="text-sm text-gray-300">
                            {new Date(adminUser.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Tasks</p>
                          <p className="text-sm text-white font-medium">
                            {userStats?.task_count || 0}
                          </p>
                        </div>
                      </div>

                      {!isCurrentUser && (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() =>
                              isConfirming
                                ? cancelDelete()
                                : handleDeleteUser(adminUser.id, adminUser.name)
                            }
                            disabled={isDeleting}
                            className={`
                              flex-1
                              px-4
                              py-2
                              text-sm
                              font-medium
                              rounded-lg
                              transition-all
                              duration-200
                              focus:outline-none
                              focus:ring-2
                              disabled:opacity-50
                              disabled:cursor-not-allowed
                              ${
                                isConfirming
                                  ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 hover:bg-yellow-500/30 focus:ring-yellow-500/50'
                                  : 'bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 focus:ring-red-500/50'
                              }
                            `}
                          >
                            {isDeleting ? 'Deleting...' : isConfirming ? 'Cancel' : 'Delete'}
                          </button>
                          {isConfirming && (
                            <button
                              onClick={() => handleDeleteUser(adminUser.id, adminUser.name)}
                              disabled={isDeleting}
                              className="
                                flex-1
                                px-4
                                py-2
                                text-sm
                                font-medium
                                bg-red-600/80
                                text-white
                                hover:bg-red-600
                                rounded-lg
                                transition-all
                                duration-200
                                focus:outline-none
                                focus:ring-2
                                focus:ring-red-500/50
                                disabled:opacity-50
                                disabled:cursor-not-allowed
                              "
                            >
                              Confirm Delete
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
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
        <p>Admin Panel - User Management</p>
      </footer>
    </div>
  );
}
