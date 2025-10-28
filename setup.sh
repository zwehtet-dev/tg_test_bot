#!/bin/bash

# Setup script for THB ⇄ MMK Exchange Bot v2.0

set -e

echo "=================================================="
echo "THB ⇄ MMK Exchange Bot v2.0 - Setup"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Please edit .env file with your credentials:${NC}"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - OPENAI_API_KEY"
    echo "   - ADMIN_GROUP_ID"
    echo ""
    echo "Run 'nano .env' to edit"
    exit 0
fi

echo -e "${GREEN}✅ .env file found${NC}"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p data receipts admin_receipts logs
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker found${NC}"
    
    # Ask user for deployment method
    echo ""
    echo "Choose deployment method:"
    echo "1) Docker (recommended)"
    echo "2) Local Python"
    read -p "Enter choice (1 or 2): " choice
    
    if [ "$choice" = "1" ]; then
        echo ""
        echo "Building and starting Docker containers..."
        docker compose up -d
        echo ""
        echo -e "${GREEN}✅ Bot started in Docker${NC}"
        echo ""
        echo "View logs with: docker compose logs -f"
        echo "Stop with: docker compose down"
    else
        echo ""
        echo "Setting up local Python environment..."
        
        # Check if venv exists
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            echo -e "${GREEN}✅ Virtual environment created${NC}"
        fi
        
        # Activate and install
        source venv/bin/activate
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Dependencies installed${NC}"
        echo ""
        echo "Starting bot..."
        python main.py
    fi
else
    echo -e "${YELLOW}Docker not found, using local Python...${NC}"
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    fi
    
    # Activate and install
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    echo ""
    echo "Starting bot..."
    python main.py
fi
