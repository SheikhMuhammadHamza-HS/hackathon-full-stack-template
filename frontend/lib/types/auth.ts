/**
 * Authentication Type Definitions
 *
 * Centralized type definitions for authentication-related data structures.
 * Ensures type safety across signup, login, and user management flows.
 */

/**
 * User data structure returned from API
 */
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

/**
 * Signup request payload
 */
export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

/**
 * Signup API response
 */
export interface SignupResponse {
  user: User;
  token: string;
}

/**
 * Login request payload
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Login API response
 */
export interface LoginResponse {
  user: User;
  token: string;
}

/**
 * Form validation errors
 */
export interface ValidationErrors {
  [key: string]: string | undefined;
}
