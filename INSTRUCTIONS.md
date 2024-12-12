# Spotify History Collector - Setup Instructions

This guide will help you set up and run the Spotify History Collector, which tracks your Spotify listening history and saves it to a CSV file.

## Prerequisites

- Python 3.x installed on your macOS system
- A Spotify account
- Git (for cloning the repository)

## Setup Steps

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone [your-repository-url]
cd spotify_listen_history

# Install required Python package
pip3 install -r requirements.txt
```

### 2. Set Up Spotify Developer Account

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app name and description
5. Once created, note down your:
   - Client ID
   - Client Secret
6. Click "Edit Settings"
7. Add `http://localhost:8888/callback` to the "Redirect URIs" section
8. Save the settings

### 3. Configure Spotify API Credentials

1. Open `scripts/set_spotify_api_credentials.sh`
2. Replace the placeholder values with your actual Spotify API credentials:
   ```bash
   export SPOTIPY_CLIENT_ID="your_actual_client_id"
   export SPOTIPY_CLIENT_SECRET="your_actual_client_secret"
   ```
3. Make the script executable:
   ```bash
   chmod +x scripts/set_spotify_api_credentials.sh
   chmod +x scripts/spotify_listen_history.py
   ```

### 4. Configure Launch Agent

1. Open `scripts/com.user.spotify-history.plist`
2. Replace `REPLACE_WITH_FULL_PATH` with your actual path to the project
   - For example, if you cloned the repo to `/Users/username/Projects`, replace it with that path
3. Copy the Launch Agent file to your user's LaunchAgents directory:
   ```bash
   cp scripts/com.user.spotify-history.plist ~/Library/LaunchAgents/
   ```

### 5. Start the Service

1. First, load the Spotify credentials:
   ```bash
   source scripts/set_spotify_api_credentials.sh
   ```

2. Load and start the Launch Agent:
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
2. Ensure the Spotify credentials are correct
3. Verify the paths in the plist file are correct
4. Try unloading and reloading the Launch Agent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.user.spotify-history.plist
   launchctl load ~/Library/LaunchAgents/com.user.spotify-history.plist
   ```

### Authentication Issues:
- If you see authentication errors, ensure your Spotify credentials are correct
- Try running the script manually first to complete the OAuth flow:
  ```bash
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