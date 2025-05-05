#!/bin/bash
# Setup script for VirtualPackaging development environment

# Text styling
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}Setting up VirtualPackaging development environment...${NC}"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python not found. Please install Python 3.8+ and try again.${NC}"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"

# Check if Python version >= 3.8
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]]; then
    echo -e "${RED}Error: Python 3.8+ is required, but you have $PYTHON_VERSION${NC}"
    exit 1
fi

# Check if virtualenv is installed, install if not
if ! $PYTHON_CMD -m pip show virtualenv &>/dev/null; then
    echo -e "${YELLOW}Installing virtualenv...${NC}"
    $PYTHON_CMD -m pip install virtualenv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    $PYTHON_CMD -m virtualenv venv
else
    echo -e "${YELLOW}Virtual environment already exists.${NC}"
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file for API keys...${NC}"
    cat > .env << EOL
# VirtualPackaging environment configuration

# OpenAI API key
OPENAI_API_KEY=your_openai_key_here

# Anthropic API key
ANTHROPIC_API_KEY=your_anthropic_key_here

# HuggingFace API key
HF_API_KEY=your_huggingface_key_here

# Internal LLM URL (if using local LLM)
# INTERNAL_LLM_URL=http://localhost:8080/v1/completions

# Development settings
DEBUG=true
LOG_LEVEL=INFO
EOL
    echo -e "${YELLOW}Please edit .env file to add your API keys${NC}"
fi

# Post-setup message
echo -e "${BOLD}${GREEN}Setup complete!${NC}"
echo -e "${BOLD}To activate this environment in the future, run:${NC}"
echo -e "    source venv/bin/activate  ${YELLOW}# On Linux/macOS${NC}"
echo -e "    venv\\Scripts\\activate     ${YELLOW}# On Windows${NC}"
echo -e "${BOLD}To install new dependencies:${NC}"
echo -e "    pip install <package>"
echo -e "    pip freeze > requirements.txt  ${YELLOW}# To update requirements.txt${NC}"
echo -e "${BOLD}Don't forget to edit .env file with your API keys.${NC}"
