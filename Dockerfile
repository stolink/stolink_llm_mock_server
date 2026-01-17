FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY main.py ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Expose port
EXPOSE 8000

# Run the application
# We use `uv run` to ensure we use the environment created by uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
