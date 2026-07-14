import pandas as pd
from backend.config import Config

def load_price_data():
    """Load Brent oil price data"""
    df = pd.read_csv(Config.PRICE_DATA_PATH, parse_dates=['Date'])
    return df.to_dict('records')

def load_events_data():
    """Load events data"""
    df = pd.read_csv(Config.EVENTS_DATA_PATH, parse_dates=['Date'])
    return df.to_dict('records')

def load_change_points():
    """Load change point detection results"""
    try:
        df = pd.read_csv(Config.CHANGE_POINT_PATH, parse_dates=[
            'change_point_date', 'ci_lower', 'ci_upper', 'event_date'
        ])
        return df.to_dict('records')
    except:
        return []

def get_price_by_date_range(start_date, end_date):
    """Filter price data by date range"""
    df = pd.read_csv(Config.PRICE_DATA_PATH, parse_dates=['Date'])
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    return df[mask].to_dict('records')

def get_event_impact_summary():
    """Calculate impact metrics for events"""
    df = pd.read_csv(Config.EVENTS_DATA_PATH, parse_dates=['Date'])
    price_df = pd.read_csv(Config.PRICE_DATA_PATH, parse_dates=['Date'])
    
    impacts = []
    for _, event in df.iterrows():
        event_date = event['Date']
        idx = price_df[price_df['Date'] >= event_date].index
        
        if len(idx) > 0:
            pos = idx[0]
            pre_price = price_df.iloc[max(0, pos-30)]['Price'] if pos > 30 else price_df.iloc[0]['Price']
            post_price = price_df.iloc[min(len(price_df)-1, pos+30)]['Price']
            impact_pct = ((post_price - pre_price) / pre_price) * 100
            
            impacts.append({
                'event': event['Event'],
                'date': event_date.strftime('%Y-%m-%d'),
                'category': event['Category'],
                'impact_pct': round(impact_pct, 2),
                'pre_price': round(pre_price, 2),
                'post_price': round(post_price, 2)
            })
    
    return impacts