/**
 * AddTaskForm Component
 *
 * Form for creating new tasks with validation and error handling.
 * Features a modern, clean design with improved visual hierarchy and interactions.
 *
 * Features:
 * - Title input (required, max 200 chars)
 * - Description textarea (optional, max 1000 chars)
 * - Client-side validation with error messages
 * - Loading states during submission
 * - Accessible form labels and error associations
 * - Mobile-responsive layout
 * - Auto-focus on title input
 * - Character count indicators
 * - Modern UI with enhanced visual design and interactions
 *
 * @example
 * <AddTaskForm
 *   onSubmit={handleCreateTask}
 *   onCancel={handleCancel}
 *   isSubmitting={false}
 * />
 */

'use client';

import { useState, FormEvent, useEffect, useRef } from 'react';
import { CreateTaskPayload, TaskPriority, RecurringInterval } from '@/types/task';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';

interface AddTaskFormProps {
  /** Callback when form is submitted with valid data */
  onSubmit: (data: CreateTaskPayload) => Promise<void>;
  /** Callback when cancel button is clicked */
  onCancel: () => void;
  /** External loading state (optional) */
  isSubmitting?: boolean;
}

const MAX_TITLE_LENGTH = 200;
const MAX_DESCRIPTION_LENGTH = 1000;
const MAX_TAGS = 10;

/**
 * Form component for adding new tasks with modern UI design
 */
