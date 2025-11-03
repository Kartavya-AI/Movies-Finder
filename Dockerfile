# Use a lightweight Python base image
FROM python:3.12-slim

# Install Node.js & npm
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list first (for Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app files into the container
COPY . .

# Install any Node MCP packages globally if needed
RUN npm install -g tv-recommender-mcp-server

EXPOSE 8080

CMD exec uvicorn fastapi_app:app --host 0.0.0.0 --port $PORT
