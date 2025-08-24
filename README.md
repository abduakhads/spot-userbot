# SPOT USER BOT

<div align="center">
  <img src="https://i.postimg.cc/1XybMH2J/Frame-7-4.png" alt="SPOT USER BOT" width="400">
</div>

## NSFW Telegram Bot Detector 🔍

> Light Telegram Bot to spot user bots in groups with NSFW content in their profile picture

## Background

This project was created out of necessity when I needed a compact NSFW detection solution for Telegram groups but had limited disk quota on server. Traditional NSFW detection models are often hundreds of megabytes or even gigabytes in size, making them impractical for resource-constrained environments.

This bot uses an optimized TensorFlow Lite model (INT8 quantized) based on the [NSFW model by GantMan](https://github.com/GantMan/nsfw_model) that's only a few megabytes while maintaining good accuracy for detecting inappropriate userbots with NSFW in profile pictures in groups.

## Features

- 🎯 **Lightweight**: Ultra-small model size optimized for limited storage
- ⚡ **Fast Detection**: Efficient TensorFlow Lite inference
- 🔄 **Async Processing**: Non-blocking NSFW detection with queue system
- 📊 **Detailed Analysis**: Confidence scores and category breakdown
- 🚨 **Admin Alerts**: Immediate notifications to group administrator
- 📝 **False Alert Reporting**: Built-in feedback system for improving accuracy
- 🌐 **Webhook Support**: Production-ready with webhook deployment
- 💾 **Database Integration**: PostgreSQL for persistent user and group data

## Project Structure

### Core Files

- **`bot.py`** - Main bot application with message handlers and NSFW worker
- **`detect.py`** - NSFW detection engine using TensorFlow Lite
- **`database.py`** - Database models and PostgreSQL connection
- **`model_int8.tflite`** - Quantized TensorFlow Lite model for NSFW detection

### Utility Files

- **`run.py`** - Testing script for the detection model and validation
- **`pyproject.toml`** - Project dependencies and metadata

### Configuration Files

- **`.env`** - Environment variables (create from template below)
- **`uv.lock`** - Dependency lock file

## Model Categories

The detection model classifies images into 5 categories:

- **drawings** - Artistic/cartoon content
- **hentai** - Explicit animated content
- **neutral** - Safe content
- **porn** - Explicit real content
- **sexy** - Suggestive content

NSFW threshold combines: `porn` + `hentai` + `sexy` probabilities

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd nsftbot
```

### 2. Install Dependencies

Using uv (recommended):

```bash
uv sync
```

Or using pip:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file with the following variables:

```env
# Bot Configuration
BOT_TOKEN=your_bot_token_from_botfather
DEVELOPER_ID=your_telegram_user_id

# Database Configuration
DATABASE_NAME=your_database_name
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=your_database_host
DATABASE_PORT=5432

# Webhook Configuration (Optional)
USE_WEBHOOK=false
WEBHOOK_SECRET=your_webhook_secret
BASE_WEBHOOK_URL=https://yourdomain.com

# Debug Mode (Optional)
DEBUG=false
```

### 4. Database Setup

Ensure PostgreSQL is running and create your database:

```sql
CREATE DATABASE your_database_name;
CREATE USER your_database_user WITH PASSWORD 'your_database_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_database_user;
```

### 5. Running the Bot

#### Development Mode (Polling)

```bash
python bot.py
```

#### Production Mode (Webhook)

Set `USE_WEBHOOK=true` in your `.env` file and configure your web server.

## Deployment Options

### Option 1: Nginx Reverse Proxy (Recommended for Production)

Add this location block to your Nginx configuration:

```nginx
location /webhook {
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_redirect off;
    proxy_buffering off;
    proxy_pass http://127.0.0.1:8080;
}
```

Then restart Nginx and run the bot:

```bash
python bot.py
```

### Option 2: Development/Testing with Tunneling

#### Using ngrok:

```bash
# Install ngrok and run
ngrok http 8080
# Copy the HTTPS URL to BASE_WEBHOOK_URL in .env
```

#### Using jprq:

```bash
# Install jprq and run
jprq http 8080
# Copy the HTTPS URL to BASE_WEBHOOK_URL in .env
```

## Usage

1. **Start the bot**: Send `/start` to your bot in a private chat
2. **Add to group**: Add the bot to your supergroup (no need to add as admin)
3. **Automatic monitoring**: The bot will monitor potential userbot profile pictures and alert admin of NSFW content
4. **False alerts**: Admin can report false positives to developer using the inline button

## Testing the Model

Use `run.py` to test the detection model on sample images:

```bash
python run.py
```

This will process all images in the `img/` directory and display detailed classification results.

## Technical Details

### Architecture

- **Async Queue System**: NSFW detection runs in background workers to avoid blocking
- **Thread-Safe Model**: TensorFlow Lite interpreter with proper locking
- **Memory Optimization**: Efficient image preprocessing and cleanup
- **Database Async**: Non-blocking database operations with peewee-async

### Performance

- **Model Size**: ~8-10MB (INT8 quantized)
- **Inference Time**: ~100-300ms per image
- **Memory Usage**: Minimal RAM footprint
- **Concurrent Processing**: 4 worker threads by default

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Troubleshooting

### Common Issues

1. **Model not found**: Ensure `model_int8.tflite` is in the project root
2. **Database connection**: Verify PostgreSQL credentials and connectivity
3. **Webhook issues**: Check firewall settings and SSL certificate (Telegram enforces SSL)
4. **Memory errors**: Reduce worker count or optimize batch processing
