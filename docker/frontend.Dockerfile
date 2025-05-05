# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Install dependencies
COPY web/frontend/package*.json ./
RUN npm ci

# Copy source code
COPY web/frontend/ ./

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
