# Change Point Analysis and Statistical Modeling of Brent Oil Prices

## Project Overview

This project analyzes how major geopolitical events, OPEC decisions, and economic shocks affect Brent oil prices using Bayesian change point detection. The analysis identifies structural breaks in oil price time series and associates them with specific events.

- **Client:** Birhan Energies
- **Course:** 10 Academy Kifiya AIM 9 - Week 10 Challenge
- **Date:** July 12, 2026
- **Author:** Hawi Chala

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Analysis Workflow](#analysis-workflow)
- [Key Findings](#key-findings)
- [Dependencies](#dependencies)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [References](#references)

---

## Setup Instructions

### 1. Create a Virtual Environment

\`\`\`bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
\`\`\`

### 2. Install Dependencies

\`\`\`bash
pip install --upgrade pip
pip install -r requirements.txt
\`\`\`

### 3. Download the Data

Place the Brent oil price data file (`BrentOilPrices.csv`) in the `data/raw/` directory.

### 4. Run the Analysis

\`\`\`bash
# Task 1: Data Exploration and EDA
python scripts/task1_exploration.py

# Task 2: Change Point Detection
python scripts/task2_change_point.py

# Run all tests
pytest tests/ -v
\`\`\`

---

## Analysis Workflow

### Phase 1: Data Foundation (Task 1) - COMPLETE

- Load and preprocess Brent oil price data (1987-2022)
- Perform comprehensive exploratory data analysis (EDA)
- Compile events dataset with 21 major events
- Test for stationarity using Augmented Dickey-Fuller test
- Analyze volatility patterns and autocorrelation
- Generate visualizations and summary statistics

**Key Deliverables:**

- Cleaned and processed data
- Events dataset with categories and impact levels
- EDA visualizations (4 plots)
- Summary statistics and initial findings

### Phase 2: Change Point Modeling (Task 2) - IN PROGRESS

- Build Bayesian change point model using PyMC
- Define discrete uniform prior for change point location
- Run MCMC sampling with convergence diagnostics (R-hat)
- Identify structural breaks in the time series
- Quantify impact of changes (mean change, price impact)
- Associate changes with specific events

**Key Deliverables:**

- Trained change point model
- Posterior distributions and trace plots
- Quantified impact statements
- Event association analysis

### Phase 3: Interactive Dashboard (Task 3) - NOT STARTED

- Develop Flask backend API for data serving
- Create React frontend with interactive visualizations
- Implement event highlight functionality
- Add filters and date range selectors
- Deploy dashboard for stakeholder access

**Key Deliverables:**

- Working Flask API with documented endpoints
- React frontend with interactive charts
- Screenshots and deployment instructions

---

## Key Findings

### Data Characteristics

| Metric | Value |
|---|---|
| Time Period | May 20, 1987 – November 14, 2022 |
| Observations | 9,011 trading days |
| Min Price | $9.10 per barrel |
| Max Price | $143.95 per barrel |
| Mean Price | $48.42 per barrel |
| Median Price | $38.57 per barrel |

### Stationarity Results

| Series | ADF Statistic | p-value | Result |
|---|---|---|---|
| Raw Prices | -1.9939 | 0.2893 | NON-STATIONARY |
| Log Returns | -16.4271 | 0.0000 | STATIONARY |

**Implication:** First-order differencing (d=1) is required for ARIMA modeling.

### Price Trends by Decade

| Decade | Mean Price | Std Dev | Min Price | Max Price |
|---|---|---|---|---|
| 1980s | $17.03 | $2.10 | $11.20 | $22.25 |
| 1990s | $18.35 | $4.32 | $9.10 | $41.45 |
| 2000s | $49.46 | $25.78 | $16.51 | $143.95 |
| 2010s | $79.35 | $26.09 | $26.01 | $128.14 |
| 2020s | $70.60 | $27.04 | $9.12 | $133.18 |

### Events Dataset

| Category | Count | Examples |
|---|---|---|
| Conflict | 9 | Gulf War, Iraq War, Arab Spring, Russia-Ukraine |
| OPEC Decision | 6 | Production cuts, production decisions |
| Financial Crisis | 4 | Asian Crisis, Lehman Brothers, COVID-19 |
| Sanctions | 1 | Iran Sanctions Lifted |
| Natural Disaster | 1 | Hurricane Katrina |

**Total Events:** 21 major events (17 High Impact, 4 Medium Impact)

---

## Dependencies

### Core Packages

| Package | Version | Purpose |
|---|---|---|
| pandas | 2.0.3 | Data manipulation |
| numpy | 1.24.3 | Numerical operations |
| scipy | 1.11.1 | Scientific computing |

### Visualization

| Package | Version | Purpose |
|---|---|---|
| matplotlib | 3.7.2 | Data visualization |
| seaborn | 0.12.2 | Statistical visualizations |

### Statistical Modeling

| Package | Version | Purpose |
|---|---|---|
| statsmodels | 0.14.0 | Statistical testing |
| pymc | 5.7.2 | Bayesian modeling |
| arviz | 0.16.1 | Bayesian diagnostics |

### Testing & Development

| Package | Version | Purpose |
|---|---|---|
| pytest | 7.4.0 | Unit testing |
| pytest-cov | 4.1.0 | Code coverage |
| jupyter | 1.0.0 | Interactive notebooks |

---

## Documentation

Detailed documentation is available in the `docs/` directory:

- **Analysis Workflow** - Step-by-step analysis process
- **Assumptions and Limitations** - Key assumptions and limitations
- **Interim Report** - Complete interim submission report with visualizations

### Generated Visualizations

All plots are saved to `scripts/plots/`:

- `brent_eda_overview.png` - EDA overview with prices, returns, distributions
- `brent_trend_analysis.png` - Price trends with moving averages
- `brent_volatility_analysis.png` - Volatility patterns and distribution
- `brent_acf_analysis.png` - Autocorrelation analysis

---

## Contributing

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write docstrings for all functions
- Include unit tests for new features
- Update documentation as needed

### Code Review Checklist

- [ ] Code follows PEP 8 standards
- [ ] Functions have docstrings
- [ ] Variables have descriptive names
- [ ] Error handling implemented
- [ ] Tests pass
- [ ] Documentation updated

---

## License

This project is part of the 10 Academy Kifiya AIM 9 program and is intended for educational purposes.

---

## Contact

- **Author:** Hawi Chala
- **GitHub:** [@hawi088](https://github.com/hawi088)
- **Course:** 10 Academy Kifiya AIM 9 - Week 10 Challenge
- **Project:** Change Point Analysis and Statistical Modeling of Brent Oil Prices

---

## References

### Academic References

- Bayesian Change Point Detection with PyMC3
- Change Point Detection in Time Series
- Monte Carlo Markov Chain (MCMC) Explained

### Data Sources

- Brent Oil Price Data (1987-2022)
- Historical Event Records

### Tools Used

- Python 3.11
- PyMC for Bayesian modeling
- Statsmodels for statistical testing
- Matplotlib/Seaborn for visualization

---

*Last Updated: July 12, 2026*