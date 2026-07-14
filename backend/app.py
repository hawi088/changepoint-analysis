from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import json

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')

PRICE_DATA_PATH = os.path.join(DATA_DIR, 'brent_oil_processed.csv')
EVENTS_DATA_PATH = os.path.join(DATA_DIR, 'events.csv')
CHANGE_POINT_PATH = os.path.join(DATA_DIR, 'change_point_results.csv')

# ============================================
# Data Loader Functions
# ============================================

def load_price_data():
    """Load Brent oil price data"""
    try:
        df = pd.read_csv(PRICE_DATA_PATH, parse_dates=['Date'])
        # Convert to list of dictionaries with proper date formatting
        result = []
        for _, row in df.iterrows():
            result.append({
                'Date': row['Date'].strftime('%Y-%m-%d'),
                'Price': float(row['Price']) if pd.notna(row['Price']) else None
            })
        return result
    except Exception as e:
        print(f"Error loading price data: {e}")
        return []

def load_events_data():
    """Load events data"""
    try:
        df = pd.read_csv(EVENTS_DATA_PATH, parse_dates=['Date'])
        result = []
        for _, row in df.iterrows():
            result.append({
                'Date': row['Date'].strftime('%Y-%m-%d'),
                'Event': row['Event'],
                'Category': row['Category'],
                'Description': row.get('Description', ''),
                'Expected_Impact': row.get('Expected_Impact', '')
            })
        return result
    except Exception as e:
        print(f"Error loading events data: {e}")
        return []

def load_change_points():
    """Load change point detection results"""
    try:
        df = pd.read_csv(CHANGE_POINT_PATH)
        result = []
        for _, row in df.iterrows():
            result.append({
                'change_point_date': row.get('change_point_date', ''),
                'ci_lower': row.get('ci_lower', ''),
                'ci_upper': row.get('ci_upper', ''),
                'mean_before': float(row.get('mean_before', 0)) if pd.notna(row.get('mean_before')) else None,
                'mean_after': float(row.get('mean_after', 0)) if pd.notna(row.get('mean_after')) else None,
                'price_change_pct': float(row.get('price_change_pct', 0)) if pd.notna(row.get('price_change_pct')) else None
            })
        return result
    except Exception as e:
        print(f"Error loading change points: {e}")
        return []

def get_price_by_date_range(start_date, end_date):
    """Filter price data by date range"""
    try:
        df = pd.read_csv(PRICE_DATA_PATH, parse_dates=['Date'])
        mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
        filtered = df[mask]
        result = []
        for _, row in filtered.iterrows():
            result.append({
                'Date': row['Date'].strftime('%Y-%m-%d'),
                'Price': float(row['Price']) if pd.notna(row['Price']) else None
            })
        return result
    except Exception as e:
        print(f"Error filtering price data: {e}")
        return []

def get_event_impact_summary():
    """Calculate impact metrics for events"""
    try:
        df = pd.read_csv(EVENTS_DATA_PATH, parse_dates=['Date'])
        price_df = pd.read_csv(PRICE_DATA_PATH, parse_dates=['Date'])
        
        impacts = []
        for _, event in df.iterrows():
            event_date = event['Date']
            idx = price_df[price_df['Date'] >= event_date].index
            
            if len(idx) > 0:
                pos = idx[0]
                pre_idx = max(0, pos - 30)
                post_idx = min(len(price_df) - 1, pos + 30)
                
                pre_price = price_df.iloc[pre_idx]['Price']
                post_price = price_df.iloc[post_idx]['Price']
                impact_pct = ((post_price - pre_price) / pre_price) * 100 if pre_price > 0 else 0
                
                impacts.append({
                    'event': event['Event'],
                    'date': event_date.strftime('%Y-%m-%d'),
                    'category': event['Category'],
                    'impact_pct': round(float(impact_pct), 2),
                    'pre_price': round(float(pre_price), 2),
                    'post_price': round(float(post_price), 2)
                })
        
        return impacts
    except Exception as e:
        print(f"Error calculating impacts: {e}")
        return []

# ============================================
# API Routes
# ============================================

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get historical price data"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        data = get_price_by_date_range(start_date, end_date)
    else:
        data = load_price_data()
    
    # Ensure we return a proper JSON array
    return jsonify(data)

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get events data"""
    data = load_events_data()
    return jsonify(data)

@app.route('/api/change-points', methods=['GET'])
def get_change_points():
    """Get change point detection results"""
    data = load_change_points()
    return jsonify(data)

@app.route('/api/event-impacts', methods=['GET'])
def get_event_impacts():
    """Get event impact summary"""
    data = get_event_impact_summary()
    return jsonify(data)

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get summary statistics"""
    price_data = load_price_data()
    events_data = load_events_data()
    change_points = load_change_points()
    
    if price_data:
        prices = [p['Price'] for p in price_data if p['Price'] is not None]
        summary = {
            'total_days': len(price_data),
            'price_min': round(float(min(prices)), 2) if prices else 0,
            'price_max': round(float(max(prices)), 2) if prices else 0,
            'price_mean': round(float(sum(prices) / len(prices)), 2) if prices else 0,
            'total_events': len(events_data),
            'change_points_detected': len(change_points)
        }
    else:
        summary = {
            'total_days': 0,
            'price_min': 0,
            'price_max': 0,
            'price_mean': 0,
            'total_events': 0,
            'change_points_detected': 0
        }
    
    return jsonify(summary)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/api/volatility', methods=['GET'])
def get_volatility():
    """Get volatility data"""
    try:
        df = pd.read_csv(PRICE_DATA_PATH, parse_dates=['Date'])
        # Calculate 30-day rolling volatility
        df['Log_Return'] = np.log(df['Price'] / df['Price'].shift(1))
        df['Volatility_30'] = df['Log_Return'].rolling(window=30).std() * np.sqrt(252)
        
        result = []
        for _, row in df.dropna().iterrows():
            result.append({
                'Date': row['Date'].strftime('%Y-%m-%d'),
                'Volatility_30': float(row['Volatility_30']) if pd.notna(row['Volatility_30']) else None
            })
        return jsonify(result)
    except Exception as e:
        print(f"Error calculating volatility: {e}")
        return jsonify([])

# ============================================
# Main
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("Brent Oil API Server")
    print("=" * 50)
    print(f"Data directory: {DATA_DIR}")
    print(f"Price data: {PRICE_DATA_PATH}")
    print(f"Events data: {EVENTS_DATA_PATH}")
    print(f"Change point data: {CHANGE_POINT_PATH}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)