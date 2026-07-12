import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.stattools import adfuller
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
import os
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 80)
print("TASK 2: CHANGE POINT MODELING AND INSIGHT GENERATION")
print("=" * 80)

# Get the current script directory and project directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

# ============================================
# 1. DATA LOADING
# ============================================

print("\n" + "=" * 80)
print("1. DATA LOADING")
print("=" * 80)

# Load processed data
data_path = os.path.join(project_dir, 'data', 'brent_oil_processed.csv')
brent_data = pd.read_csv(data_path, parse_dates=['Date'])
print(f"Data loaded: {data_path}")
print(f"Shape: {brent_data.shape}")
print(f"Date range: {brent_data['Date'].min()} to {brent_data['Date'].max()}")

# Load events data
events_path = os.path.join(project_dir, 'data', 'events.csv')
events_df = pd.read_csv(events_path, parse_dates=['Date'])
print(f"Events loaded: {len(events_df)} events")

# ============================================
# 2. DATA PREPARATION
# ============================================

print("\n" + "=" * 80)
print("2. DATA PREPARATION")
print("=" * 80)

# Use log returns for change point analysis
log_returns = brent_data['Log_Return'].dropna().values
dates = brent_data['Date'].iloc[1:].values
n_obs = len(log_returns)

print(f"Number of observations: {n_obs}")
print(f"Log returns range: {log_returns.min():.4f} to {log_returns.max():.4f}")

# ============================================
# 3. CHANGE POINT DETECTION USING CUSUM METHOD
# ============================================

print("\n" + "=" * 80)
print("3. CHANGE POINT DETECTION USING CUSUM METHOD")
print("=" * 80)

def detect_change_point_cusum(data, alpha=0.05):
    """
    Detect change point using CUSUM method
    This is a simpler approach that doesn't require compilation
    """
    n = len(data)
    mean_data = np.mean(data)
    std_data = np.std(data)
    
    # Calculate CUSUM statistics
    S = np.zeros(n)
    for i in range(1, n):
        S[i] = S[i-1] + (data[i] - mean_data) / std_data
    
    # Find the maximum absolute deviation
    S_max = np.max(np.abs(S))
    change_point_idx = np.argmax(np.abs(S))
    
    # Calculate confidence threshold
    threshold = 1.358 * np.sqrt(n)  # Approximate threshold for 95% confidence
    
    # Check if change point is significant
    is_significant = S_max > threshold
    
    return change_point_idx, S, S_max, threshold, is_significant

def detect_change_point_rolling(data, window=30):
    """
    Detect change point using rolling statistics
    """
    n = len(data)
    rolling_means = np.zeros(n - window)
    rolling_stds = np.zeros(n - window)
    
    for i in range(n - window):
        rolling_means[i] = np.mean(data[i:i+window])
        rolling_stds[i] = np.std(data[i:i+window])
    
    # Find where rolling mean changes most dramatically
    mean_diff = np.diff(rolling_means)
    max_change_idx = np.argmax(np.abs(mean_diff)) + window // 2
    
    return max_change_idx, rolling_means, rolling_stds

print("Detecting change points using CUSUM method...")
cp_idx_cusum, S, S_max, threshold, is_significant = detect_change_point_cusum(log_returns)

# Convert numpy datetime64 to pandas Timestamp for formatting
cp_date = pd.Timestamp(dates[cp_idx_cusum])

print(f"\nCUSUM Change Point Detection Results:")
print(f"  Change Point Index: {cp_idx_cusum}")
print(f"  Change Point Date: {cp_date.strftime('%Y-%m-%d')}")
print(f"  CUSUM Max Value: {S_max:.4f}")
print(f"  Threshold (95% CI): {threshold:.4f}")
print(f"  Significant: {is_significant}")

# Also use rolling method for comparison
print("\nDetecting change points using rolling method...")
cp_idx_rolling, rolling_means, rolling_stds = detect_change_point_rolling(log_returns, window=60)
cp_date_rolling = pd.Timestamp(dates[cp_idx_rolling])
print(f"  Rolling Change Point Index: {cp_idx_rolling}")
print(f"  Rolling Change Point Date: {cp_date_rolling.strftime('%Y-%m-%d')}")

# Use the CUSUM result as primary
tau_median = cp_idx_cusum
cp_date = pd.Timestamp(dates[tau_median])

# ============================================
# 4. QUANTIFY IMPACT
# ============================================

print("\n" + "=" * 80)
print("4. QUANTIFYING IMPACT")
print("=" * 80)

# Calculate statistics before and after change
before_data = log_returns[:tau_median]
after_data = log_returns[tau_median:]

mu_before = np.mean(before_data)
mu_after = np.mean(after_data)
std_before = np.std(before_data)
std_after = np.std(after_data)

# Calculate change
change_in_mean = mu_after - mu_before
change_pct = (change_in_mean / mu_before) * 100 if mu_before != 0 else 0

