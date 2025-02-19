FROM python:3.12-alpine

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set the working directory
WORKDIR /workspace

# Change ownership to the non-root user
RUN chown -R appuser:appgroup /workspace

# Switch to non-root user
USER appuser

# Install dependencies (done after switching user to avoid permission issues)
RUN pip install --no-cache-dir requests beautifulsoup4
