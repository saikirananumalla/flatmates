# Use an official Python runtime as a base image
FROM python:3.12.0

# Set the working directory in the container
WORKDIR /

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

ENV SECRET_KEY=8f934fd44042ad36975226bed085284c227a9d9ee713425fadf7d81932773932
ENV ALGORITHM=HS256
ENV DATABASE_HOST=host.docker.internal

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*"]

