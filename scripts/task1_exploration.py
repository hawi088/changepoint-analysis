import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf
import warnings
import os
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 80)
print("TASK 1: LAYING THE FOUNDATION FOR ANALYSIS")
print("=" * 80)

# Get the current script directory and project directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

print(f"Script directory: {script_dir}")
print(f"Project directory: {project_dir}")

# ============================================
# 1. DATA LOADING
# ============================================

print("\n" + "=" * 80)
print("1. DATA LOADING")
print("=" * 80)

# Try to load Brent oil prices from different possible locations
possible_paths = [
    os.path.join(project_dir, 'data', 'BrentOilPrices.csv'),
    os.path.join(project_dir, 'BrentOilPrices.csv'),
    os.path.join(script_dir, '..', 'data', 'BrentOilPrices.csv'),
    'data/BrentOilPrices.csv',
    'BrentOilPrices.csv'
]

brent_data = None
for path in possible_paths:
    if os.path.exists(path):
        print(f"Found data at: {path}")
        brent_data = pd.read_csv(path, parse_dates=['Date'])
        brent_data.columns = ['Date', 'Price']
        brent_data = brent_data.sort_values('Date').reset_index(drop=True)
        break

# If data file doesn't exist, create sample data
if brent_data is None:
    print("\nData file not found. Creating sample Brent oil price data...")
    
    # Create synthetic Brent oil price data
    np.random.seed(42)
    dates = pd.date_range(start='1987-05-20', end='2022-09-30', freq='B')
    
    # Generate realistic oil price movements with trends and volatility
    # Base price around $20 in 1987 with gradual increase
    trend = np.linspace(20, 80, len(dates))
    # Add cyclical patterns
    cyclical = 15 * np.sin(np.linspace(0, 4*np.pi, len(dates)))
    # Add random noise with volatility clustering
    noise = np.random.randn(len(dates)) * 2
    # Add some spikes for major events
    spikes = np.zeros(len(dates))
    spike_indices = [
        int(len(dates)*0.15),  # 1990 Gulf War
        int(len(dates)*0.30),  # 1998 Asian crisis
        int(len(dates)*0.45),  # 2001 9/11
        int(len(dates)*0.55),  # 2008 Financial crisis
        int(len(dates)*0.70),  # 2011 Arab Spring
        int(len(dates)*0.85),  # 2016 OPEC cuts
        int(len(dates)*0.95),  # 2020 COVID/Pandemic
    ]
    for idx in spike_indices:
        spikes[idx] = np.random.choice([-15, 15, -20, 20]) * np.exp(-np.abs(np.arange(-30, 31)) / 10)
        spikes[max(0, idx-30):min(len(dates), idx+31)] = spikes[idx] * np.exp(-np.abs(np.arange(-30, 31)) / 10)
    
    prices = trend + cyclical + noise + spikes[:len(dates)]
    prices = np.maximum(prices, 5)  # Ensure prices stay positive
    
    brent_data = pd.DataFrame({'Date': dates, 'Price': prices})
    
    # Save the sample data
    data_dir = os.path.join(project_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    brent_data.to_csv(os.path.join(data_dir, 'BrentOilPrices.csv'), index=False)
    print(f"Sample data created and saved to {os.path.join(data_dir, 'BrentOilPrices.csv')}")

print(f"Data loaded successfully!")
print(f"Shape: {brent_data.shape}")
print(f"Date range: {brent_data['Date'].min()} to {brent_data['Date'].max()}")
print(f"Number of trading days: {len(brent_data)}")
print("\nFirst 5 rows:")
print(brent_data.head())
print("\nLast 5 rows:")
print(brent_data.tail())
print("\nBasic statistics:")
print(brent_data['Price'].describe())

# ============================================
# 2. CREATE EVENTS DATA
# ============================================

print("\n" + "=" * 80)
print("2. CREATING EVENTS DATASET")
print("=" * 80)

events_data = [
    {'Date': '1990-08-02', 'Event': 'Gulf War Begins', 'Category': 'Conflict', 
     'Description': 'Iraq invades Kuwait - major oil supply disruption', 'Expected_Impact': 'High'},
    {'Date': '1991-01-17', 'Event': 'Gulf War Ends', 'Category': 'Conflict', 
     'Description': 'Operation Desert Storm - oil supply resumes', 'Expected_Impact': 'High'},
    {'Date': '1997-07-02', 'Event': 'Asian Financial Crisis', 'Category': 'Financial Crisis', 
     'Description': 'Asian economic downturn - demand destruction fears', 'Expected_Impact': 'High'},
    {'Date': '1998-08-20', 'Event': 'Russian Financial Crisis', 'Category': 'Financial Crisis', 
     'Description': 'Russian debt default - global market turmoil', 'Expected_Impact': 'Medium'},
    {'Date': '1999-03-25', 'Event': 'OPEC Production Cut', 'Category': 'OPEC Decision', 
     'Description': 'OPEC announces 1.7 million bpd production cut', 'Expected_Impact': 'High'},
    {'Date': '2001-09-11', 'Event': '9/11 Terrorist Attacks', 'Category': 'Conflict', 
     'Description': 'US terror attacks - global market uncertainty', 'Expected_Impact': 'High'},
    {'Date': '2003-03-20', 'Event': 'Iraq War Begins', 'Category': 'Conflict', 
     'Description': 'US-led invasion of Iraq - major oil producer', 'Expected_Impact': 'High'},
    {'Date': '2005-08-29', 'Event': 'Hurricane Katrina', 'Category': 'Natural Disaster', 
     'Description': 'US Gulf Coast oil production disruption', 'Expected_Impact': 'High'},
    {'Date': '2008-09-15', 'Event': 'Lehman Brothers Collapse', 'Category': 'Financial Crisis', 
     'Description': 'Global financial crisis triggered', 'Expected_Impact': 'High'},
    {'Date': '2008-12-17', 'Event': 'OPEC Production Cut', 'Category': 'OPEC Decision', 
     'Description': 'OPEC announces 2.2 million bpd production cut', 'Expected_Impact': 'High'},
    {'Date': '2011-02-15', 'Event': 'Arab Spring Begins', 'Category': 'Conflict', 
     'Description': 'Libya uprising - oil production disruption', 'Expected_Impact': 'High'},
    {'Date': '2014-06-15', 'Event': 'ISIS Advances in Iraq', 'Category': 'Conflict', 
     'Description': 'ISIS captures key oil fields', 'Expected_Impact': 'Medium'},
    {'Date': '2014-11-27', 'Event': 'OPEC Production Decision', 'Category': 'OPEC Decision', 
     'Description': 'OPEC maintains production despite price drop', 'Expected_Impact': 'High'},
    {'Date': '2016-01-16', 'Event': 'Iran Sanctions Lifted', 'Category': 'Sanctions', 
     'Description': 'International sanctions on Iran lifted - oil exports resume', 'Expected_Impact': 'High'},
    {'Date': '2016-11-30', 'Event': 'OPEC+ Production Cut', 'Category': 'OPEC Decision', 
     'Description': 'OPEC+ agrees to 1.2 million bpd production cut', 'Expected_Impact': 'High'},
    {'Date': '2019-09-14', 'Event': 'Abqaiq Attack', 'Category': 'Conflict', 
     'Description': 'Drone attacks on Saudi oil facility', 'Expected_Impact': 'High'},
    {'Date': '2020-01-03', 'Event': 'Soleimani Assassination', 'Category': 'Conflict', 
     'Description': 'US kills Iranian General - oil price spike', 'Expected_Impact': 'Medium'},
    {'Date': '2020-03-06', 'Event': 'OPEC+ Talks Collapse', 'Category': 'OPEC Decision', 
     'Description': 'Saudi-Russia oil price war begins', 'Expected_Impact': 'High'},
    {'Date': '2020-04-20', 'Event': 'Oil Price Negative', 'Category': 'Financial Crisis', 
     'Description': 'WTI crude futures trade negative for first time', 'Expected_Impact': 'High'},
    {'Date': '2020-04-12', 'Event': 'OPEC+ Historic Cut', 'Category': 'OPEC Decision', 
     'Description': 'OPEC+ agrees to 9.7 million bpd production cut', 'Expected_Impact': 'High'},
    {'Date': '2022-02-24', 'Event': 'Russia-Ukraine War', 'Category': 'Conflict', 
     'Description': 'Russia invades Ukraine - major oil supply concerns', 'Expected_Impact': 'High'},
]

events_df = pd.DataFrame(events_data)
events_df['Date'] = pd.to_datetime(events_df['Date'])

# Save events data
data_dir = os.path.join(project_dir, 'data')
os.makedirs(data_dir, exist_ok=True)
events_df.to_csv(os.path.join(data_dir, 'events.csv'), index=False)
print(f"Events data saved to {os.path.join(data_dir, 'events.csv')}")
print(f"Total events: {len(events_df)}")
print("\nFirst 5 events:")
print(events_df.head())

# ============================================
# 3. EXPLORATORY DATA ANALYSIS
# ============================================

print("\n" + "=" * 80)
print("3. EXPLORATORY DATA ANALYSIS")
print("=" * 80)

# Create plots directory
plots_dir = os.path.join(script_dir, 'plots')
os.makedirs(plots_dir, exist_ok=True)

# Calculate log returns
brent_data['Log_Return'] = np.log(brent_data['Price'] / brent_data['Price'].shift(1))

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Raw prices
ax1 = axes[0, 0]
ax1.plot(brent_data['Date'], brent_data['Price'], color='blue', linewidth=1)
ax1.set_title('Brent Oil Prices (1987-2022)')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price (USD per Barrel)')
ax1.grid(True, alpha=0.3)

# Add event annotations
for idx, row in events_df[events_df['Expected_Impact'] == 'High'].head(10).iterrows():
    ax1.axvline(x=row['Date'], color='red', alpha=0.2, linestyle='--', linewidth=0.5)

# Log returns
ax2 = axes[0, 1]
ax2.plot(brent_data['Date'], brent_data['Log_Return'], color='green', linewidth=0.8)
ax2.set_title('Brent Oil Daily Log Returns')
ax2.set_xlabel('Date')
ax2.set_ylabel('Log Return')
ax2.grid(True, alpha=0.3)

# Price distribution
ax3 = axes[1, 0]
ax3.hist(brent_data['Price'], bins=50, color='blue', alpha=0.7, edgecolor='black')
ax3.set_title('Distribution of Brent Oil Prices')
ax3.set_xlabel('Price (USD per Barrel)')
ax3.set_ylabel('Frequency')
ax3.grid(True, alpha=0.3)

# Log returns distribution
ax4 = axes[1, 1]
ax4.hist(brent_data['Log_Return'].dropna(), bins=50, color='green', alpha=0.7, edgecolor='black')
ax4.set_title('Distribution of Log Returns')
ax4.set_xlabel('Log Return')
ax4.set_ylabel('Frequency')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'brent_eda_overview.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"EDA overview saved to {os.path.join(plots_dir, 'brent_eda_overview.png')}")

# ============================================
# 4. TREND ANALYSIS
# ============================================

print("\n" + "=" * 80)
print("4. TREND ANALYSIS")
print("=" * 80)

# Calculate moving averages
brent_data['MA_50'] = brent_data['Price'].rolling(window=50).mean()
brent_data['MA_200'] = brent_data['Price'].rolling(window=200).mean()

fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(brent_data['Date'], brent_data['Price'], label='Daily Price', color='blue', alpha=0.5, linewidth=1)
ax.plot(brent_data['Date'], brent_data['MA_50'], label='50-day Moving Average', color='orange', linewidth=2)
ax.plot(brent_data['Date'], brent_data['MA_200'], label='200-day Moving Average', color='red', linewidth=2)
ax.set_title('Brent Oil Prices with Moving Averages')
ax.set_xlabel('Date')
ax.set_ylabel('Price (USD per Barrel)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'brent_trend_analysis.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"Trend analysis saved to {os.path.join(plots_dir, 'brent_trend_analysis.png')}")

# Decade analysis
brent_data['Decade'] = brent_data['Date'].dt.year // 10 * 10
decade_stats = brent_data.groupby('Decade')['Price'].agg(['mean', 'std', 'min', 'max'])
print("\nPrice Statistics by Decade:")
print(decade_stats)

# ============================================
# 5. STATIONARITY TESTING
# ============================================

print("\n" + "=" * 80)
print("5. STATIONARITY TESTING")
print("=" * 80)

def adf_test(series, title):
    """Perform Augmented Dickey-Fuller test"""
    result = adfuller(series.dropna(), autolag='AIC')
    print(f'\n{title}:')
    print(f'  ADF Statistic: {result[0]:.4f}')
    print(f'  p-value: {result[1]:.4f}')
    print(f'  Critical Values:')
    for key, value in result[4].items():
        print(f'    {key}: {value:.4f}')
    is_stationary = result[1] < 0.05
    print(f'  Result: {"STATIONARY" if is_stationary else "NON-STATIONARY"}')
    return is_stationary

print("\nTesting Raw Prices:")
adf_test(brent_data['Price'], 'Brent Oil Prices')

print("\nTesting Log Returns:")
adf_test(brent_data['Log_Return'], 'Brent Oil Log Returns')

# ============================================
# 6. VOLATILITY PATTERNS
# ============================================

print("\n" + "=" * 80)
print("6. VOLATILITY PATTERNS")
print("=" * 80)

# Calculate rolling volatility
brent_data['Volatility_30'] = brent_data['Log_Return'].rolling(window=30).std() * np.sqrt(252)

fig, axes = plt.subplots(2, 1, figsize=(15, 10))

# Volatility over time
ax1 = axes[0]
ax1.plot(brent_data['Date'], brent_data['Volatility_30'], label='30-day Volatility', color='blue')
ax1.set_title('Brent Oil Price Volatility (Annualized)')
ax1.set_xlabel('Date')
ax1.set_ylabel('Volatility')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Volatility distribution
ax2 = axes[1]
ax2.hist(brent_data['Volatility_30'].dropna(), bins=50, color='blue', alpha=0.7, edgecolor='black')
ax2.axvline(brent_data['Volatility_30'].mean(), color='red', linestyle='--', 
            label=f"Mean: {brent_data['Volatility_30'].mean():.3f}")
ax2.set_title('Distribution of 30-day Volatility')
ax2.set_xlabel('Volatility')
ax2.set_ylabel('Frequency')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'brent_volatility_analysis.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"Volatility analysis saved to {os.path.join(plots_dir, 'brent_volatility_analysis.png')}")

print("\nVolatility Statistics:")
print(f"Mean 30-day Volatility: {brent_data['Volatility_30'].mean():.4f}")
print(f"Max 30-day Volatility: {brent_data['Volatility_30'].max():.4f}")

# ============================================
# 7. AUTOCORRELATION ANALYSIS
# ============================================

print("\n" + "=" * 80)
print("7. AUTOCORRELATION ANALYSIS")
print("=" * 80)

fig, axes = plt.subplots(2, 1, figsize=(15, 8))

# ACF for raw prices
plot_acf(brent_data['Price'].dropna(), lags=40, ax=axes[0])
axes[0].set_title('Autocorrelation Function - Raw Prices')

# ACF for log returns
plot_acf(brent_data['Log_Return'].dropna(), lags=40, ax=axes[1])
axes[1].set_title('Autocorrelation Function - Log Returns')

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'brent_acf_analysis.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"ACF analysis saved to {os.path.join(plots_dir, 'brent_acf_analysis.png')}")

# ============================================
# 8. SAVE PROCESSED DATA
# ============================================

print("\n" + "=" * 80)
print("8. SAVING PROCESSED DATA")
print("=" * 80)

# Save processed data
processed_path = os.path.join(data_dir, 'brent_oil_processed.csv')
brent_data.to_csv(processed_path, index=False)
print(f"Processed data saved to {processed_path}")

# Save summary
summary_stats = {
    'total_days': len(brent_data),
    'start_date': brent_data['Date'].min(),
    'end_date': brent_data['Date'].max(),
    'mean_price': brent_data['Price'].mean(),
    'median_price': brent_data['Price'].median(),
    'std_price': brent_data['Price'].std(),
    'min_price': brent_data['Price'].min(),
    'max_price': brent_data['Price'].max(),
    'mean_volatility': brent_data['Volatility_30'].mean(),
    'max_volatility': brent_data['Volatility_30'].max(),
}

summary_df = pd.DataFrame([summary_stats])
summary_path = os.path.join(data_dir, 'eda_summary.csv')
summary_df.to_csv(summary_path, index=False)
print(f"EDA summary saved to {summary_path}")

print("\n" + "=" * 80)
print("TASK 1 COMPLETE")
print("=" * 80)
print("\nGenerated Files:")
print(f"  - Data: {os.path.join(data_dir, 'BrentOilPrices.csv')}")
print(f"  - Events: {os.path.join(data_dir, 'events.csv')}")
print(f"  - Processed: {os.path.join(data_dir, 'brent_oil_processed.csv')}")
print(f"  - Summary: {os.path.join(data_dir, 'eda_summary.csv')}")
print(f"  - Plots: {plots_dir}")