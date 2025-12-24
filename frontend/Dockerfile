# =============================================================================
# Frontend Dockerfile - Next.js Application
# =============================================================================
# Multi-stage build for optimized production image using standalone output
# Base: node:20-alpine | Target Size: < 200MB | Security: Non-root user (nextjs)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies - Install npm packages
# -----------------------------------------------------------------------------
FROM node:20-alpine AS deps

# Set working directory
WORKDIR /app

# Install dependencies required for node-gyp (if native modules needed)
RUN apk add --no-cache libc6-compat

# Copy dependency files first (for layer caching)
COPY package.json package-lock.json* ./

# Install dependencies using npm ci for reproducible builds
# --legacy-peer-deps: Handle peer dependency conflicts gracefully
RUN npm ci

# -----------------------------------------------------------------------------
# Stage 2: Builder - Build the Next.js application
# -----------------------------------------------------------------------------
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source files
COPY . .

# Set environment variables for build
# NEXT_TELEMETRY_DISABLED: Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application
# This creates .next/standalone with minimal server
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Runner - Minimal production image
# -----------------------------------------------------------------------------
FROM node:20-alpine AS runner

# Set working directory
WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
# Using UID 1001 following Next.js Docker example conventions
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy public folder (static assets like favicon, images)
COPY --from=builder /app/public ./public

# Create .next directory and set ownership
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy standalone server output from builder
# The standalone folder contains a minimal Node.js server
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./

# Copy static files to the correct location
# Next.js expects static files at .next/static
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copy environment variable injection script (before switching to nextjs user)
COPY --chown=nextjs:nodejs docker-entrypoint.sh /app/docker-entrypoint.sh
RUN apk add --no-cache dos2unix && \
    dos2unix /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER nextjs

# Expose Next.js port
EXPOSE 3000

# Set hostname to listen on all interfaces
ENV HOSTNAME="0.0.0.0"
ENV PORT=3000

# Start the standalone server via entrypoint script
# This allows runtime environment variable injection
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["node", "server.js"]
