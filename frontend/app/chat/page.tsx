/**
 * Chat Page - AI-Powered Todo Chatbot Interface
 *
 * A beautiful, modern chat interface for interacting with the AI-powered
 * todo assistant. Users can create, view, complete, delete, and update
 * tasks through natural language commands.
 *
 * Features:
 * - Full-height chat interface with message bubbles
 * - Dark mode support matching existing app theme
 * - Typing indicator during AI processing
 * - Auto-scroll to latest message
 * - Tool call indicators for AI actions
 * - Mobile responsive (375px minimum)
 * - JWT authentication integration
 * - Conversation history persistence
 *
 * @see specs/002-ai-chatbot/contracts/chat-endpoint.md for API contract
 */

'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { getCurrentUser, type JWTPayload } from '@/lib/auth';
import { api } from '@/lib/api-client';
import { clsx } from 'clsx';
import type { ToolCall, Message, ChatResponse } from '@/types/chat';
import { TOOL_DISPLAY_NAMES } from '@/types/chat';

// -----------------------------------------------------------------------------
// Helper Components
// -----------------------------------------------------------------------------

/**
 * Animated typing indicator with three bouncing dots
 */
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      <div className="flex gap-1">
        <span
          className="
            w-2 h-2 rounded-full bg-purple-400
            animate-bounce
          "
          style={{ animationDelay: '0ms' }}
        />
        <span
          className="
            w-2 h-2 rounded-full bg-purple-400
            animate-bounce
          "
          style={{ animationDelay: '150ms' }}
        />
        <span
          className="
            w-2 h-2 rounded-full bg-purple-400
            animate-bounce
          "
          style={{ animationDelay: '300ms' }}
        />
      </div>
      <span className="ml-2 text-sm text-gray-400">AI is thinking...</span>
    </div>
  );
}

/**
 * Icon component for tool actions
 */
function ToolIcon({ tool }: { tool: string }) {
  const iconClasses = 'w-4 h-4';

  switch (tool) {
    case 'add_task':
      return (
        <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      );
    case 'list_tasks':
      return (
        <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
      );
    case 'complete_task':
      return (
        <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      );
    case 'delete_task':
      return (
        <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      );
    case 'update_task':
      return (
        <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      );
    default:
      return (
        <svg className={iconClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      );
  }
}

/**
 * Tool call badge component showing what action the AI performed
 */
function ToolCallBadge({ toolCall }: { toolCall: ToolCall }) {
  const toolName = TOOL_DISPLAY_NAMES[toolCall.tool] || toolCall.tool;
  const isSuccess = toolCall.result?.success === true;

  return (
    <div
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
        'transition-colors duration-200',
        isSuccess
          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
          : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
      )}
    >
      <ToolIcon tool={toolCall.tool} />
      <span>{toolName}</span>
    </div>
  );
}

/**
 * Individual message bubble component
 */
