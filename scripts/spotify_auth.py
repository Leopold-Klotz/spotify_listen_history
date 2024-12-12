#!/usr/bin/env python3

import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import requests
import secrets
import base64
import hashlib
import signal
from datetime import datetime, timedelta

CONFIG_FILE = os.path.expanduser('~/.spotify_history_config.json')

class AuthenticationTimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise AuthenticationTimeoutError("Authentication timed out after 60 seconds. Please try again and approve the Spotify login promptly.")

def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    return code_verifier, code_challenge

class SpotifyAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if 'code' in query_components:
            self.server.auth_code = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authentication successful! You can close this window.")
        elif 'error' in query_components:
            self.server.auth_error = query_components['error'][0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"Authentication failed: {query_components['error'][0]}".encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authentication failed: Unknown error")

    def log_message(self, format, *args):
        # Suppress logging
        pass

def get_spotify_tokens():
    """Get or refresh Spotify tokens"""
    # Client ID for the Spotify History Collector app
    CLIENT_ID = "2e98209a9de244a389f1d0ba1711f6a9"  # Public client ID for this app
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            
        # Check if tokens are still valid
        if datetime.now() < datetime.fromisoformat(config['expires_at']):
            return config['access_token'], config['refresh_token']
            
        # Refresh token if expired
        if 'refresh_token' in config:
            response = requests.post('https://accounts.spotify.com/api/token', data={
                'grant_type': 'refresh_token',
                'refresh_token': config['refresh_token'],
                'client_id': CLIENT_ID
            })
            
            if response.status_code == 200:
                token_info = response.json()
                config.update({
                    'access_token': token_info['access_token'],
                    'expires_at': (datetime.now() + timedelta(seconds=token_info['expires_in'])).isoformat()
                })
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f)
                return config['access_token'], config['refresh_token']

    # If no valid tokens exist, start new authentication flow
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Start local server to receive callback
    server = HTTPServer(('localhost', 8888), SpotifyAuthHandler)
    server.auth_code = None
    server.auth_error = None
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)  # Set 60-second timeout
    
    try:
        # Construct authorization URL
        params = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': 'http://localhost:8888/callback',
            'code_challenge_method': 'S256',
            'code_challenge': code_challenge,
            'scope': 'user-read-currently-playing user-read-recently-played'
        }
        auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
        
        # Open browser for user authentication
        print("\nOpening browser for Spotify authentication...")
        print("Please log in and approve the permissions request within 60 seconds.")
        webbrowser.open(auth_url)
        
        # Wait for callback
        while server.auth_code is None and server.auth_error is None:
            server.handle_request()
        
        # Cancel the timeout
        signal.alarm(0)
        
        if server.auth_error:
            raise Exception(f"Authentication failed: {server.auth_error}")
        
        # Exchange code for tokens
        response = requests.post('https://accounts.spotify.com/api/token', data={
            'client_id': CLIENT_ID,
            'grant_type': 'authorization_code',
            'code': server.auth_code,
            'redirect_uri': 'http://localhost:8888/callback',
            'code_verifier': code_verifier
        })
        
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")
        
        token_info = response.json()
        config = {
            'access_token': token_info['access_token'],
            'refresh_token': token_info['refresh_token'],
            'expires_at': (datetime.now() + timedelta(seconds=token_info['expires_in'])).isoformat()
        }
        
        # Save tokens
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        
        return token_info['access_token'], token_info['refresh_token']
        
    except AuthenticationTimeoutError as e:
        print(f"\nError: {str(e)}")
        raise SystemExit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        raise SystemExit(1)
    finally:
        signal.alarm(0)  # Ensure timeout is cancelled
        server.server_close()

if __name__ == '__main__':
    try:
        access_token, refresh_token = get_spotify_tokens()
        print("Authentication successful!")
        print(f"Tokens saved to {CONFIG_FILE}")
    except SystemExit:
        pass  # Error message already printed
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1) 