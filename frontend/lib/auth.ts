/**
 * Authentication utility functions
 *
 * Handles JWT token operations including decoding, validation, and storage.
 * All functions are client-side only (localStorage access).
 */

/**
 * JWT token payload structure
 */
export interface JWTPayload {
  user_id: string;
  sub: string;
  email: string;
  name: string;
  iat: number;
  exp: number;
}

/**
 * Decode JWT token without verification
 *
 * Note: This only decodes the payload - does NOT verify signature.
 * Backend endpoints must still validate tokens for security.
 * Client-side decoding is only for UI display purposes.
 *
 * @param token - JWT token string
 * @returns Decoded payload or null if invalid
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    // JWT format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decode base64url payload (second part)
    const payload = parts[1];

    // Replace URL-safe characters and decode
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const decoded = atob(base64);

    return JSON.parse(decoded) as JWTPayload;
  } catch (error) {
    console.error('Failed to decode JWT:', error);
    return null;
  }
}

/**
 * Check if JWT token is expired
 *
 * @param token - JWT token string
 * @returns true if expired, false if valid, null if unable to decode
 */
export function isTokenExpired(token: string): boolean | null {
  const payload = decodeJWT(token);
  if (!payload || !payload.exp) {
    return null;
  }

  // exp is in seconds, Date.now() is in milliseconds
  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp < currentTime;
}

/**
 * Get JWT token from localStorage
 *
 * @returns Token string or null if not found/expired
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const token = localStorage.getItem('auth_token');
  if (!token) {
    return null;
  }

  // Check if token is expired
  if (isTokenExpired(token)) {
    // Remove expired token
    localStorage.removeItem('auth_token');
    return null;
  }

  return token;
}

/**
 * Get decoded user info from stored JWT token
 *
 * @returns User info or null if token not found/invalid/expired
 */
export function getCurrentUser(): JWTPayload | null {
  const token = getAuthToken();
  if (!token) {
    return null;
  }

  return decodeJWT(token);
}

/**
 * Save JWT token to localStorage
 *
 * @param token - JWT token string
 */
export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') {
    return;
  }

  localStorage.setItem('auth_token', token);
}

/**
 * Remove JWT token from localStorage
 *
 * Used for sign out functionality
 */
export function clearAuthToken(): void {
  if (typeof window === 'undefined') {
    return;
  }

  localStorage.removeItem('auth_token');
}

/**
 * Check if user is authenticated
 *
 * @returns true if valid token exists, false otherwise
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}
