# Use a lightweight Python base image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency list first (for Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app files into the container
COPY . .

# Expose the port Streamlit will run on
EXPOSE 8080

# Start the Streamlit app when the container runs
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0"]