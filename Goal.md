# Spotify Listening History

## Goal

I want to create a Python script that collects my Spotify listening data and stores it in a local CSV file. The script should use the Spotipy library to interact with the Spotify API and run persistently in the background on macOS, even after system restarts. Additionally, I need a bash script to set the required environment variables for Spotify API credentials.

## Requirements

- [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/)
- [Spotify API](https://developer.spotify.com/documentation/web-api/)
- [macOS](https://www.apple.com/macos/)
- [Python](https://www.python.org/)

## Directory Structure

- `spotify_listen_history/`
  - `data/`
    - `spotify_listen_history.csv`
  - `scripts/`
    - `set_spotify_api_credentials.sh`
    - `spotify_listen_history.py`

## Steps

1. Create the directory structure.
2. Create the bash script to set the required environment variables for Spotify API credentials.
3. Create the Python script to collect my Spotify listening data and store it in a local CSV file.
4. Run the Python script persistently in the background on macOS, even after system restarts.

## Next

- [ ] dashboard visualizing the listening history and showing the top artists and tracks
- [ ] implement duplicate detection to prevent double-saving tracks when script restarts
- [ ] add timestamp tracking for script stops/starts to identify potential gaps in data collection
- [ ] implement graceful shutdown to record when the script stops collecting data
- [ ] add data integrity checks to verify no duplicate entries exist in the CSV