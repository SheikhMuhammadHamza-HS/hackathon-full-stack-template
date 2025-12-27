/**
 * Task type definitions
 *
 * Matches backend Task model schema for type safety across frontend.
 */

/**
 * Task priority levels
 */
export type TaskPriority = 'low' | 'medium' | 'high';

/**
 * Recurring task intervals
 */
export type RecurringInterval = 'daily' | 'weekly' | 'monthly';

/**
 * Task entity as returned from API
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: TaskPriority;
  tags: string[] | null;
  due_date: string | null;
  is_recurring: boolean;
  recurring_interval: RecurringInterval | null;
  created_at: string;
  updated_at: string;
}

/**
 * Payload for creating a new task
 */
export interface CreateTaskPayload {
  title: string;
  description?: string;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string;
  is_recurring?: boolean;
  recurring_interval?: RecurringInterval;
}

/**
 * Payload for updating an existing task
 */
export interface UpdateTaskPayload {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string;
  is_recurring?: boolean;
  recurring_interval?: RecurringInterval;
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