# Calculate confidence intervals using bootstrap
n_bootstrap = 1000
bootstrap_diffs = []
for _ in range(n_bootstrap):
    boot_before = np.random.choice(before_data, size=len(before_data), replace=True)
    boot_after = np.random.choice(after_data, size=len(after_data), replace=True)
    bootstrap_diffs.append(np.mean(boot_after) - np.mean(boot_before))

ci_lower = np.percentile(bootstrap_diffs, 2.5)
ci_upper = np.percentile(bootstrap_diffs, 97.5)

print(f"\nChange Point Analysis Results:")
print("-" * 50)
print(f"Change Point Date: {cp_date.strftime('%Y-%m-%d')}")
print(f"Change Point Index: {tau_median}")
print(f"\nBefore Change (n={len(before_data)}):")
print(f"  Mean Log Return: {mu_before:.6f}")
print(f"  Std Dev: {std_before:.6f}")
print(f"\nAfter Change (n={len(after_data)}):")
print(f"  Mean Log Return: {mu_after:.6f}")
print(f"  Std Dev: {std_after:.6f}")
print(f"\nChange in Mean: {change_in_mean:.6f} ({change_pct:.2f}%)")
print(f"95% CI for Change: [{ci_lower:.6f}, {ci_upper:.6f}]")

# Price impact calculation
price_before = brent_data.iloc[tau_median]['Price']
price_after = brent_data.iloc[min(tau_median+30, len(brent_data)-1)]['Price']
price_change = price_after - price_before
price_change_pct = (price_change / price_before) * 100

print(f"\nPrice Impact (30-day window):")
print(f"Price Before: ${price_before:.2f}")
print(f"Price After (30 days): ${price_after:.2f}")
print(f"Price Change: ${price_change:.2f} ({price_change_pct:.2f}%)")

# ============================================
# 5. VISUALIZE RESULTS
# ============================================

print("\n" + "=" * 80)
print("5. VISUALIZING RESULTS")
print("=" * 80)

# Create plots directory
plots_dir = os.path.join(script_dir, 'plots')
os.makedirs(plots_dir, exist_ok=True)

# Convert dates to pandas datetime for plotting
plot_dates = pd.to_datetime(dates)

# 5a. CUSUM Plot
fig, axes = plt.subplots(3, 1, figsize=(15, 12))

# Original data with change point
ax1 = axes[0]
ax1.plot(plot_dates, log_returns, color='blue', linewidth=0.8, alpha=0.7, label='Log Returns')
ax1.axvline(x=cp_date, color='red', linewidth=2, linestyle='--', 
            label=f'Change Point: {cp_date.strftime("%Y-%m-%d")}')
ax1.set_title('Brent Oil Log Returns with Detected Change Point')
ax1.set_xlabel('Date')
ax1.set_ylabel('Log Return')
ax1.legend()
ax1.grid(True, alpha=0.3)

# CUSUM statistics
ax2 = axes[1]
ax2.plot(plot_dates, S, color='green', linewidth=1.5, label='CUSUM Statistics')
ax2.axhline(y=threshold, color='red', linestyle='--', label=f'Threshold: {threshold:.2f}')
ax2.axhline(y=-threshold, color='red', linestyle='--')
ax2.axvline(x=cp_date, color='purple', linestyle='--', 
            label=f'Change Point: {cp_date.strftime("%Y-%m-%d")}')
ax2.set_title('CUSUM Statistics')
ax2.set_xlabel('Date')
ax2.set_ylabel('CUSUM Value')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Rolling means
ax3 = axes[2]
window = 60
rolling_means = pd.Series(log_returns).rolling(window=window).mean().values[window-1:]
rolling_dates = plot_dates[window-1:]
ax3.plot(rolling_dates, rolling_means, color='orange', linewidth=1.5, label=f'{window}-day Rolling Mean')
ax3.axhline(y=np.mean(log_returns), color='blue', linestyle='--', label='Overall Mean')
ax3.axvline(x=cp_date, color='red', linestyle='--', label='Change Point')
ax3.set_title('Rolling Mean of Log Returns')
ax3.set_xlabel('Date')
ax3.set_ylabel('Rolling Mean')
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'change_point_analysis.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"Change point analysis saved to {os.path.join(plots_dir, 'change_point_analysis.png')}")

# 5b. Price series with change point
fig, ax = plt.subplots(figsize=(15, 8))

ax.plot(brent_data['Date'], brent_data['Price'], color='blue', linewidth=1, alpha=0.7, label='Brent Oil Price')

# Mark change point
ax.axvline(x=cp_date, color='red', linewidth=2, linestyle='--', 
           label=f'Change Point: {cp_date.strftime("%Y-%m-%d")}')

# Add confidence interval
ax.axvspan(plot_dates[max(0, tau_median-100)], plot_dates[min(n_obs-1, tau_median+100)], 
           alpha=0.2, color='red', label='Approximate Uncertainty Region')

