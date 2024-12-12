#!/bin/bash

# Color codes for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the absolute path of the project directory early for the check
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Check for existing processes
check_existing_process() {
    local PIDS=$(pgrep -f "python3.*spotify_listen_history.py")
    if [ -n "$PIDS" ]; then
        echo -e "\n${RED}Warning: Spotify History Collector is already running!${NC}"
        echo -e "Running processes: $PIDS"
        echo -e "\nYou have two options:"
        echo -e "${BLUE}1. Stop the existing process:${NC}"
        echo -e "   Run: ${PROJECT_DIR}/scripts/kill_collector.sh"
        echo -e "   Then run this setup script again"
        echo -e "\n${BLUE}2. Continue using the existing process:${NC}"
        echo -e "   View logs: tail -f ${PROJECT_DIR}/data/spotify_listen_history.log"
        echo -e "   Check status: pgrep -fl 'python3.*spotify_listen_history.py'"
        echo -e "\nExiting setup..."
        exit 1
    fi
}

# Function to show progress
show_progress() {
    local progress=$1
    local status=$2
    local width=50
    local completed=$((width * progress / 100))
    local remaining=$((width - completed))
    
    printf "\r[${BLUE}"
    printf "%${completed}s" | tr ' ' '='
    printf "${NC}"
    printf "%${remaining}s" | tr ' ' '-'
    printf "] ${progress}%% : ${status}"
}

# Function to verify the collector is running
verify_collector_running() {
    # Wait a bit for process to start
    sleep 2
    if pgrep -f "python3.*spotify_listen_history.py" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check for existing processes before starting
check_existing_process

echo -e "${GREEN}Starting Spotify History Collector Setup...${NC}\n"

# Step 1: Virtual Environment Setup (25%)
show_progress 0 "Setting up virtual environment..."
VENV_DIR="${PROJECT_DIR}/venv"
if [ -d "${VENV_DIR}" ]; then
    source "${VENV_DIR}/bin/activate"
    show_progress 25 "Activated existing virtual environment"
else
    python3 -m venv "${VENV_DIR}"
    source "${VENV_DIR}/bin/activate"
    show_progress 25 "Created and activated new virtual environment"
fi
echo -e "\n"

# Step 2: Install/Update Requirements (50%)
show_progress 25 "Installing/updating requirements..."
pip install -r "${PROJECT_DIR}/requirements.txt"
show_progress 50 "Requirements installed/updated"
echo -e "\n"

# Step 3: Configure plist file (75%)
show_progress 50 "Configuring launch agent..."
PLIST_TEMPLATE="${PROJECT_DIR}/scripts/com.user.spotify-history.plist"
PLIST_DEST="${HOME}/Library/LaunchAgents/com.user.spotify-history.plist"

# Make scripts executable
chmod +x "${PROJECT_DIR}/scripts/spotify_listen_history.py"
chmod +x "${PROJECT_DIR}/scripts/kill_collector.sh"

# Update plist file with correct paths
sed "s|REPLACE_WITH_FULL_PATH|${PROJECT_DIR}|g" "${PLIST_TEMPLATE}" > "${PLIST_DEST}"
show_progress 75 "Launch agent configured"
echo -e "\n"

# Step 4: Final setup (100%)
show_progress 75 "Finalizing setup..."
mkdir -p "${PROJECT_DIR}/data"
show_progress 100 "Setup complete!"
echo -e "\n"

# Print summary
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "Virtual Environment: ${VENV_DIR}"
echo "Launch Agent: ${PLIST_DEST}"
echo "Data Directory: ${PROJECT_DIR}/data"
echo

# Ask to run the collector
read -p "Would you like to start the Spotify History Collector now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\nStarting Spotify History Collector..."
    cd "${PROJECT_DIR}/scripts"
    
    # Start authentication process
    python3 spotify_listen_history.py &
    
    # Wait for authentication and verify process is running
    sleep 5  # Give time for authentication
    
    if verify_collector_running; then
        echo -e "\n${GREEN}Spotify History Collector is now running in the background!${NC}"
        echo -e "\nUseful commands:"
        echo -e "${BLUE}Check if it's running:${NC}"
        echo "pgrep -fl 'python3.*spotify_listen_history.py'"
        echo -e "\n${BLUE}View the log file:${NC}"
        echo "tail -f ${PROJECT_DIR}/data/spotify_listen_history.log"
        echo -e "\n${BLUE}Stop the collector:${NC}"
        echo "${PROJECT_DIR}/scripts/kill_collector.sh"
    else
        echo -e "\n${RED}Error: Collector failed to start properly.${NC}"
        echo "Please check the log file for errors:"
        echo "tail -f ${PROJECT_DIR}/spotify_listen_history.log"
    fi
else
    echo -e "\nTo start the collector later, run:"
    echo "cd ${PROJECT_DIR}/scripts"
    echo "python3 spotify_listen_history.py"
fi 