from flask import Blueprint, request, jsonify
from backend.api.data_loader import (
    load_price_data, load_events_data, load_change_points,
    get_price_by_date_range, get_event_impact_summary
)

api = Blueprint('api', __name__)

@api.route('/api/prices', methods=['GET'])
def get_prices():
    """Get historical price data"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        data = get_price_by_date_range(start_date, end_date)
    else:
        data = load_price_data()
    
    return jsonify(data)

@api.route('/api/events', methods=['GET'])
def get_events():
    """Get events data"""
    data = load_events_data()
    return jsonify(data)

@api.route('/api/change-points', methods=['GET'])
def get_change_points():
    """Get change point detection results"""
    data = load_change_points()
    return jsonify(data)

@api.route('/api/event-impacts', methods=['GET'])
def get_event_impacts():
    """Get event impact summary"""
    data = get_event_impact_summary()
    return jsonify(data)

@api.route('/api/summary', methods=['GET'])
def get_summary():
    """Get summary statistics"""
    price_data = load_price_data()
    events_data = load_events_data()
    change_points = load_change_points()
    
    df = pd.DataFrame(price_data)
    
    summary = {
        'total_days': len(df),
        'price_min': round(df['Price'].min(), 2),
        'price_max': round(df['Price'].max(), 2),
        'price_mean': round(df['Price'].mean(), 2),
        'total_events': len(events_data),
        'change_points_detected': len(change_points)
    }
    
    return jsonify(summary)

@api.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})