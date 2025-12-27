/**
 * TaskItem Component
 *
 * Displays a single task with completion toggle and action buttons.
 * Features a modern, clean design with improved visual hierarchy and interactions.
 *
 * Features:
 * - Checkbox for marking task complete/incomplete
 * - Strikethrough styling for completed tasks
 * - Edit and delete action buttons
 * - Responsive layout with mobile-first design
 * - Accessible keyboard navigation
 * - Loading states for async operations
 * - Modern UI with enhanced visual design and interactions
 *
 * @example
 * <TaskItem
 *   task={task}
 *   onToggleComplete={handleToggle}
 *   onEdit={handleEdit}
 *   onDelete={handleDelete}
 * />
 */

'use client';

import { useState } from 'react';
import { Task } from '@/types/task';
import { LoadingSpinner } from './LoadingSpinner';

interface TaskItemProps {
  /** Task data to display */
  task: Task;
  /** Callback when task completion is toggled */
  onToggleComplete: (taskId: number, completed: boolean) => Promise<void>;
  /** Callback when edit button is clicked */
  onEdit: (task: Task) => void;
  /** Callback when delete button is clicked */
  onDelete: (taskId: number) => Promise<void>;
  /** Callback when tag chip is clicked */
  onTagClick?: (tag: string) => void;
}

/**
 * Individual task item component with modern UI design
 */
export function TaskItem({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
  onTagClick,
}: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  /**
   * Handle checkbox toggle with optimistic UI
   */
  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggleComplete(task.id, !task.completed);
    } finally {
      setIsToggling(false);
    }
  };

  /**
   * Handle delete with confirmation
   */
  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      setIsDeleting(true);
      try {
        await onDelete(task.id);
      } catch (error) {
        // Error handling is done in parent component
        setIsDeleting(false);
      }
    }
  };

  return (
    <div
      className={`
        flex
        items-start
        gap-4
        p-5
        bg-white
        dark:bg-gray-800
        border
        border-gray-200
        dark:border-gray-700
        rounded-xl
        transition-all
        duration-300
        hover:shadow-md
        ${isDeleting ? 'opacity-50 pointer-events-none' : ''}
        ${task.completed ? 'bg-gray-50 dark:bg-gray-800/70' : ''}
      `}
    >
      {/* Checkbox */}
      <div className="flex items-start pt-0.5">
        {isToggling ? (
          <div className="w-6 h-6 flex items-center justify-center">
            <LoadingSpinner size="sm" className="text-blue-600" />
          </div>
        ) : (
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggle}
            disabled={isToggling || isDeleting}
            className="
              w-6
              h-6
              text-blue-600
              bg-gray-50
              dark:bg-gray-900
              border-gray-300
              dark:border-gray-600
              rounded
              focus:ring-2
              focus:ring-blue-500
              focus:ring-offset-2
              dark:focus:ring-offset-gray-800
              transition-colors
              cursor-pointer
              disabled:opacity-50
              disabled:cursor-not-allowed
            "
            aria-label={`Mark "${task.title}" as ${task.completed ? 'incomplete' : 'complete'}`}
          />
        )}
      </div>

      {/* Task Content */}
      <div className="flex-1 min-w-0">
        <h3
          className={`
            text-base
            font-medium
            text-gray-900
            dark:text-white
            break-words
            ${task.completed ? 'line-through text-gray-500 dark:text-gray-400' : ''}
          `}
        >
          {task.title}
        </h3>
        {task.description && (
          <p
            className={`
              mt-2
              text-sm
              text-gray-600
              dark:text-gray-400
              break-words
              ${task.completed ? 'line-through' : ''}
            `}
          >
            {task.description}
          </p>
        )}

        {/* Tags Display */}
        {task.tags && task.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {task.tags.map((tag, index) => (
              <button
                key={index}
                onClick={() => onTagClick?.(tag)}
                className="
                  inline-flex
                  items-center
                  px-2.5
                  py-0.5
                  rounded-full
                  text-xs
                  font-medium
                  bg-blue-100
                  text-blue-800
                  dark:bg-blue-900/30
                  dark:text-blue-400
                  hover:bg-blue-200
                  dark:hover:bg-blue-800/40
                  transition-colors
                  cursor-pointer
                "
                title={`Filter by tag: ${tag}`}
              >
                {tag}
              </button>
            ))}
          </div>
        )}

        <div className="mt-3 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-500 flex-wrap">
          {/* Priority Badge */}
          <span
            className={`
              inline-flex
              items-center
              px-2
              py-0.5
              rounded-full
              text-xs
              font-medium
              ${
                task.priority === 'high'
                  ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                  : task.priority === 'medium'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'
              }
            `}
          >
            {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
          </span>

          {/* Due Date Display */}
          {task.due_date && (
            <span
              className={`
                inline-flex
                items-center
                px-2
                py-0.5
                rounded-full
                text-xs
                font-medium
                ${
                  new Date(task.due_date) < new Date()
                    ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    : 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
                }
              `}
            >
              {new Date(task.due_date) < new Date() && '⚠️ OVERDUE: '}
              Due: {new Date(task.due_date).toLocaleString(undefined, {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          )}

          {/* Recurring Badge */}
          {task.is_recurring && task.recurring_interval && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400">
              🔄 {task.recurring_interval}
            </span>
          )}

          {/* Created Date */}
          <span>
            Created {new Date(task.created_at).toLocaleDateString()}
          </span>

          {/* Completed Badge */}
          {task.completed && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Completed
            </span>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-start gap-2">
        {/* Edit Button */}
        <button
          onClick={() => onEdit(task)}
          disabled={isDeleting || task.completed}
          className="
            p-2.5
            text-gray-600
            dark:text-gray-400
            hover:text-blue-600
            dark:hover:text-blue-400
            hover:bg-blue-50
            dark:hover:bg-blue-900/20
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
            disabled:hover:text-gray-600
            disabled:hover:bg-transparent
            shadow-sm
          "
          aria-label={`Edit task: ${task.title}`}
          title={task.completed ? 'Cannot edit completed task' : 'Edit task'}
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
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
        </button>

        {/* Delete Button */}
        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="
            p-2.5
            text-gray-600
            dark:text-gray-400
            hover:text-red-600
            dark:hover:text-red-400
            hover:bg-red-50
            dark:hover:bg-red-900/20
            rounded-lg
            transition-all
            duration-200
            focus:outline-none
            focus:ring-2
            focus:ring-red-500
            focus:ring-offset-2
            dark:focus:ring-offset-gray-800
            disabled:opacity-50
            disabled:cursor-not-allowed
            shadow-sm
          "
          aria-label={`Delete task: ${task.title}`}
          title="Delete task"
        >
          {isDeleting ? (
            <LoadingSpinner size="sm" className="text-red-600" />
          ) : (
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
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}