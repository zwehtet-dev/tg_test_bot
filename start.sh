#!/bin/bash

# THB ⇄ MMK Exchange Bot - Quick Start Script
# This script helps you quickly deploy the bot on your VPS

set -e

echo "=========================================="
echo "THB ⇄ MMK Exchange Bot - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your actual credentials:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - ADMIN_GROUP_ID"
    echo "   - OPENAI_API_KEY"
    echo "   - BALANCE_TOPIC_ID (default: 3)"
    echo ""
    echo "Run this command to edit:"
    echo "   nano .env"
    echo ""
    read -p "Press Enter after you've configured .env file..."
fi

echo "✅ .env file exists"
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data receipts admin_receipts logs
echo "✅ Directories created"
echo ""

# Build and start the bot
echo "Building and starting the bot..."
echo "This may take a few minutes on first run..."
docker-compose build --no-cache
docker-compose up -d

echo ""
echo "=========================================="
echo "✅ Bot deployment complete!"
echo "=========================================="
echo ""
echo "The bot is now running with:"
echo "  • 9 bank accounts initialized"
echo "  • Balance topic ID: 3 (or your configured value)"
echo "  • Exchange rate: 121.5"
echo ""
echo "Useful commands:"
echo "  • View logs:        docker-compose logs -f"
echo "  • Stop bot:         docker-compose down"
echo "  • Restart bot:      docker-compose restart"
echo "  • Check status:     docker-compose ps"
echo ""
echo "For more information, see DEPLOYMENT.md"
echo ""