function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  const isError = message.isError;

  return (
    <div
      className={clsx(
        'flex w-full mb-4',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div
        className={clsx(
          'max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3',
          'transition-all duration-200 ease-out',
          isUser
            ? 'bg-gradient-to-br from-purple-600 to-purple-700 text-white rounded-br-md'
            : isError
              ? 'bg-red-500/10 border border-red-500/30 text-red-200 rounded-bl-md'
              : 'bg-white/10 backdrop-blur-sm border border-white/10 text-gray-100 rounded-bl-md'
        )}
      >
        {/* Avatar and role indicator */}
        <div className="flex items-center gap-2 mb-1">
          <div
            className={clsx(
              'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
              isUser
                ? 'bg-purple-500/50 text-white'
                : 'bg-gradient-to-br from-emerald-400 to-cyan-400 text-gray-900'
            )}
          >
            {isUser ? 'U' : 'AI'}
          </div>
          <span className="text-xs text-gray-400">
            {isUser ? 'You' : 'Todo Assistant'}
          </span>
        </div>

        {/* Message content */}
        <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
          {message.content}
        </div>

        {/* Tool calls badges */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-white/10">
            {message.toolCalls.map((toolCall, index) => (
              <ToolCallBadge key={index} toolCall={toolCall} />
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className="mt-2 text-right">
          <span className="text-xs text-gray-400/70">
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>
    </div>
  );
}

/**
 * Empty state component shown when no messages exist
 */
function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-6 py-12">
      <div className="w-20 h-20 mb-6 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </div>
      <h3 className="text-xl font-semibold text-white mb-2">
        Start a Conversation
      </h3>
      <p className="text-gray-400 max-w-sm mb-8">
        Chat with your AI assistant to manage tasks using natural language.
        Try saying something like:
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
        {[
          'Add a task to buy groceries',
          'Show me my tasks',
          'Mark task 1 as done',
          'Delete the grocery task',
        ].map((suggestion, index) => (
          <div
            key={index}
            className="
              px-4 py-3 rounded-xl
              bg-white/5 border border-white/10
              text-sm text-gray-300
              hover:bg-white/10 hover:border-purple-500/30
              transition-all duration-200
              cursor-default
            "
          >
            &quot;{suggestion}&quot;
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Send button with loading state
 */
function SendButton({
  onClick,
  disabled,
  isLoading,
}: {
  onClick: () => void;
  disabled: boolean;
  isLoading: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'p-3 rounded-xl transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-purple-500/50',
        disabled
          ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
          : 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 text-white shadow-lg hover:shadow-purple-500/25'
      )}
      aria-label="Send message"
    >
      {isLoading ? (
        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
      )}
    </button>
  );
}

// -----------------------------------------------------------------------------
// Conversation Sidebar Component
// -----------------------------------------------------------------------------

interface ConversationItem {
  id: number;
  created_at: string;
  updated_at: string;
}

interface ConversationSidebarProps {
  conversations: ConversationItem[];
  currentConversationId: number | null;
  onSelectConversation: (id: number) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: number) => void;
  isOpen: boolean;
  onClose: () => void;
}

function ConversationSidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  isOpen,
  onClose,
}: ConversationSidebarProps) {
  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'Unknown';

    // Parse UTC date from backend and convert to PKT (UTC+5)
    let date = new Date(dateStr);
    if (isNaN(date.getTime())) return 'Unknown';

    // If the date string doesn't have timezone info, assume it's UTC
    if (!dateStr.includes('Z') && !dateStr.includes('+')) {
      date = new Date(dateStr + 'Z'); // Append Z to treat as UTC
    }

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 0) return 'Just now'; // Future date fallback
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    // Format date in PKT timezone
    return date.toLocaleDateString('en-PK', { timeZone: 'Asia/Karachi' });
  };

  return (
    <>
      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed lg:relative inset-y-0 left-0 z-50 lg:z-0',
          'w-72 bg-gray-900/95 backdrop-blur-xl border-r border-white/10',
          'transform transition-transform duration-300 ease-in-out',
          'flex flex-col',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          'lg:translate-x-0'
        )}
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <h2 className="text-lg font-semibold text-white">Conversations</h2>
          <button
            onClick={onClose}
            className="lg:hidden p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/10"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={() => {
              onNewConversation();
              onClose();
            }}
            className="
              w-full flex items-center justify-center gap-2 px-4 py-2.5
              bg-gradient-to-r from-purple-600 to-cyan-600
              hover:from-purple-500 hover:to-cyan-500
              text-white font-medium rounded-lg
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-purple-500/50
            "
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Start a new chat!</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                className={clsx(
                  'group flex items-center gap-2 p-3 rounded-lg cursor-pointer',
                  'transition-all duration-200',
                  currentConversationId === conv.id
                    ? 'bg-purple-500/20 border border-purple-500/30'
                    : 'hover:bg-white/5 border border-transparent'
                )}
                onClick={() => {
                  onSelectConversation(conv.id);
                  onClose();
                }}
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500/20 to-cyan-500/20 flex items-center justify-center">
                  <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">
                    Chat #{conv.id}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatDate(conv.updated_at)}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conv.id);
                  }}
                  className="
                    opacity-0 group-hover:opacity-100
                    p-1.5 rounded-md
                    text-gray-500 hover:text-red-400
                    hover:bg-red-500/10
                    transition-all duration-200
                  "
                  title="Delete conversation"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>
      </aside>
    </>
  );
}

