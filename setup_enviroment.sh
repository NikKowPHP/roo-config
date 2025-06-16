#!/bin/bash

# This script fully automates the setup of the project environment for Ubuntu.
# It checks for and installs dependencies (Python, Docker, Docker Compose) before
# setting up the Python virtual environment and the project's services.
# It will exit immediately if any command fails.
set -e

echo "--- Starting Project Environment Setup ---"

# --- Step 1: Check for and Install Dependencies (for Ubuntu) ---
echo "🔎 Checking for required dependencies..."

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check for Python 3
if ! command_exists python3 || ! command_exists python3-venv; then
    echo "🐍 Python 3 and/or python3-venv not found. Attempting to install..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip
    echo "✅ Python 3 installed."
fi

# Check for Docker and Docker Compose Plugin
if ! command_exists docker; then
    echo "🐳 Docker not found. Attempting to install..."
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    # Install Docker Engine, CLI, Containerd, and Docker Compose plugin
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    echo "✅ Docker and Docker Compose plugin installed."

    # Add the current user to the 'docker' group to avoid using 'sudo' with Docker
    echo "👤 Adding current user to the 'docker' group..."
    sudo usermod -aG docker $USER
    echo "⚠️ IMPORTANT: For the Docker group change to take effect, you must either"
    echo "   1. Log out and log back in."
    echo "   2. Start a new shell."
    echo "   3. Or run 'newgrp docker' in this terminal to apply it temporarily."
fi

echo "✅ All dependencies are present."

# --- Step 2: Clean up old virtual environment ---
if [ -d ".venv" ]; then
  echo "🧹 Found an old .venv directory. Removing it for a clean setup..."
  rm -rf .venv
fi

# --- Step 3: Create a fresh Python virtual environment ---
echo "🐍 Creating new Python virtual environment in './.venv'..."
python3 -m venv .venv

# --- Step 4: Activate the environment for this script's context ---
echo "🚀 Activating the virtual environment for installation..."
source .venv/bin/activate

# --- Step 5: Install/Upgrade core packaging tools ---
echo "📦 Upgrading pip and installing wheel..."
pip install --upgrade pip wheel

# --- Step 6: Install dependencies into the new environment ---
echo "📦 Installing project dependencies from requirements.txt..."
pip install -r requirements.txt

# --- Step 7: Start Docker services ---
echo "🐳 Starting Qdrant vector database via Docker Compose..."
# Use 'docker compose' (with a space), which is the modern command.
# The user might need to start a new shell if Docker was just installed.
# We will run it with 'sudo' just in case the group permissions haven't propagated yet.
if groups | grep &>/dev/null '\bdocker\b'; then
    docker compose up --build -d
else
    echo "Running 'docker compose' with sudo as user is not yet in the docker group for this session."
    sudo docker compose up --build -d
fi

# --- Step 8: Initialize the Code Context Tool (CCT) ---
echo "🧠 Initializing and indexing the codebase with the CCT..."
# This ensures the config file exists without user interaction.
cct init --force
# This command scans the entire project and loads it into the AI's memory (Qdrant).
cct index

echo ""
echo "--- ✅ Setup Complete! ---"
echo ""
echo "Your environment is ready. Here's what to do next:"
echo ""
echo "1. If you haven't already, run './copy_script.sh' to link agents to Roo."
echo ""
echo "2. **IMPORTANT FOR VS CODE:** To make the Roo extension work correctly,"
echo "   you MUST select the new interpreter:"
echo "   - Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P)"
echo "   - Type and select: 'Python: Select Interpreter'"
echo "   - Choose the one that says './.venv/bin/python' (It should be recommended)."
echo ""