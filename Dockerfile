# Use an official Python runtime as a base image
FROM python:3.10

# Install PostgreSQL development libraries
RUN apt-get update && apt-get install -y libpq-dev

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Create a home directory for the dynamically assigned user, so we can avoid permission issues
ARG UID
ARG GID
RUN mkdir -p /home/dynamicuser && \
    echo "dynamicuser:x:${UID}:${GID}:Dynamic User,,,:/home/dynamicuser:/bin/bash" >> /etc/passwd && \
    echo "dynamicuser:x:${GID}:" >> /etc/group && \
    chown ${UID}:${GID} -R /home/dynamicuser

ENV HOME=/home/dynamicuser

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Disable virtual environments creation by Poetry
RUN poetry config virtualenvs.create false

# Install the required packages
RUN poetry install --no-interaction --no-ansi

RUN chown -R ${UID}:${GID} /home/dynamicuser

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
