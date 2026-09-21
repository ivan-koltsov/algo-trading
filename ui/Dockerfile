# Stage 1: Build the application
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci || npm install

# Copy project files and build
COPY . .

# Build arguments for Vite compilation
ARG VITE_API_URL
ARG VITE_APP_ENV
ENV VITE_API_URL=$VITE_API_URL \
    VITE_APP_ENV=$VITE_APP_ENV

RUN npm run build

# Stage 2: Production runner
FROM node:22-alpine AS runner

WORKDIR /app

# Set production environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    HOST=0.0.0.0

# Install curl for healthcheck
RUN apk add --no-cache curl

# Create a non-root system user and group
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 reactapp

# Copy the built production output from the builder stage
COPY --from=builder --chown=reactapp:nodejs /app/.output .output

USER reactapp

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start Nitro production server
CMD ["node", ".output/server/index.mjs"]
