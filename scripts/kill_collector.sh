#!/bin/bash

# Color codes for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${RED}Stopping Spotify History Collector...${NC}"

# Unload the launch agent
launchctl unload ~/Library/LaunchAgents/com.user.spotify-history.plist 2>/dev/null

# Find and kill any running instances of the collector
PIDS=$(pgrep -f "python3.*spotify_listen_history.py")

if [ -n "$PIDS" ]; then
    echo "Found running collector processes: $PIDS"
    echo "Killing processes..."
    kill $PIDS
    sleep 1
    # Check if processes are still running and force kill if necessary
    if pgrep -f "python3.*spotify_listen_history.py" >/dev/null; then
        echo "Forcing kill..."
        kill -9 $PIDS
    fi
    echo -e "${GREEN}Collector processes stopped successfully${NC}"
else
    echo "No running collector processes found"
fi

echo "To start the collector again, run:"
echo "launchctl load ~/Library/LaunchAgents/com.user.spotify-history.plist" 