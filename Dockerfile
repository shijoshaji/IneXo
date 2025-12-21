FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if any (none for now)
# RUN apt-get update && apt-get install -y gcc

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Command to run the application
# We use 0.0.0.0 to enable access from outside the container
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
