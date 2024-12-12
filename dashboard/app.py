from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)

def load_listening_data():
    """Load and process the listening history CSV"""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'spotify_listen_history.csv')
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def calculate_stats(df, time_period=None):
    """Calculate listening statistics for a given time period"""
    if time_period:
        now = datetime.now()
        if time_period == 'month':
            start_date = now - timedelta(days=30)
        elif time_period == 'year':
            start_date = now - timedelta(days=365)
        df = df[df['timestamp'] >= start_date]

    stats = {
        'total_tracks': len(df),
        'unique_tracks': df['track_id'].nunique(),
        'total_duration_hrs': df['duration_ms'].sum() / (1000 * 60 * 60),  # Convert ms to hours
        
        # Top artists
        'top_artists': (df.groupby('artist_name')
                       .size()
                       .sort_values(ascending=False)
                       .head(10)
                       .to_dict()),
        
        # Top tracks
        'top_tracks': (df.groupby(['track_name', 'artist_name'])
                      .size()
                      .sort_values(ascending=False)
                      .head(10)
                      .to_dict()),
        
        # Top albums
        'top_albums': (df.groupby('album_name')
                      .size()
                      .sort_values(ascending=False)
                      .head(10)
                      .to_dict()),
        
        # Listening activity by hour
        'hourly_activity': (df.groupby(df['timestamp'].dt.hour)
                          .size()
                          .to_dict())
    }
    
    return stats

@app.route('/')
def index():
    """Main dashboard page"""
    df = load_listening_data()
    stats = calculate_stats(df)
    return render_template('index.html', stats=stats)

@app.route('/history')
def history():
    """Paginated listening history"""
    df = load_listening_data()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Sort by timestamp descending
    df = df.sort_values('timestamp', ascending=False)
    
    # Calculate total pages
    total_items = len(df)
    total_pages = (total_items + per_page - 1) // per_page
    
    # Get items for current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = df.iloc[start_idx:end_idx]
    
    return render_template('history.html',
                         tracks=page_items.to_dict('records'),
                         page=page,
                         total_pages=total_pages)

@app.route('/api/stats/<period>')
def get_stats(period):
    """API endpoint for getting stats for different time periods"""
    if period not in ['month', 'year', 'all']:
        return jsonify({'error': 'Invalid time period'}), 400
    
    df = load_listening_data()
    stats = calculate_stats(df, period if period != 'all' else None)
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True) 