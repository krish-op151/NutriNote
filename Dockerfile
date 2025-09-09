
FROM python:3.11-slim


WORKDIR /app

# Install system dependencies, including ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# The Gunicorn 
CMD gunicorn --workers 4 --bind 0.0.0.0:$PORT app:app