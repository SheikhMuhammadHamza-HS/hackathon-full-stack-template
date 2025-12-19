/**
 * Task type definitions
 *
 * Matches backend Task model schema for type safety across frontend.
 */

/**
 * Task entity as returned from API
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Payload for creating a new task
 */
export interface CreateTaskPayload {
  title: string;
  description?: string;
}

/**
 * Payload for updating an existing task
 */
export interface UpdateTaskPayload {
  title?: string;
  description?: string;
  completed?: boolean;
}

/**
 * API response for task operations
 */
export interface TaskResponse {
  task: Task;
}

/**
 * API response for listing tasks
 */
export interface TaskListResponse {
  tasks: Task[];
}
