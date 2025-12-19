/**
 * TaskList Component
 *
 * Displays a list of tasks with filtering, sorting, and management capabilities.
 * Features a modern, clean design with improved visual hierarchy and interactions.
 *
 * Features:
 * - Displays all tasks in a vertical list
 * - Sort by creation date (newest first)
 * - Toggle task completion
 * - Edit task (shows inline edit form)
 * - Delete task with confirmation
 * - Empty state when no tasks
 * - Loading state during data fetch
 * - Error handling with retry option
 * - Optimistic UI updates for better UX
 * - Responsive design
 * - Modern UI with enhanced visual design and interactions
 *
 * @example
 * <TaskList
 *   tasks={tasks}
 *   isLoading={isLoading}
 *   error={error}
 *   onToggleComplete={handleToggle}
 *   onUpdate={handleUpdate}
 *   onDelete={handleDelete}
 *   onRetry={handleRetry}
 * />
 */

'use client';

import { useState } from 'react';
import { Task, UpdateTaskPayload } from '@/types/task';
import { TaskItem } from './TaskItem';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';

interface TaskListProps {
  /** Array of tasks to display */
  tasks: Task[];
  /** Loading state */
  isLoading?: boolean;
  /** Error message if fetch failed */
  error?: string | null;
  /** Callback when task completion is toggled */
  onToggleComplete: (taskId: number, completed: boolean) => Promise<void>;
  /** Callback when task is updated */
  onUpdate: (taskId: number, data: UpdateTaskPayload) => Promise<void>;
  /** Callback when task is deleted */
  onDelete: (taskId: number) => Promise<void>;
  /** Callback to retry loading tasks */
  onRetry?: () => void;
}

/**
 * Task list component with sorting and management
 */
