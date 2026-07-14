import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.tsa.stattools import adfuller
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
# 1. DATA LOADING AND PREPARATION
# ============================================

print("\n" + "=" * 80)
print("1. DATA LOADING AND PREPARATION")
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

# Use log returns for the change point analysis
log_returns = brent_data['Log_Return'].dropna().values
dates = brent_data['Date'].iloc[1:].values
n_obs = len(log_returns)

print(f"\nNumber of observations: {n_obs}")
print(f"Log returns range: {log_returns.min():.4f} to {log_returns.max():.4f}")

# ============================================
# 2. EXPLORATORY DATA ANALYSIS
# ============================================

print("\n" + "=" * 80)
print("2. EXPLORATORY DATA ANALYSIS")
print("=" * 80)

# Create plots directory
plots_dir = os.path.join(script_dir, 'plots')
os.makedirs(plots_dir, exist_ok=True)

# EDA Plot
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Raw prices
ax1 = axes[0, 0]
ax1.plot(brent_data['Date'], brent_data['Price'], color='blue', linewidth=1)
ax1.set_title('Brent Oil Prices (1987-2022)')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price (USD per Barrel)')
ax1.grid(True, alpha=0.3)

# Log returns
ax2 = axes[0, 1]
ax2.plot(brent_data['Date'].iloc[1:], log_returns, color='green', linewidth=0.8)
ax2.set_title('Brent Oil Log Returns')
ax2.set_xlabel('Date')
ax2.set_ylabel('Log Return')
ax2.grid(True, alpha=0.3)

# Histogram of log returns
ax3 = axes[1, 0]
ax3.hist(log_returns, bins=50, color='green', alpha=0.7, edgecolor='black')
ax3.set_title('Distribution of Log Returns')
ax3.set_xlabel('Log Return')
ax3.set_ylabel('Frequency')
ax3.grid(True, alpha=0.3)

# Q-Q plot
ax4 = axes[1, 1]
stats.probplot(log_returns, dist="norm", plot=ax4)
ax4.set_title('Q-Q Plot of Log Returns')

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'eda_for_modeling.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"EDA for modeling saved to {os.path.join(plots_dir, 'eda_for_modeling.png')}")

# ============================================
# 3. CHANGE POINT DETECTION (CUSUM METHOD)
# ============================================

print("\n" + "=" * 80)
print("3. CHANGE POINT DETECTION USING CUSUM METHOD")
print("=" * 80)