// -----------------------------------------------------------------------------
// Quick Action Suggestions Component
// -----------------------------------------------------------------------------

/**
 * Quick action suggestion buttons that populate the chat input
 */
interface QuickActionSuggestionsProps {
  onSuggestionClick: (suggestion: string) => void;
  disabled?: boolean;
}

const QUICK_SUGGESTIONS = [
  {
    label: 'Add Task',
    prompt: 'Add a task to buy groceries',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
      </svg>
    ),
    color: 'bg-green-500/10 text-green-400 border-green-500/30 hover:bg-green-500/20',
  },
  {
    label: 'Update Title',
    prompt: 'Update task 1 title to "Call dentist at 3pm"',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    ),
    color: 'bg-blue-500/10 text-blue-400 border-blue-500/30 hover:bg-blue-500/20',
  },
  {
    label: 'Mark Done',
    prompt: 'Mark task 1 as done',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    ),
    color: 'bg-purple-500/10 text-purple-400 border-purple-500/30 hover:bg-purple-500/20',
  },
  {
    label: 'Delete Task',
    prompt: 'Delete task 1',
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
      </svg>
    ),
    color: 'bg-red-500/10 text-red-400 border-red-500/30 hover:bg-red-500/20',
  },
];

function QuickActionSuggestions({ onSuggestionClick, disabled }: QuickActionSuggestionsProps) {
  return (
    <div className="flex flex-wrap gap-2 justify-center px-4 py-3">
      {QUICK_SUGGESTIONS.map((suggestion) => (
        <button
          key={suggestion.label}
          onClick={() => onSuggestionClick(suggestion.prompt)}
          disabled={disabled}
          className={clsx(
            'flex items-center gap-2 px-3 py-2 rounded-full border text-sm font-medium',
            'transition-all duration-200 ease-in-out',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            suggestion.color
          )}
        >
          {suggestion.icon}
          <span>{suggestion.label}</span>
        </button>
      ))}
    </div>
  );
}

// -----------------------------------------------------------------------------
// Main Chat Page Component
// -----------------------------------------------------------------------------

/**
 * Chat page component with full conversation management
 */
