FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Copy the requirements file into the container
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make port 10000 available to the world outside this container
# Render will automatically map this to its public port
EXPOSE 10000

# Run the Gunicorn server
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:10000", "app:app"]