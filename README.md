# SPOT USER BOT

<div align="center">
  <img src="https://i.postimg.cc/sD3B2JcP/Frame-7-7.png" alt="SPOT USER BOT" width="400">
</div>

## NSFW Telegram Bot Detector 🔍

> **Advanced Telegram Bot for detecting NSFW content in user profile pictures within groups**

## Background

This project was created out of necessity when I needed a compact NSFW detection solution for Telegram groups but had limited disk quota on server. Traditional NSFW detection models are often hundreds of megabytes or even gigabytes in size, making them impractical for resource-constrained environments.

This bot uses an optimized TensorFlow Lite model (INT8 quantized) based on the NSFW model by GantMan that's only a few megabytes while maintaining good accuracy for detecting inappropriate user bots with NSFW profile pictures in groups.

## ✨ Features

- 🎯 **Lightweight**: Ultra-small model size optimized for limited storage (~8-10MB)
- ⚡ **Fast Detection**: Efficient TensorFlow Lite inference (100-300ms per image)
- 🔄 **Async Processing**: Non-blocking NSFW detection with queue system
- 📊 **Detailed Analysis**: Confidence scores and category breakdown
- 🚨 **Admin Alerts**: Immediate notifications to group administrator
- 📝 **False Alert Reporting**: Built-in feedback system for improving accuracy
- 🌐 **Webhook Support**: Production-ready with webhook deployment
- 💾 **Database Integration**: PostgreSQL with async operations
- 🎛️ **Group Management**: Per-group settings with kick/delete options
- 🔒 **Permission Control**: Automatic permission checking and validation
- 📢 **Admin Commands**: Built-in announcement system for developers
- 🏗️ **Modular Architecture**: Clean separation of concerns with handlers

## 🏗️ Project Structure

The project follows a clean, modular architecture with separated concerns:

```
├── bot/                        # Main bot package
│   ├── main.py                 # Bot initialization and startup logic
│   ├── settings.py             # Configuration and environment variables
│   ├── database.py             # Database models and connection
│   ├── detect.py               # NSFW detection engine
│   ├── nsfw_worker.py          # Background worker for async processing
│   ├── keyboards.py            # Telegram keyboard layouts
│   ├── utils.py                # Utility functions and callback data
│   ├── handlers/               # Message and event handlers
│   │   ├── commands.py         # Command handlers (/start, /say)
│   │   ├── messages.py         # Message processing and group monitoring
│   │   ├── callback_queries.py # Inline button handlers
│   │   ├── chat_members.py     # Group membership events
│   │   └── common.py           # Shared handler functions
│   └── migrations/             # Database migrations
├── model/                      # AI model files
│   └── model_int8.tflite       # Quantized TensorFlow Lite model
├── run.py                      # Main application launcher
├── pyproject.toml              # Modern Python project configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Core Components

- **`bot/main.py`** - Application entry point with bot initialization and lifecycle management
- **`bot/handlers/`** - Modular handlers for different types of Telegram events
- **`bot/nsfw_worker.py`** - Asynchronous background worker for NSFW detection
- **`bot/database.py`** - Database models with async support and connection pooling
- **`run.py`** - Production launcher with webhook/polling support

## Model Categories

The detection model classifies images into 5 categories:

- **drawings** - Artistic/cartoon content
- **hentai** - Explicit animated content
- **neutral** - Safe content
- **porn** - Explicit real content
- **sexy** - Suggestive content

NSFW threshold combines: `porn` + `hentai` + `sexy` probabilities

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/abduakhads/spot-userbot.git
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
```

### 4. Database Setup

Ensure PostgreSQL is running and create your database:

```sql
CREATE DATABASE your_database_name;
CREATE USER your_database_user WITH PASSWORD 'your_database_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_database_user;
```
> Tables are created automatically at start of the bot.

### 5. Running the Bot

#### Development Mode (Polling)

