# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (not mandatory for Telegram bots but good practice)
EXPOSE 8080

# Start the bot
CMD ["python", "main.py"]
