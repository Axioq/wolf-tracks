# Attempting to use smaller version of python
# "slim" is a minimal image with just enough to run python
FROM python:3.12-slim

# Setting the working directory inside the container
WORKDIR /app

# Copy requirements first
# If requirements.txt hasn't changed, Docker should skill reinstalling packages

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project code
COPY . .

# Default command when the container starts
CMD ["python", "scripts/run_pipeline.py"]