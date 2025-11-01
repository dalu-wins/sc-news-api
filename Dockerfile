# 1. Base image
FROM python:3.12-slim

# 2. Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    wget \
    unzip \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Copy Python requirements
COPY src/requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy all code
COPY src/ .

# 7. Install matching ChromeDriver
RUN CHROME_VERSION=$(chromium --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+') && \
    echo "Detected Chromium version: $CHROME_VERSION" && \
    DRIVER_URL=$(wget -qO- "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json" \
        | jq -r ".builds[\"$CHROME_VERSION\"].version as \$v | \"https://storage.googleapis.com/chrome-for-testing-public/\(\$v)/linux64/chromedriver-linux64.zip\"") && \
    echo "Downloading ChromeDriver from $DRIVER_URL" && \
    wget -O /tmp/chromedriver.zip "$DRIVER_URL" && \
    unzip /tmp/chromedriver.zip -d /tmp && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

# 8. Set environment variables for Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="$PATH:/usr/bin"

# 9. Expose port
EXPOSE 8000

# 10. Start command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]