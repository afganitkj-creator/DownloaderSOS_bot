FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    pandoc \
    ghostscript \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for uploads and outputs
RUN mkdir -p tmp/bot_uploads tmp/bot_outputs tmp/outputs

# Run the bot only (not Streamlit, which is for web ui)
CMD ["python", "bot.py"]
