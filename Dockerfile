# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies required for compiling Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# We use a virtual env to isolate dependencies for easy copying later
RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt


# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.11-slim

# 1. Set Critical Environment Variables
ENV TZ=UTC
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Install System Dependencies
# - cron: The background timer
# - tzdata: Timezone data (to ensure UTC works)
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && ln -fs /usr/share/zoneinfo/UTC /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

# 3. Set Working Directory
WORKDIR /app

# 4. Copy Dependencies from Builder Stage
COPY --from=builder /opt/venv /opt/venv

# 5. Copy Application Code
# We copy the specific folders to keep things clean
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY cron/ ./cron/
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .

# 6. Setup Cron Job
# - Copy the config file to the cron.d directory
# - Set permissions (0644 is strict requirement for cron)
RUN cp cron/2fa_cron /etc/cron.d/2fa_cron && \
    chmod 0644 /etc/cron.d/2fa_cron

# 7. Create Volume Mount Points
# We create these folders so permissions are set correctly
RUN mkdir -p /data /cron && \
    chmod 755 /data /cron

# 8. Expose the API Port
EXPOSE 8080

# 9. Start Everything
# We use a shell command to start BOTH services:
# "cron" starts the timer daemon in background
# "uvicorn" starts the web server in foreground
CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"]