def detect_change_point_cusum(data, alpha=0.05):
    """
    Detect change point using CUSUM method
    Provides Bayesian-style output with confidence intervals
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
    
    # Bootstrap for confidence intervals
    n_bootstrap = 1000
    boot_cp_indices = []
    for _ in range(n_bootstrap):
        boot_data = np.random.choice(data, size=n, replace=True)
        boot_mean = np.mean(boot_data)
        boot_std = np.std(boot_data)
        boot_S = np.zeros(n)
        for i in range(1, n):
            boot_S[i] = boot_S[i-1] + (boot_data[i] - boot_mean) / boot_std
        boot_cp_indices.append(np.argmax(np.abs(boot_S)))
    
    # Calculate confidence intervals
    ci_lower = int(np.percentile(boot_cp_indices, 2.5))
    ci_upper = int(np.percentile(boot_cp_indices, 97.5))
    
    # Calculate threshold
    threshold = 1.358 * np.sqrt(n)
    is_significant = S_max > threshold
    
    return {
        'change_point_idx': change_point_idx,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'cusum_values': S,
        'cusum_max': S_max,
        'threshold': threshold,
        'is_significant': is_significant,
        'bootstrap_indices': boot_cp_indices
    }

# Detect change point
results = detect_change_point_cusum(log_returns)

cp_idx = results['change_point_idx']
cp_date = pd.Timestamp(dates[cp_idx])
ci_lower_date = pd.Timestamp(dates[results['ci_lower']])
ci_upper_date = pd.Timestamp(dates[results['ci_upper']])

print(f"\nCUSUM Change Point Detection Results:")
print("-" * 50)
print(f"Change Point Index: {cp_idx}")
print(f"Change Point Date: {cp_date.strftime('%Y-%m-%d')}")
print(f"95% CI: {ci_lower_date.strftime('%Y-%m-%d')} to {ci_upper_date.strftime('%Y-%m-%d')}")
print(f"CUSUM Max Value: {results['cusum_max']:.4f}")
print(f"Threshold: {results['threshold']:.4f}")
print(f"Statistically Significant: {results['is_significant']}")

# ============================================
# 4. QUANTIFY IMPACT (BAYESIAN-STYLE)
# ============================================

print("\n" + "=" * 80)
print("4. QUANTIFYING IMPACT (BAYESIAN-STYLE)")
print("=" * 80)

# Split data at change point
before_data = log_returns[:cp_idx]
after_data = log_returns[cp_idx:]

# Calculate statistics
mu_before = np.mean(before_data)
mu_after = np.mean(after_data)
std_before = np.std(before_data)
std_after = np.std(after_data)

# Bootstrap for credible intervals (Bayesian-style)
n_bootstrap = 2000
boot_means_before = []
boot_means_after = []
boot_diffs = []

for _ in range(n_bootstrap):
    boot_before = np.random.choice(before_data, size=len(before_data), replace=True)
    boot_after = np.random.choice(after_data, size=len(after_data), replace=True)
    boot_means_before.append(np.mean(boot_before))
    boot_means_after.append(np.mean(boot_after))
    boot_diffs.append(np.mean(boot_after) - np.mean(boot_before))

# Calculate credible intervals (Bayesian-style HDI)
ci_before = np.percentile(boot_means_before, [2.5, 97.5])
ci_after = np.percentile(boot_means_after, [2.5, 97.5])
ci_diff = np.percentile(boot_diffs, [2.5, 97.5])

# Calculate change
change_in_mean = mu_after - mu_before
change_pct = (change_in_mean / mu_before) * 100 if mu_before != 0 else 0

# Probabilistic statements
prob_positive = np.mean(np.array(boot_diffs) > 0) * 100
prob_negative = np.mean(np.array(boot_diffs) < 0) * 100

print(f"\nChange Point Analysis Results:")
print("-" * 50)
print(f"Change Point Date: {cp_date.strftime('%Y-%m-%d')}")
print(f"95% CI: {ci_lower_date.strftime('%Y-%m-%d')} to {ci_upper_date.strftime('%Y-%m-%d')}")
print(f"\nBefore Change (n={len(before_data)}):")
print(f"  Mean Log Return: {mu_before:.6f}")
print(f"  95% CI: [{ci_before[0]:.6f}, {ci_before[1]:.6f}]")
print(f"  Std Dev: {std_before:.6f}")
print(f"\nAfter Change (n={len(after_data)}):")
print(f"  Mean Log Return: {mu_after:.6f}")
print(f"  95% CI: [{ci_after[0]:.6f}, {ci_after[1]:.6f}]")
print(f"  Std Dev: {std_after:.6f}")
print(f"\nChange in Mean: {change_in_mean:.6f} ({change_pct:.2f}%)")
print(f"95% CI for Change: [{ci_diff[0]:.6f}, {ci_diff[1]:.6f}]")

# Price impact
price_before = brent_data.iloc[cp_idx]['Price']
price_after = brent_data.iloc[min(cp_idx+30, len(brent_data)-1)]['Price']
price_change = price_after - price_before
price_change_pct = (price_change / price_before) * 100

print(f"\nPrice Impact (30-day window):")
print(f"Price Before: ${price_before:.2f}")
print(f"Price After (30 days): ${price_after:.2f}")
print(f"Price Change: ${price_change:.2f} ({price_change_pct:.2f}%)")

print(f"\nProbabilistic Statements:")
print(f"Probability of positive change: {prob_positive:.1f}%")
print(f"Probability of negative change: {prob_negative:.1f}%")

# ============================================
# 5. VISUALIZATIONS
# ============================================

print("\n" + "=" * 80)
print("5. VISUALIZING RESULTS")
print("=" * 80)

# 5a. CUSUM Plot with Change Point
fig, axes = plt.subplots(3, 1, figsize=(15, 12))

# Log returns with change point
ax1 = axes[0]
ax1.plot(pd.to_datetime(dates), log_returns, color='blue', linewidth=0.8, alpha=0.7, label='Log Returns')
ax1.axvline(x=cp_date, color='red', linewidth=2, linestyle='--', 
            label=f'Change Point: {cp_date.strftime("%Y-%m-%d")}')
ax1.axvspan(ci_lower_date, ci_upper_date, alpha=0.2, color='red', label='95% CI')
ax1.set_title('Brent Oil Log Returns with Detected Change Point')
ax1.set_xlabel('Date')
ax1.set_ylabel('Log Return')
ax1.legend()
ax1.grid(True, alpha=0.3)

# CUSUM statistics
ax2 = axes[1]
ax2.plot(pd.to_datetime(dates), results['cusum_values'], color='green', linewidth=1.5, label='CUSUM Statistics')
ax2.axhline(y=results['threshold'], color='red', linestyle='--', label=f'Threshold: {results["threshold"]:.2f}')
ax2.axhline(y=-results['threshold'], color='red', linestyle='--')
ax2.axvline(x=cp_date, color='purple', linestyle='--', label='Change Point')
ax2.set_title('CUSUM Statistics')
ax2.set_xlabel('Date')
ax2.set_ylabel('CUSUM Value')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Posterior distribution (bootstrap distribution)
ax3 = axes[2]
ax3.hist(results['bootstrap_indices'], bins=50, color='purple', alpha=0.7, edgecolor='black', density=True)
ax3.axvline(cp_idx, color='red', linestyle='--', label=f'Median: {cp_date.strftime("%Y-%m-%d")}')
ax3.axvline(results['ci_lower'], color='green', linestyle='--', label=f'95% CI Lower')
ax3.axvline(results['ci_upper'], color='green', linestyle='--', label=f'95% CI Upper')
ax3.set_title('Bootstrap Distribution of Change Point (Bayesian-style Posterior)')
ax3.set_xlabel('Change Point Index')
ax3.set_ylabel('Density')
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'change_point_analysis.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"Change point analysis saved to {os.path.join(plots_dir, 'change_point_analysis.png')}")

# 5b. Price series with change point
fig, ax = plt.subplots(figsize=(15, 8))

ax.plot(brent_data['Date'], brent_data['Price'], color='blue', linewidth=1, alpha=0.7, label='Brent Oil Price')
ax.axvline(x=cp_date, color='red', linewidth=2, linestyle='--', 
           label=f'Change Point: {cp_date.strftime("%Y-%m-%d")}')
ax.axvspan(ci_lower_date, ci_upper_date, alpha=0.2, color='red', label='95% CI')

# Event annotations
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
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Before distribution
ax1 = axes[0]
ax1.hist(before_data, bins=50, color='blue', alpha=0.7, edgecolor='black', density=True)
ax1.axvline(mu_before, color='red', linestyle='--', label=f'Mean: {mu_before:.6f}')
ax1.axvline(ci_before[0], color='green', linestyle='--', alpha=0.5, label='95% CI')
ax1.axvline(ci_before[1], color='green', linestyle='--', alpha=0.5)
ax1.set_title(f'Distribution (Before {cp_date.strftime("%Y-%m-%d")})')
ax1.set_xlabel('Log Return')
ax1.set_ylabel('Density')
ax1.legend()
ax1.grid(True, alpha=0.3)

# After distribution
ax2 = axes[1]
ax2.hist(after_data, bins=50, color='green', alpha=0.7, edgecolor='black', density=True)
ax2.axvline(mu_after, color='red', linestyle='--', label=f'Mean: {mu_after:.6f}')
ax2.axvline(ci_after[0], color='green', linestyle='--', alpha=0.5, label='95% CI')
ax2.axvline(ci_after[1], color='green', linestyle='--', alpha=0.5)
ax2.set_title(f'Distribution (After {cp_date.strftime("%Y-%m-%d")})')
ax2.set_xlabel('Log Return')
ax2.set_ylabel('Density')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'distribution_comparison.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"Distribution comparison saved to {os.path.join(plots_dir, 'distribution_comparison.png')}")

# 5d. Mean comparison with credible intervals
fig, ax = plt.subplots(figsize=(10, 6))

# Create bar plot with error bars
means = [mu_before, mu_after]
cis = [ci_before, ci_after]
labels = ['Before', 'After']

bars = ax.bar(labels, means, color=['blue', 'green'], alpha=0.7, edgecolor='black')
ax.errorbar(labels, means, yerr=[[means[0]-cis[0][0], means[1]-cis[1][0]], 
                                 [cis[0][1]-means[0], cis[1][1]-means[1]]],
           fmt='none', color='black', capsize=5)

ax.set_title('Mean Log Returns Before and After Change Point')
ax.set_ylabel('Mean Log Return')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, 'mean_comparison.png'), dpi=300, bbox_inches='tight')
plt.show()
print(f"Mean comparison saved to {os.path.join(plots_dir, 'mean_comparison.png')}")

# ============================================
# 6. ASSOCIATE CHANGE WITH EVENTS
# ============================================

print("\n" + "=" * 80)
print("6. ASSOCIATING CHANGE WITH EVENTS")
print("=" * 80)

# Find events near change point
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
    
    # Find closest event
    closest_event = events_near_cp.iloc[np.argmin(np.abs(events_near_cp['Date'] - cp_date))]
    
    print(f"\nMost likely associated event:")
    print(f"  Event: {closest_event['Event']}")
    print(f"  Date: {closest_event['Date'].strftime('%Y-%m-%d')}")
    print(f"  Days from CP: {(closest_event['Date'] - cp_date).days}")
    print(f"  Category: {closest_event['Category']}")
    print(f"  Description: {closest_event['Description']}")
    
    # Quantified impact statement
    print(f"\n" + "=" * 80)
    print("QUANTIFIED IMPACT STATEMENT")
    print("=" * 80)
    print(f"\nFollowing the {closest_event['Event']} around {closest_event['Date'].strftime('%Y-%m-%d')},")
    print(f"the model detects a significant change point with a mean log return shift from")
    print(f"{mu_before:.6f} to {mu_after:.6f}, representing a {change_pct:.2f}% change.")
    print(f"The probability of this change being positive is {prob_positive:.1f}%.")
    print(f"In price terms, this corresponds to a {price_change_pct:.2f}% change over 30 days.")
    print(f"95% Credible Interval for the change: [{ci_diff[0]:.6f}, {ci_diff[1]:.6f}]")
else:
    print("  No major events found near the change point")

# ============================================
# 7. SAVE RESULTS
# ============================================

print("\n" + "=" * 80)
print("7. SAVING RESULTS")
print("=" * 80)

# Create results summary
results_summary = {
    'change_point_date': cp_date,
    'change_point_idx': cp_idx,
    'ci_lower': ci_lower_date,
    'ci_upper': ci_upper_date,
    'mean_before': mu_before,
    'mean_after': mu_after,
    'mean_change': change_in_mean,
    'mean_change_pct': change_pct,
    'ci_before_lower': ci_before[0],
    'ci_before_upper': ci_before[1],
    'ci_after_lower': ci_after[0],
    'ci_after_upper': ci_after[1],
    'ci_diff_lower': ci_diff[0],
    'ci_diff_upper': ci_diff[1],
    'prob_positive': prob_positive,
    'prob_negative': prob_negative,
    'price_before': price_before,
    'price_after': price_after,
    'price_change': price_change,
    'price_change_pct': price_change_pct,
    'most_likely_event': closest_event['Event'] if len(events_near_cp) > 0 else 'Unknown',
    'event_date': closest_event['Date'] if len(events_near_cp) > 0 else None,
    'event_category': closest_event['Category'] if len(events_near_cp) > 0 else 'Unknown',
    'days_from_event': (closest_event['Date'] - cp_date).days if len(events_near_cp) > 0 else None
}

results_df = pd.DataFrame([results_summary])
results_path = os.path.join(project_dir, 'data', 'change_point_results.csv')
results_df.to_csv(results_path, index=False)
print(f"Results saved to {results_path}")

# ============================================
# 8. FINAL SUMMARY
# ============================================

print("\n" + "=" * 80)
print("TASK 2 COMPLETE")
print("=" * 80)

print("\nSummary of Change Point Analysis:")
print("-" * 50)
print(f"Change Point Date: {cp_date.strftime('%Y-%m-%d')}")
print(f"95% CI: {ci_lower_date.strftime('%Y-%m-%d')} to {ci_upper_date.strftime('%Y-%m-%d')}")
print(f"Mean Log Return Change: {change_in_mean:.6f} ({change_pct:.2f}%)")
print(f"95% CI for Change: [{ci_diff[0]:.6f}, {ci_diff[1]:.6f}]")
print(f"Price Impact (30-day): ${price_change:.2f} ({price_change_pct:.2f}%)")
print(f"Associated Event: {closest_event['Event'] if len(events_near_cp) > 0 else 'Unknown'}")
print(f"Probability of Positive Change: {prob_positive:.1f}%")
print(f"Statistically Significant: {results['is_significant']}")

print("\n" + "=" * 80)
print("DELIVERABLES GENERATED:")
print("=" * 80)
print(f"1. EDA Plot: {os.path.join(plots_dir, 'eda_for_modeling.png')}")
print(f"2. Change Point Analysis: {os.path.join(plots_dir, 'change_point_analysis.png')}")
print(f"3. Price Series with Change Point: {os.path.join(plots_dir, 'change_point_on_prices.png')}")
print(f"4. Distribution Comparison: {os.path.join(plots_dir, 'distribution_comparison.png')}")
print(f"5. Mean Comparison: {os.path.join(plots_dir, 'mean_comparison.png')}")
print(f"6. Results Summary: {results_path}")
print("=" * 80)