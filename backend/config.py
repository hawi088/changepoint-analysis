import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
    
    PRICE_DATA_PATH = os.path.join(DATA_DIR, 'brent_oil_processed.csv')
    EVENTS_DATA_PATH = os.path.join(DATA_DIR, 'events.csv')
    CHANGE_POINT_PATH = os.path.join(DATA_DIR, 'change_point_results.csv')
    
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000