# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY main.py ./
COPY src/ ./src/
ENV PYTHONPATH="${PYTHONPATH}:/src"

# Use Gunicorn to serve Dash (recommended for production)
# CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:app"]
CMD ["python3", "main.py"]

