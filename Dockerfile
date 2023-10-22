# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# Install system packages required by the Django application and its dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libpango1.0-0 \
    libcairo2 \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app/
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Specify the command to run on container start
CMD ["gunicorn", "e_voting.wsgi:application"]
