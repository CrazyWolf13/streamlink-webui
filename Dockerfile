FROM node:22.9.0-bookworm-slim AS frontend-builder
WORKDIR /app/frontend/src

# Install deps and build frontend
COPY frontend/src/package.json frontend/src/yarn.lock ./
RUN yarn install
COPY frontend/src/ ./
RUN yarn build

# Set up backend
FROM python:3.13-slim-bookworm AS backend
WORKDIR /app/backend/src

COPY /backend/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /backend/src/ ./

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
# Copy frontend build to backend build
COPY --from=frontend-builder /app/frontend/ /app/frontend/

EXPOSE 8000

# Run generate_config.sh before starting the app with fastapi
CMD ["sh", "-c", "/app/start.sh"]
