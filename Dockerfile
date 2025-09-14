FROM python:3.11-slim

WORKDIR /app

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin -c "Docker image user" appuser

# Copy requirements file first to leverage Docker cache
COPY --chown=appuser:appgroup requirements.txt .

# Grant appuser ownership of /app
RUN chown appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Create and activate virtual environment
RUN python -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies using standard pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Ensure the appuser owns the application code as well
COPY --chown=appuser:appgroup server.py .

# Expose the port the server runs on
EXPOSE 7860

# Command to run the server with python directly
CMD ["python", "main.py"] 