export function AddTaskForm({
  onSubmit,
  onCancel,
  isSubmitting = false,
}: AddTaskFormProps) {
  console.log('🔴🔴🔴 AddTaskForm LOADED - Priority fields should be visible! 🔴🔴🔴');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('medium');
  const [tagsInput, setTagsInput] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurringInterval, setRecurringInterval] = useState<RecurringInterval>('daily');
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
    tags?: string;
    recurring?: string;
  }>({});
  const [isLoading, setIsLoading] = useState(false);
  const titleInputRef = useRef<HTMLInputElement>(null);

  // Auto-focus title input on mount
  useEffect(() => {
    titleInputRef.current?.focus();
  }, []);

  /**
   * Parse and validate tags input
   */
  const parseTags = (): string[] | undefined => {
    if (!tagsInput.trim()) return undefined;

    const tags = tagsInput
      .split(',')
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    return tags.length > 0 ? tags : undefined;
  };

  /**
   * Validate form inputs
   */
  const validate = (): boolean => {
    const newErrors: {
      title?: string;
      description?: string;
      tags?: string;
      recurring?: string;
    } = {};

    // Title validation
    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > MAX_TITLE_LENGTH) {
      newErrors.title = `Title must be ${MAX_TITLE_LENGTH} characters or less`;
    }

    // Description validation
    if (description.length > MAX_DESCRIPTION_LENGTH) {
      newErrors.description = `Description must be ${MAX_DESCRIPTION_LENGTH} characters or less`;
    }

    // Tags validation
    const tags = parseTags();
    if (tags && tags.length > MAX_TAGS) {
      newErrors.tags = `Maximum ${MAX_TAGS} tags allowed`;
    }

    // Recurring validation
    if (isRecurring && !recurringInterval) {
      newErrors.recurring = 'Recurring interval is required for recurring tasks';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});

    // Validate
    if (!validate()) {
      return;
    }

    // Prepare payload
    const tags = parseTags();
    const payload: CreateTaskPayload = {
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      tags,
      due_date: dueDate || undefined,
      is_recurring: isRecurring,
      recurring_interval: isRecurring ? recurringInterval : undefined,
    };

    // Submit
    setIsLoading(true);
    try {
      await onSubmit(payload);
      // Form will be unmounted after successful submission
      // So no need to reset form here
    } catch (error) {
      // Error handling is done in parent component
      setIsLoading(false);
    }
  };

  /**
   * Handle cancel
   */
  const handleCancel = () => {
    // Clear form
    setTitle('');
    setDescription('');
    setPriority('medium');
    setTagsInput('');
    setDueDate('');
    setIsRecurring(false);
    setRecurringInterval('daily');
    setErrors({});
    onCancel();
  };

  const loading = isLoading || isSubmitting;

  return (
    <form
      onSubmit={handleSubmit}
      className="
        bg-gradient-to-br
        from-blue-50
        to-indigo-50
        dark:from-blue-900/20
        dark:to-indigo-900/20
        border
        border-blue-200
        dark:border-blue-700
        rounded-2xl
        p-6
        space-y-5
        shadow-sm
        transition-all
        duration-300
        hover:shadow-md
      "
    >
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
          <svg
            className="w-5 h-5 text-white"
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
        </div>
        <h3
          className="
            text-lg
            font-semibold
            text-gray-900
            dark:text-white
          "
        >
          Add New Task
        </h3>
      </div>

      {/* Title Input */}
      <div>
        <label
          htmlFor="task-title"
          className="
            block
            text-sm
            font-medium
            text-gray-700
            dark:text-gray-300
            mb-2
          "
        >
          Title <span className="text-red-500" aria-label="required">*</span>
        </label>
        <input
          ref={titleInputRef}
          id="task-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={loading}
          maxLength={MAX_TITLE_LENGTH}
          className="
            w-full
            px-4
            py-3
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
            shadow-sm
          "
          placeholder="Enter task title"
          aria-describedby={errors.title ? 'task-title-error' : 'task-title-hint'}
          aria-invalid={!!errors.title}
          aria-required="true"
        />
        <div className="mt-2 flex items-center justify-between">
          <ErrorMessage message={errors.title} htmlFor="task-title" />
          <span
            id="task-title-hint"
            className="text-xs text-gray-500 dark:text-gray-400"
          >
            {title.length}/{MAX_TITLE_LENGTH}
          </span>
        </div>
      </div>

      {/* Description Textarea */}
      <div>
        <label
          htmlFor="task-description"
          className="
            block
            text-sm
            font-medium
            text-gray-700
            dark:text-gray-300
            mb-2
          "
        >
          Description <span className="text-gray-400 text-xs">(optional)</span>
        </label>
        <textarea
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={loading}
          maxLength={MAX_DESCRIPTION_LENGTH}
          rows={4}
          className="
            w-full
            px-4
            py-3
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
            resize-vertical
            shadow-sm
          "
          placeholder="Enter task description (optional)"
          aria-describedby={errors.description ? 'task-description-error' : 'task-description-hint'}
          aria-invalid={!!errors.description}
        />
        <div className="mt-2 flex items-center justify-between">
          <ErrorMessage message={errors.description} htmlFor="task-description" />
          <span
            id="task-description-hint"
            className="text-xs text-gray-500 dark:text-gray-400"
          >
            {description.length}/{MAX_DESCRIPTION_LENGTH}
          </span>
        </div>
      </div>

      {/* Priority Dropdown */}
      <div>
        <label
          htmlFor="task-priority"
          className="
            block
            text-sm
            font-medium
            text-gray-700
            dark:text-gray-300
            mb-2
          "
        >
          Priority
        </label>
        <select
          id="task-priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as TaskPriority)}
          disabled={loading}
          className="
            w-full
            px-4
            py-3
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
            shadow-sm
          "
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      {/* Tags Input */}
      <div>
        <label
          htmlFor="task-tags"
          className="
            block
            text-sm
            font-medium
            text-gray-700
            dark:text-gray-300
            mb-2
          "
        >
          Tags <span className="text-gray-400 text-xs">(optional)</span>
        </label>
        <input
          id="task-tags"
          type="text"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          disabled={loading}
          className="
            w-full
            px-4
            py-3
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
            shadow-sm
          "
          placeholder="Add tags (comma-separated)"
          aria-describedby={errors.tags ? 'task-tags-error' : 'task-tags-hint'}
          aria-invalid={!!errors.tags}
        />
        <div className="mt-2 flex items-center justify-between">
          <ErrorMessage message={errors.tags} htmlFor="task-tags" />
          <span
            id="task-tags-hint"
            className="text-xs text-gray-500 dark:text-gray-400"
          >
            {parseTags()?.length || 0} tag(s)
          </span>
        </div>
      </div>

      {/* Due Date Input */}
      <div>
        <label
          htmlFor="task-due-date"
          className="
            block
            text-sm
            font-medium
            text-gray-700
            dark:text-gray-300
            mb-2
          "
        >
          Due Date <span className="text-gray-400 text-xs">(optional)</span>
        </label>
        <input
          id="task-due-date"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          disabled={loading}
          className="
            w-full
            px-4
            py-3
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
            shadow-sm
          "
        />
      </div>

      {/* Recurring Task Checkbox and Interval */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <input
            id="task-recurring"
            type="checkbox"
            checked={isRecurring}
            onChange={(e) => setIsRecurring(e.target.checked)}
            disabled={loading}
            className="
              w-5
              h-5
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
          />
          <label
            htmlFor="task-recurring"
            className="
              text-sm
              font-medium
              text-gray-700
              dark:text-gray-300
              cursor-pointer
            "
          >
            Recurring Task
          </label>
        </div>

        {isRecurring && (
          <div>
            <label
              htmlFor="task-recurring-interval"
              className="
                block
                text-sm
                font-medium
                text-gray-700
                dark:text-gray-300
                mb-2
              "
            >
              Recurring Interval
            </label>
            <select
              id="task-recurring-interval"
              value={recurringInterval}
              onChange={(e) => setRecurringInterval(e.target.value as RecurringInterval)}
              disabled={loading}
              className="
                w-full
                px-4
                py-3
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
                shadow-sm
              "
              aria-describedby={errors.recurring ? 'task-recurring-error' : undefined}
              aria-invalid={!!errors.recurring}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
            <ErrorMessage message={errors.recurring} htmlFor="task-recurring-interval" />
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-3 pt-2">
        {/* Cancel Button */}
        <button
          type="button"
          onClick={handleCancel}
          disabled={loading}
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
            shadow-sm
          "
        >
          Cancel
        </button>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !title.trim()}
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
          {loading && <LoadingSpinner size="sm" className="text-white" />}
          {loading ? 'Creating...' : 'Create Task'}
        </button>
      </div>
    </form>
  );
}