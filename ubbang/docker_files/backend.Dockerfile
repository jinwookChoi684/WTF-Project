# backend/Dockerfile

# 1. Base Image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy and install dependencies
# Dockerfile이 밖에 있으므로, 소스 경로를 명확히 해줍니다.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy backend source code
COPY backend/ . 

# 5. Expose port and run the application
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
