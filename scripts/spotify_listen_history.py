#!/usr/bin/env python3

import os
import time
import csv
import spotipy
from datetime import datetime
import logging
import sys
from spotify_auth import get_spotify_tokens

def setup_logging(is_background=False):
    """Set up logging configuration based on whether we're running in background"""
    handlers = [logging.FileHandler('../data/spotify_listen_history.log')]
    
    # Only add StreamHandler if not running in background
    if not is_background:
        handlers.append(logging.StreamHandler())
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

class SpotifyHistoryCollector:
    def __init__(self):
        self.scope = "user-read-currently-playing user-read-recently-played"
        access_token, refresh_token = get_spotify_tokens()
        self.sp = spotipy.Spotify(auth=access_token)
        self.csv_file = "../data/spotify_listen_history.csv"
        self.last_track_id = None
        self.initialize_csv()

    def initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'track_id', 'track_name', 'artist_name',
                    'album_name', 'duration_ms', 'popularity'
                ])

    def get_current_track(self):
        """Get currently playing track"""
        try:
            current = self.sp.current_user_playing_track()
            if current and current.get('item'):
                return current['item']
            return None
        except Exception as e:
            logging.error(f"Error getting current track: {e}")
            # If we get an authentication error, refresh the token
            if "token expired" in str(e).lower() or "unauthorized" in str(e).lower():
                logging.info("Refreshing access token...")
                access_token, _ = get_spotify_tokens()
                self.sp = spotipy.Spotify(auth=access_token)
                return self.get_current_track()
            return None

    def save_track(self, track):
        """Save track information to CSV"""
        try:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    track['id'],
                    track['name'],
                    track['artists'][0]['name'],
                    track['album']['name'],
                    track['duration_ms'],
                    track['popularity']
                ])
            logging.info(f"Saved track: {track['name']} by {track['artists'][0]['name']}")
        except Exception as e:
            logging.error(f"Error saving track: {e}")

    def run(self):
        """Main loop to collect listening history"""
        logging.info("Starting Spotify History Collector")
        while True:
            try:
                current_track = self.get_current_track()
                if current_track and current_track['id'] != self.last_track_id:
                    self.save_track(current_track)
                    self.last_track_id = current_track['id']
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait longer if there's an error

if __name__ == "__main__":
    # Check if running in background by looking for command line argument
    is_background = "--background" in sys.argv
    setup_logging(is_background)
    
    collector = SpotifyHistoryCollector()
    collector.run() 