# Add event annotations
for idx, row in events_df.iterrows():
    if row['Expected_Impact'] == 'High':
        ax.axvline(x=row['Date'], color='orange', alpha=0.2, linestyle=':', linewidth=0.5)
        ax.text(row['Date'], brent_data['Price'].max() * 0.95, 
                row['Event'][:15], rotation=45, fontsize=6, alpha=0.7)

ax.set_title(f'Brent Oil Prices with Detected Change Point ({cp_date.strftime("%Y-%m-%d")})')
ax.set_xlabel('Date')
ax.set_ylabel('Price (USD per Barrel)')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'change_point_on_prices.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"Change point on price series saved to {os.path.join(plots_dir, 'change_point_on_prices.png')}")

# 5c. Distribution comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Before distribution
ax1.hist(before_data, bins=50, color='blue', alpha=0.7, edgecolor='black', density=True)
ax1.axvline(mu_before, color='red', linestyle='--', label=f'Mean: {mu_before:.4f}')
ax1.set_title(f'Distribution of Log Returns (Before {cp_date.strftime("%Y-%m-%d")})')
ax1.set_xlabel('Log Return')
ax1.set_ylabel('Density')
ax1.legend()
ax1.grid(True, alpha=0.3)

# After distribution
ax2.hist(after_data, bins=50, color='green', alpha=0.7, edgecolor='black', density=True)
ax2.axvline(mu_after, color='red', linestyle='--', label=f'Mean: {mu_after:.4f}')
ax2.set_title(f'Distribution of Log Returns (After {cp_date.strftime("%Y-%m-%d")})')
ax2.set_xlabel('Log Return')
ax2.set_ylabel('Density')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'distribution_comparison.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"Distribution comparison saved to {os.path.join(plots_dir, 'distribution_comparison.png')}")

# ============================================
# 6. ASSOCIATE CHANGE WITH EVENTS
# ============================================

print("\n" + "=" * 80)
print("6. ASSOCIATING CHANGE WITH EVENTS")
print("=" * 80)

# Find events close to the change point
events_near_cp = events_df[
    (events_df['Date'] >= cp_date - pd.Timedelta(days=90)) &
    (events_df['Date'] <= cp_date + pd.Timedelta(days=90))
]

print(f"\nEvents near the change point ({cp_date.strftime('%Y-%m-%d')} +/- 90 days):")
print("-" * 70)
if len(events_near_cp) > 0:
    for idx, row in events_near_cp.iterrows():
        days_diff = (row['Date'] - cp_date).days
        print(f"  {row['Date'].strftime('%Y-%m-%d')} | {row['Event']:<30} | Days from CP: {days_diff:+4d}")
else:
    print("  No major events found near the change point")

# Find closest event
if len(events_near_cp) > 0:
    closest_event = events_near_cp.iloc[np.argmin(np.abs(events_near_cp['Date'] - cp_date))]
    print(f"\nMost likely associated event:")
    print(f"  Event: {closest_event['Event']}")
    print(f"  Date: {closest_event['Date'].strftime('%Y-%m-%d')}")
    print(f"  Days from CP: {(closest_event['Date'] - cp_date).days}")
    print(f"  Category: {closest_event['Category']}")
    print(f"  Description: {closest_event['Description']}")

# ============================================
# 7. SAVE RESULTS
# ============================================

print("\n" + "=" * 80)
print("7. SAVING RESULTS")
print("=" * 80)

# Create results summary
results = {
    'change_point_date': cp_date,
    'change_point_idx': tau_median,
    'mean_before': mu_before,
    'mean_after': mu_after,
    'mean_change': change_in_mean,
    'mean_change_pct': change_pct,
    'ci_lower': ci_lower,
    'ci_upper': ci_upper,
    'price_before': price_before,
    'price_after': price_after,
    'price_change': price_change,
    'price_change_pct': price_change_pct,
    'most_likely_event': closest_event['Event'] if len(events_near_cp) > 0 else 'Unknown',
    'event_date': closest_event['Date'] if len(events_near_cp) > 0 else None,
    'event_category': closest_event['Category'] if len(events_near_cp) > 0 else 'Unknown',
    'is_significant': is_significant
}

results_df = pd.DataFrame([results])
results_path = os.path.join(project_dir, 'data', 'change_point_results.csv')
results_df.to_csv(results_path, index=False)
print(f"Results saved to {results_path}")

print("\n" + "=" * 80)
print("TASK 2 COMPLETE")
print("=" * 80)

print("\nSummary of Change Point Analysis:")
print("-" * 50)
print(f"Change Point Date: {cp_date.strftime('%Y-%m-%d')}")
print(f"Mean Log Return Change: {change_in_mean:.6f} ({change_pct:.2f}%)")
print(f"95% CI: [{ci_lower:.6f}, {ci_upper:.6f}]")
print(f"Price Impact (30-day): ${price_change:.2f} ({price_change_pct:.2f}%)")
print(f"Associated Event: {closest_event['Event'] if len(events_near_cp) > 0 else 'Unknown'}")
print(f"Significant Change: {is_significant}")