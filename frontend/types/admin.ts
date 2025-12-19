/**
 * Admin API types
 *
 * Type definitions for admin-specific API endpoints including user management
 * and database statistics.
 */

/**
 * User information returned by admin endpoints
 */
export interface AdminUser {
  id: string;
  name: string;
  email: string;
  created_at: string;
  is_admin: boolean;
}

/**
 * User with task count for statistics
 */
export interface AdminUserStats {
  name: string;
  email: string;
  task_count: number;
}

/**
 * Database statistics returned by admin/stats endpoint
 */
export interface AdminStats {
  total_users: number;
  total_tasks: number;
  users: AdminUserStats[];
}

/**
 * Response from user deletion endpoint
 */
export interface DeleteUserResponse {
  message: string;
}

/**
 * Response from admin/users endpoint
 */
export interface AdminUsersResponse {
  users: AdminUser[];
}
