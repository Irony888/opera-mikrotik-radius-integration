# Dockerfile

FROM python:3.10-slim

# Set a non-root user
RUN useradd -ms /bin/bash opera
USER opera

# Set the working directory
WORKDIR /home/opera

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Command to run the application using gunicorn with 4 workers
CMD ["gunicorn", "--workers", "4", "your_module:app"]