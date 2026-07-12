# Analysis Workflow Documentation

## Overview

This document outlines the complete analysis workflow for the Brent oil price change point detection project.

---

## Phase 1: Data Foundation (Task 1)

### 1.1 Data Loading

**Objective:** Load Brent oil price data from the source file.

**Process:**

1. Locate the data file in `data/raw/BrentOilPrices.csv`
2. Read CSV using pandas with date parsing
3. Verify data integrity (check for missing values, correct date range)
4. Create a backup of raw data

**Output:** Loaded DataFrame with columns: `Date`, `Price`

### 1.2 Data Cleaning

**Objective:** Ensure data quality for analysis.

**Process:**

1. Check for missing values
2. Handle missing values (forward fill or interpolation)
3. Verify date continuity (no gaps in trading days)
4. Validate price ranges (no negative prices)
5. Log data cleaning steps

**Output:** Cleaned DataFrame with verified data quality

### 1.3 Feature Engineering

**Objective:** Create additional features for analysis.

**Features Created:**

1. **Log Returns:** `log(Price_t) - log(Price_t-1)`
2. **Moving Averages:** 50-day and 200-day
3. **Rolling Volatility:** 30-day and 90-day standard deviation
4. **Decade:** Categorical variable for decade analysis

**Output:** Enhanced DataFrame with engineered features

### 1.4 Exploratory Data Analysis (EDA)

**Objective:** Understand data characteristics and patterns.

**Analysis Steps:**

1. **Time Series Visualization**
   - Plot raw prices over time
   - Identify major trends and cycles
   - Highlight potential break points

2. **Distribution Analysis**
   - Histograms of prices and returns
   - Statistical summary (mean, median, std, min, max)
   - Identify outliers

3. **Trend Analysis**
   - Moving averages (50-day, 200-day)
   - Decade-by-decade comparison
   - Identify long-term trends

4. **Stationarity Testing**
   - Augmented Dickey-Fuller test on prices
   - Augmented Dickey-Fuller test on log returns
   - Interpret results for modeling

5. **Volatility Analysis**
   - Rolling standard deviation
   - Identify high-volatility periods
   - Compare volatility across decades

6. **Autocorrelation Analysis**
   - ACF plots for prices and returns
   - Identify persistence patterns
   - Implications for modeling

**Outputs:**

- Visualization files in `scripts/plots/`
- Summary statistics in `data/processed/eda_summary.csv`

### 1.5 Events Compilation

**Objective:** Create a structured dataset of major events affecting oil prices.

**Process:**

1. Research major events (1987-2022)
2. Categorize events:
   - Conflict
   - OPEC Decision
   - Financial Crisis
   - Sanctions
   - Natural Disaster
3. Assign impact levels (High, Medium, Low)
4. Create structured CSV file

**Output:** `data/events.csv` with columns:

- `Date` (YYYY-MM-DD)
- `Event` (Name)
- `Category` (Event type)
- `Description` (Detailed explanation)
- `Expected_Impact` (High/Medium/Low)

---

## Phase 2: Change Point Modeling (Task 2)

### 2.1 Model Specification

**Objective:** Define the Bayesian change point model.

**Model Components:**

1. **Change Point (τ):** Discrete uniform prior over all possible days
2. **Mean Before (μ₁):** Normal prior
3. **Mean After (μ₂):** Normal prior
4. **Standard Deviation (σ):** Half-normal prior
5. **Likelihood:** Normal distribution with switch function

**Model Code:**

```python
with pm.Model() as change_point_model:
    tau = pm.DiscreteUniform('tau', lower=0, upper=n_obs-1)
    mu_1 = pm.Normal('mu_1', mu=0, sigma=0.1)
    mu_2 = pm.Normal('mu_2', mu=0, sigma=0.1)
    sigma = pm.HalfNormal('sigma', sigma=0.1)
    mu = pm.math.switch(tau >= np.arange(n_obs), mu_1, mu_2)
    returns_obs = pm.Normal('returns_obs', mu=mu, sigma=sigma, observed=log_returns)
```

### 2.2 MCMC Sampling

**Objective:** Sample from the posterior distribution.

**Sampling Parameters:**

- Draws: 2000
- Tune: 1000
- Chains: 4
- Cores: 1 (for reproducibility)
- Random Seed: 42

**Convergence Diagnostics:**

- R-hat (should be < 1.01)
- Effective Sample Size (ESS)
- Trace plots

### 2.3 Impact Quantification

**Objective:** Quantify the impact of the detected change.

**Metrics Calculated:**

- **Change Point Date:** Median date of τ
- **Confidence Interval:** 95% credible interval for τ
- **Mean Change:** μ₂ - μ₁
- **Percentage Change:** (μ₂ - μ₁) / μ₁ * 100
- **Price Impact:** Price change in USD
- **Price Impact %:** Percentage change in price

### 2.4 Event Association

**Objective:** Associate detected changes with specific events.

**Process:**

1. Find events within ±90 days of change point
2. Identify the closest event in time
3. Calculate days difference
4. Evaluate plausibility of association
5. Document qualitative support

---

## Phase 3: Dashboard Development (Task 3)

### 3.1 Backend (Flask)

**Objective:** Create API endpoints for data serving.

**Endpoints:**

- `/api/prices` - Historical price data
- `/api/events` - Events dataset
- `/api/change_points` - Detected change points
- `/api/impact` - Impact quantification

### 3.2 Frontend (React)

**Objective:** Create interactive visualization dashboard.

**Features:**

- **Price Chart:** Line chart with event overlays
- **Change Point Display:** Mark detected change points
- **Event Highlight:** Click events to see impact
- **Date Range Filter:** Select time periods
- **Volatility Display:** Show volatility metrics

### 3.3 Deployment

**Objective:** Deploy dashboard for stakeholder access.

**Deployment Steps:**

1. Package frontend for production
2. Deploy backend to cloud service
3. Configure environment variables
4. Set up SSL/TLS
5. Monitor performance

---

## Quality Assurance

### Testing Strategy

- **Unit Tests:** Test individual functions
- **Integration Tests:** Test data pipeline
- **Model Validation:** Test model performance

### Code Review Checklist

- [ ] Code follows PEP 8 standards
- [ ] Functions have docstrings
- [ ] Variables have descriptive names
- [ ] Error handling implemented
- [ ] Logging included
- [ ] Tests pass

### Documentation Standards

- [ ] README updated
- [ ] Docstrings for all functions
- [ ] Comments for complex logic
- [ ] Architecture diagrams
- [ ] Deployment instructions

---

## Timeline

| Phase | Task | Duration | Status |
|---|---|---|---|
| Phase 1 | Data Foundation | 2 days |  COMPLETE |
| Phase 2 | Change Point Modeling | 2 days | IN PROGRESS |
| Phase 3 | Dashboard Development | 2 days |  NOT STARTED |
| Phase 4 | Final Report | 1 day |  NOT STARTED |

---

## References

- Bayesian Changepoint Detection
- Time Series Analysis with Python
- Modern Portfolio Theory
