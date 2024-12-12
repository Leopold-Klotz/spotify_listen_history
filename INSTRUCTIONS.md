# Spotify History Collector - Setup Instructions

This guide will help you set up and run the Spotify History Collector, which tracks your Spotify listening history and saves it to a CSV file.

## Prerequisites

- Python 3.x installed on your macOS system
- A Spotify account
- Git (for cloning the repository)

## Quick Setup

1. Clone the repository:
```bash
git clone [your-repository-url]
cd spotify_listen_history
```

2. Run the setup script:
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script will:
- Create or activate a virtual environment
- Install required dependencies
- Configure the launch agent
- Offer to start the collector

When you first run the collector, it will:
1. Open your browser for Spotify authentication
2. Ask you to log in to your Spotify account
3. Request permission to access your listening history
4. Save your authentication tokens securely

After the initial setup, the collector will run automatically in the background and survive system restarts.

## Manual Setup

If you prefer to set up everything manually, follow these steps:

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone [your-repository-url]
cd spotify_listen_history

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required Python packages
pip3 install -r requirements.txt
```

### 2. Make Scripts Executable

```bash
chmod +x scripts/spotify_listen_history.py
```

### 3. Configure Launch Agent

1. Open `scripts/com.user.spotify-history.plist`
2. Replace `REPLACE_WITH_FULL_PATH` with your actual path to the project
   - For example, if you cloned the repo to `/Users/username/Projects`, replace it with that path
3. Copy the Launch Agent file to your user's LaunchAgents directory:
   ```bash
   cp scripts/com.user.spotify-history.plist ~/Library/LaunchAgents/
   ```

### 4. First-Time Authentication

1. Run the script manually first to authenticate with Spotify:
   ```bash
   cd scripts
   python3 spotify_listen_history.py
   ```
2. A browser window will open asking you to log in to Spotify
3. After logging in, authorize the application to access your listening history
4. The window will close automatically, and you'll see a success message
5. Your authentication tokens will be saved securely in `~/.spotify_history_config.json`

### 5. Start the Service

Load and start the Launch Agent:
```bash
launchctl load ~/Library/LaunchAgents/com.user.spotify-history.plist
```

## Verification

1. The script should start automatically and run in the background
2. Check if the data file is being created:
   ```bash
   ls -l data/spotify_listen_history.csv
   ```

3. Monitor the logs:
   - Main script log: `spotify_listen_history.log`
   - System logs: 
     - `spotify_error.log`
     - `spotify_output.log`

## Troubleshooting

### If the script isn't running:
1. Check the log files for errors
2. Try running the script manually to check for authentication issues:
   ```bash
   cd scripts
   python3 spotify_listen_history.py
   ```
3. Verify the paths in the plist file are correct
4. Try unloading and reloading the Launch Agent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.user.spotify-history.plist
   launchctl load ~/Library/LaunchAgents/com.user.spotify-history.plist
   ```

### Authentication Issues:
- If you see authentication errors, try removing the config file and authenticating again:
  ```bash
  rm ~/.spotify_history_config.json
  cd scripts
  python3 spotify_listen_history.py
  ```

## Data Collection

The script will:
- Check your currently playing track every 30 seconds
- Save new tracks to `data/spotify_listen_history.csv`
- Include the following information for each track:
  - Timestamp
  - Track ID
  - Track Name
  - Artist Name
  - Album Name
  - Duration
  - Popularity

## Stopping the Service

To stop the service:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.spotify-history.plist
``` 