```bash
python run.py
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
python run.py
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

## 📱 Usage & Features

### Basic Usage

1. **Start the bot**: Send `/start` to your bot in a private chat
2. **Add to group**: Add the bot to your supergroup
3. **Automatic monitoring**: The bot monitors user profile pictures and alerts admin of NSFW content
4. **Manage settings**: Use "My Groups 👥" button to configure per-group settings

### Advanced Features

#### Group Management Interface

- **My Groups 👥**: View and manage all groups the bot monitors
- **Individual Settings**: Configure kick and delete options per group
- **Permission Validation**: Automatic checking of bot permissions

#### Per-Group Settings

- **Kick User Bots**: Automatically ban users with NSFW profile pictures
- **Delete Messages**: Remove messages from users with NSFW content
- **Smart Permission Handling**: Settings auto-disable if bot lacks permissions

#### Admin Tools

- **False Alert Reporting**: Users can report false positives via inline buttons
- **Developer Announcements**: Broadcast messages to all bot users
- **Detailed Logging**: Comprehensive detection results with confidence scores

#### Enhanced Detection

- **Markdown-Safe Reporting**: Proper escaping of special characters in reports
- **Link Generation**: Direct links to flagged messages and profiles
- **Multi-Category Analysis**: Detailed breakdown of detection categories

### Available Commands

#### User Commands

- `/start` - Initialize the bot and get welcome message
- **My Groups 👥** (button) - View and manage monitored groups

#### Developer/Admin Commands

- `/say <message>` - Broadcast announcement to all bot users (developer only)

### Bot Permissions

The bot requires the following permissions for full functionality:

- **Restrict Members** - To kick users with NSFW content (if enabled)
- **Delete Messages** - To remove messages with NSFW content (if enabled)

> **Note**: Settings automatically disable if the bot lacks required permissions

## 🔧 Technical Details

### Architecture Improvements

- **Modular Handler System**: Clean separation of commands, messages, callbacks, and chat events
- **Async Queue Processing**: Background workers prevent blocking on detection tasks
- **Database Connection Pooling**: Efficient PostgreSQL connections with peewee-async
- **Smart Permission Management**: Automatic detection and handling of bot permissions
- **Migration System**: Structured database schema updates
- **Enhanced Error Handling**: Comprehensive exception handling and fallbacks

### New Components

#### Handler Structure

- **`commands.py`**: `/start`, `/say` (announcements), and other bot commands
- **`messages.py`**: Group message processing and profile picture detection
- **`callback_queries.py`**: Inline keyboard interactions and settings management
- **`chat_members.py`**: Group join/leave events and permission changes
- **`common.py`**: Shared functionality for group management

#### Database Enhancements

- **User Management**: Track all users for announcements
- **Group Settings**: Per-group configuration storage
- **Migration Support**: Structured schema updates
- **Async Operations**: Non-blocking database interactions

### Performance Metrics

- **Model Size**: ~8-10MB (INT8 quantized TensorFlow Lite)
- **Inference Time**: ~100-300ms per image
- **Memory Usage**: Minimal RAM footprint with efficient cleanup
- **Database**: Connection pooling with keepalive for stability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🛠️ Troubleshooting

### Common Issues

1. **Model not found**: Ensure `model_int8.tflite` is in the `model/` directory
2. **Database connection**: Verify PostgreSQL credentials and connectivity
3. **Webhook issues**: Check firewall settings and SSL certificate (Telegram enforces HTTPS)
4. **Permission errors**: Ensure bot has admin rights with restrict/delete permissions
5. **Memory errors**: Reduce worker count in `main.py` if needed

### Debug Mode

Enable detailed logging by setting environment variables:

```bash
export DEBUG=true
python run.py
```

### Database Migrations

You need to manage migrations manually - create migration file under bot/migrations/ (if models are modified) then/else just run: 

```bash
python bot/migrations/<file_name>.py
```

## 📋 Recent Updates

### Version 2.0 Features

- ✅ Complete restructuring into modular package architecture
- ✅ Advanced group management with per-group settings
- ✅ Enhanced permission system with automatic validation
- ✅ Improved user interface with inline keyboards
- ✅ Database migrations
- ✅ Enhanced error handling and logging
- ✅ Production-ready webhook support
- ✅ Developer announcement system

### Migration from v1.0

If upgrading from the older single-file version, you need to migrate database.

## 🙏 Acknowledgments

- [GantMan/nsfw_model](https://github.com/GantMan/nsfw_model) - For the base NSFW detection model
- [aiogram](https://github.com/aiogram/aiogram) - Modern Telegram Bot API framework
- TensorFlow Lite team - For the efficient inference engine