export function TaskList({
  tasks,
  isLoading = false,
  error = null,
  onToggleComplete,
  onUpdate,
  onDelete,
  onRetry,
}: TaskListProps) {
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editErrors, setEditErrors] = useState<{ title?: string }>({});
  const [isUpdating, setIsUpdating] = useState(false);

  /**
   * Sort tasks by creation date (newest first)
   */
  const sortedTasks = (tasks || [])
    .filter(task => task != null) // Filter out null/undefined tasks first
    .slice()
    .sort((a, b) => {
      // Ensure both a and b exist and have created_at property
      if (!a?.created_at || !b?.created_at) return 0;
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });

  /**
   * Handle edit button click
   */
  const handleEdit = (task: Task) => {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setEditErrors({});
  };

  /**
   * Handle cancel edit
   */
  const handleCancelEdit = () => {
    setEditingTaskId(null);
    setEditTitle('');
    setEditDescription('');
    setEditErrors({});
  };

  /**
   * Handle save edit
   */
  const handleSaveEdit = async (taskId: number) => {
    // Validate
    if (!editTitle.trim()) {
      setEditErrors({ title: 'Title is required' });
      return;
    }

    if (editTitle.length > 200) {
      setEditErrors({ title: 'Title must be 200 characters or less' });
      return;
    }

    // Update
    setIsUpdating(true);
    try {
      await onUpdate(taskId, {
        title: editTitle.trim(),
        description: editDescription.trim() || undefined,
      });
      handleCancelEdit();
    } catch (error) {
      // Error handling is done in parent component
    } finally {
      setIsUpdating(false);
    }
  };

  /**
   * Loading State
   */
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="mb-4">
          <LoadingSpinner size="lg" className="text-blue-600 dark:text-blue-400" />
        </div>
        <p className="text-gray-600 dark:text-gray-400">Loading your tasks...</p>
      </div>
    );
  }

  /**
   * Error State
   */
  if (error) {
    return (
      <div className="text-center py-16">
        <div
          className="
            inline-flex
            items-center
            justify-center
            w-16
            h-16
            bg-red-100
            dark:bg-red-900/20
            rounded-full
            mb-6
          "
        >
          <svg
            className="w-8 h-8 text-red-600 dark:text-red-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <ErrorMessage message={error} className="justify-center mb-6" />
        {onRetry && (
          <button
            onClick={onRetry}
            className="
              px-4
              py-2.5
              text-sm
              font-medium
              text-white
              bg-gradient-to-r
              from-blue-600
              to-indigo-600
              hover:from-blue-700
              hover:to-indigo-700
              rounded-lg
              transition-all
              duration-200
              focus:outline-none
              focus:ring-2
              focus:ring-blue-500
              focus:ring-offset-2
              dark:focus:ring-offset-gray-900
              shadow-sm
            "
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  /**
   * Empty State
   */
  if (sortedTasks.length === 0) {
    return (
      <div className="text-center py-16">
        <div
          className="
            inline-flex
            items-center
            justify-center
            w-16
            h-16
            bg-gradient-to-br
            from-blue-100
            to-indigo-100
            dark:from-blue-900/30
            dark:to-indigo-900/30
            rounded-full
            mb-6
          "
        >
          <svg
            className="w-8 h-8 text-blue-600 dark:text-blue-400"
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
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No tasks yet</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Get started by creating your first task
        </p>
        <div className="flex justify-center">
          <div className="relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg blur opacity-20"></div>
            <div className="relative bg-white dark:bg-gray-800 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Tasks help you stay organized and productive
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /**
   * Task List
   */
  return (
    <div className="space-y-4">
      {sortedTasks
        .filter(task => task != null) // Filter out null/undefined tasks
        .map((task) => {
        // Show edit form for this task
        if (editingTaskId === task.id) {
          return (
            <div
              key={task.id}
              className="
                bg-gradient-to-br
                from-blue-50
                to-blue-100
                dark:from-blue-900/20
                dark:to-blue-800/20
                border
                border-blue-200
                dark:border-blue-700
                rounded-xl
                p-5
                space-y-4
                shadow-sm
              "
            >
              <div>
                <label
                  htmlFor={`edit-title-${task.id}`}
                  className="
                    block
                    text-sm
                    font-medium
                    text-gray-700
                    dark:text-gray-300
                    mb-2
                  "
                >
                  Title
                </label>
                <input
                  id={`edit-title-${task.id}`}
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  disabled={isUpdating}
                  maxLength={200}
                  className="
                    w-full
                    px-4
                    py-2.5
                    text-gray-900
                    dark:text-white
                    bg-white
                    dark:bg-gray-900
                    border
                    border-gray-300
                    dark:border-gray-600
                    rounded-lg
                    focus:outline-none
                    focus:ring-2
                    focus:ring-blue-500
                    focus:border-transparent
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                    transition-colors
                  "
                  aria-invalid={!!editErrors.title}
                />
                <ErrorMessage message={editErrors.title} htmlFor={`edit-title-${task.id}`} />
              </div>

              <div>
                <label
                  htmlFor={`edit-description-${task.id}`}
                  className="
                    block
                    text-sm
                    font-medium
                    text-gray-700
                    dark:text-gray-300
                    mb-2
                  "
                >
                  Description
                </label>
                <textarea
                  id={`edit-description-${task.id}`}
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  disabled={isUpdating}
                  maxLength={1000}
                  rows={3}
                  className="
                    w-full
                    px-4
                    py-2.5
                    text-gray-900
                    dark:text-white
                    bg-white
                    dark:bg-gray-900
                    border
                    border-gray-300
                    dark:border-gray-600
                    rounded-lg
                    focus:outline-none
                    focus:ring-2
                    focus:ring-blue-500
                    focus:border-transparent
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                    resize-vertical
                    transition-colors
                  "
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  onClick={handleCancelEdit}
                  disabled={isUpdating}
                  className="
                    px-4
                    py-2.5
                    text-sm
                    font-medium
                    text-gray-700
                    dark:text-gray-300
                    bg-white
                    dark:bg-gray-700
                    border
                    border-gray-300
                    dark:border-gray-600
                    hover:bg-gray-50
                    dark:hover:bg-gray-600
                    rounded-lg
                    transition-colors
                    focus:outline-none
                    focus:ring-2
                    focus:ring-gray-500
                    focus:ring-offset-2
                    dark:focus:ring-offset-gray-800
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                  "
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveEdit(task.id)}
                  disabled={isUpdating || !editTitle.trim()}
                  className="
                    px-4
                    py-2.5
                    text-sm
                    font-medium
                    text-white
                    bg-gradient-to-r
                    from-blue-600
                    to-indigo-600
                    hover:from-blue-700
                    hover:to-indigo-700
                    rounded-lg
                    transition-all
                    duration-200
                    focus:outline-none
                    focus:ring-2
                    focus:ring-blue-500
                    focus:ring-offset-2
                    dark:focus:ring-offset-gray-800
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                    flex
                    items-center
                    gap-2
                    shadow-sm
                  "
                >
                  {isUpdating && <LoadingSpinner size="sm" className="text-white" />}
                  {isUpdating ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
          );
        }

        // Show normal task item
        return (
          <TaskItem
            key={task.id}
            task={task}
            onToggleComplete={onToggleComplete}
            onEdit={handleEdit}
            onDelete={onDelete}
          />
        );
      })}
    </div>
  );
}