export default function ChatPage() {
  const router = useRouter();

  // Authentication state
  const [user, setUser] = useState<JWTPayload | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Conversation list state
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Scroll to bottom of messages
   */
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  /**
   * Auto-resize textarea based on content
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    // Reset height to auto to recalculate
    e.target.style.height = 'auto';
    // Set height based on scrollHeight (max 150px)
    e.target.style.height = `${Math.min(e.target.scrollHeight, 150)}px`;
  };

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  /**
   * Send message to chat API
   */
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading || !user) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }

    // Add user message to UI immediately (optimistic update)
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    setIsLoading(true);

    try {
      const response = await api.post<ChatResponse>(
        `/api/${user.user_id}/chat`,
        {
          message: userMessage,
          conversation_id: conversationId,
        }
      );

      // Update conversation ID if new conversation and save to localStorage
      if (response.conversation_id) {
        const isNewConversation = !conversationId;
        setConversationId(response.conversation_id);
        localStorage.setItem('chat_conversation_id', response.conversation_id.toString());

        // Refresh conversations list if this is a new conversation
        if (isNewConversation) {
          fetchConversations(user.user_id);
        }
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: response.reply,
        timestamp: response.timestamp,
        toolCalls: response.tool_calls,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      // Add error message to chat
      const errorChatMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorChatMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Start a new conversation
   */
  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    localStorage.removeItem('chat_conversation_id');
    inputRef.current?.focus();
  };

  /**
   * Navigate back to dashboard
   */
  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  /**
   * Handle quick action suggestion click - populate input with suggestion
   */
  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  };

  /**
   * Fetch list of conversations for the user
   */
  const fetchConversations = useCallback(async (userId: string) => {
    try {
      const response = await api.get<ConversationItem[]>(`/api/${userId}/conversations`);
      setConversations(response);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
    }
  }, []);

  /**
   * Handle selecting a conversation from sidebar
   */
  const handleSelectConversation = useCallback(async (convId: number) => {
    if (!user) return;

    setConversationId(convId);
    localStorage.setItem('chat_conversation_id', convId.toString());

    // Load the conversation messages
    try {
      const response = await api.get<Array<{
        id: number;
        role: string;
        content: string;
        tool_calls: ToolCall[] | null;
        created_at: string;
      }>>(`/api/${user.user_id}/conversations/${convId}/messages`);

      const loadedMessages: Message[] = response.map((msg) => ({
        id: `msg-${msg.id}`,
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: msg.created_at,
        toolCalls: msg.tool_calls || undefined,
      }));

      setMessages(loadedMessages);
    } catch (err) {
      console.error('Failed to load conversation:', err);
    }
  }, [user]);

  /**
   * Handle deleting a conversation
   */
  const handleDeleteConversation = useCallback(async (convId: number) => {
    if (!user) return;

    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete this conversation?')) {
      return;
    }

    try {
      await api.delete(`/api/${user.user_id}/conversations/${convId}`);

      // Remove from local state
      setConversations(prev => prev.filter(c => c.id !== convId));

      // If deleting current conversation, start new one
      if (conversationId === convId) {
        handleNewConversation();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError('Failed to delete conversation');
    }
  }, [user, conversationId, handleNewConversation]);

  /**
   * Load conversation history from API
   */
  const loadConversationHistory = useCallback(async (userId: string, convId: number) => {
    try {
      const response = await api.get<Array<{
        id: number;
        role: string;
        content: string;
        tool_calls: ToolCall[] | null;
        created_at: string;
      }>>(`/api/${userId}/conversations/${convId}/messages`);

      const loadedMessages: Message[] = response.map((msg) => ({
        id: `msg-${msg.id}`,
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: msg.created_at,
        toolCalls: msg.tool_calls || undefined,
      }));

      setMessages(loadedMessages);
      setConversationId(convId);
    } catch (err) {
      console.error('Failed to load conversation history:', err);
      // If conversation doesn't exist, clear saved ID
      localStorage.removeItem('chat_conversation_id');
      setConversationId(null);
    }
  }, []);

  /**
   * Check authentication on mount and load last conversation
   */
  useEffect(() => {
    const currentUser = getCurrentUser();

    if (!currentUser) {
      router.push('/auth/signin');
      return;
    }

    setUser(currentUser);
    setIsAuthLoading(false);

    // Initialize chat: Fetch conversations -> Restore last session or Load latest
    const initChat = async () => {
      try {
        // 1. Fetch all conversations
        const convs = await api.get<ConversationItem[]>(`/api/${currentUser.user_id}/conversations`);
        setConversations(convs);

        // 2. Determine which conversation to load
        let convIdToLoad: number | null = null;
        const savedIdStr = localStorage.getItem('chat_conversation_id');

        if (savedIdStr) {
          const savedId = parseInt(savedIdStr, 10);
          // Only attempt to load if it exists in the user's list (avoids 404s)
          if (!isNaN(savedId) && convs.some(c => c.id === savedId)) {
            convIdToLoad = savedId;
          }
        }

        // 3. Fallback: If no valid saved ID, load the most recent conversation
        if (!convIdToLoad && convs.length > 0) {
          convIdToLoad = convs[0].id; // Backend returns desc sorted by updated_at
        }

        // 4. Load the selected conversation
        if (convIdToLoad) {
          await loadConversationHistory(currentUser.user_id, convIdToLoad);
          localStorage.setItem('chat_conversation_id', convIdToLoad.toString());
        }

      } catch (error) {
        console.error('Failed to initialize chat:', error);
      }
    };

    initChat();
  }, [router, loadConversationHistory]);

  /**
   * Scroll to bottom when messages change
   */
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  /**
   * Focus input on mount
   */
  useEffect(() => {
    if (!isAuthLoading && user) {
      inputRef.current?.focus();
    }
  }, [isAuthLoading, user]);

  // Loading state
  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-transparent">
        <div className="text-center">
          <div
            className="
              inline-block w-12 h-12
              border-4 border-purple-600 border-t-transparent
              rounded-full animate-spin
            "
            role="status"
            aria-label="Loading chat"
          />
          <p className="mt-4 text-gray-400">Loading chat...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!user) {
    return null;
  }

  return (
    <div className="flex h-screen bg-transparent">
      {/* Conversation Sidebar */}
      <ConversationSidebar
        conversations={conversations}
        currentConversationId={conversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header
          className="
            flex-shrink-0
            bg-white/5 backdrop-blur-xl
            border-b border-white/10
            sticky top-0 z-30
          "
        >
          <div className="px-4 py-3 flex items-center justify-between">
            {/* Left: Menu button (mobile), Back button and title */}
            <div className="flex items-center gap-3">
              {/* Mobile menu button */}
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="
                  lg:hidden p-2 rounded-lg
                  text-gray-400 hover:text-white
                  hover:bg-white/10
                  transition-all duration-200
                "
                aria-label="Open conversations"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <button
                onClick={handleBackToDashboard}
                className="
                  p-2 rounded-lg
                  text-gray-400 hover:text-white
                  hover:bg-white/10
                  transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-purple-500/50
                "
                aria-label="Back to dashboard"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-white">Todo Assistant</h1>
                  <p className="text-xs text-gray-400">Manage tasks with AI</p>
                </div>
              </div>
            </div>

            {/* Right: New conversation button */}
            <button
              onClick={handleNewConversation}
              className="
                px-3 py-1.5 rounded-lg
                text-sm font-medium
                text-purple-300 hover:text-purple-200
                border border-purple-500/30 hover:border-purple-500/50
                hover:bg-purple-500/10
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-purple-500/50
                flex items-center gap-2
              "
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="hidden sm:inline">New Chat</span>
            </button>
          </div>
        </header>

        {/* Quick Action Suggestions */}
        <div className="flex-shrink-0 bg-white/5 border-b border-white/10">
          <div className="max-w-4xl mx-auto">
            <QuickActionSuggestions
              onSuggestionClick={handleSuggestionClick}
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Messages Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 py-6">
            {messages.length === 0 ? (
              <EmptyState />
            ) : (
              <>
                {messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}
                {isLoading && <TypingIndicator />}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </main>

        {/* Input Area */}
        <footer
          className="
          flex-shrink-0
          bg-white/5 backdrop-blur-xl
          border-t border-white/10
        "
        >
          <div className="max-w-4xl mx-auto px-4 py-4">
            {/* Error message */}
            {error && (
              <div className="mb-3 px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
                {error}
              </div>
            )}

            {/* Input container */}
            <div
              className="
              flex items-end gap-3
              bg-white/5 backdrop-blur-sm
              border border-white/10 hover:border-white/20
              rounded-2xl p-2
              transition-all duration-200
              focus-within:border-purple-500/50 focus-within:ring-1 focus-within:ring-purple-500/25
            "
            >
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder="Type a message... (e.g., 'Add a task to buy milk')"
                rows={1}
                className="
                flex-1 min-h-[44px] max-h-[150px]
                bg-transparent border-0
                text-white placeholder-gray-500
                resize-none
                focus:outline-none focus:ring-0
                px-3 py-2
                text-sm leading-relaxed
              "
                disabled={isLoading}
                aria-label="Chat message input"
              />
              <SendButton
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                isLoading={isLoading}
              />
            </div>

            {/* Helper text */}
            <p className="mt-2 text-center text-xs text-gray-500">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
