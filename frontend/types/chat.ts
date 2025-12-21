/**
 * Chat type definitions
 *
 * Matches backend Chat API schema for type safety across frontend.
 * @see specs/002-ai-chatbot/contracts/chat-endpoint.md
 */

/**
 * Tool call information from AI response
 */
export interface ToolCall {
  /** Name of the MCP tool called */
  tool: string;
  /** Parameters passed to the tool */
  parameters: Record<string, unknown>;
  /** Result returned from the tool */
  result: Record<string, unknown>;
}

/**
 * Chat message structure for UI display
 */
export interface Message {
  /** Unique identifier for the message */
  id: string;
  /** Message sender role */
  role: 'user' | 'assistant';
  /** Message content text */
  content: string;
  /** ISO 8601 timestamp */
  timestamp: string;
  /** Tool calls made by assistant (optional) */
  toolCalls?: ToolCall[];
  /** Whether this message represents an error */
  isError?: boolean;
}

/**
 * Chat request payload
 */
export interface ChatRequest {
  /** User's natural language message (1-10,000 chars) */
  message: string;
  /** Conversation ID to continue (null for new conversation) */
  conversation_id: number | null;
}

/**
 * API response from POST /api/{user_id}/chat
 */
export interface ChatResponse {
  /** AI assistant's response text */
  reply: string;
  /** Conversation ID (new or existing) */
  conversation_id: number;
  /** MCP tools executed during processing */
  tool_calls?: ToolCall[];
  /** Server timestamp (ISO 8601) */
  timestamp: string;
}

/**
 * Conversation list item from GET /api/{user_id}/conversations
 */
export interface ConversationItem {
  /** Unique conversation identifier */
  id: number;
  /** When conversation was created */
  created_at: string;
  /** When conversation was last updated */
  updated_at: string;
}

/**
 * Message from conversation history
 */
export interface HistoryMessage {
  /** Unique message identifier */
  id: number;
  /** Conversation this message belongs to */
  conversation_id: number;
  /** Message sender role */
  role: 'user' | 'assistant';
  /** Message content text */
  content: string;
  /** Tool calls (for assistant messages) */
  tool_calls?: ToolCall[];
  /** When message was created */
  created_at: string;
}

/**
 * Tool names mapping to user-friendly labels
 */
export const TOOL_DISPLAY_NAMES: Record<string, string> = {
  add_task: 'Added Task',
  list_tasks: 'Listed Tasks',
  complete_task: 'Completed Task',
  delete_task: 'Deleted Task',
  update_task: 'Updated Task',
};
