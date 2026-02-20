# Markov Trading Framework

A quantitative research framework that models equity markets as Markov chains, using technical state transitions to identify favorable trading conditions and optimize position sizing via the Kelly criterion.

## Core Idea

Instead of using technical indicators as static signals ("RSI is below 30, buy"), this framework treats the market as a **state machine**. It defines discrete states from technical conditions, calculates empirical transition probabilities between states, and bets only when the transition matrix favors a profitable move.

Think of it as card counting for equities: you're not predicting the next card, you're estimating when the deck is in your favor.

## Architecture

```
Scraper (Yahoo Finance)
    ↓
Price Data + 20 Technical Features (SMA, EMA, RSI, MACD, Bollinger, etc.)
    ↓
State Determiner → Discrete States (e.g., "growth phase 2" or "decline phase 3")
    ↓
Transition Probability Calculator → Empirical Transition Matrix
    ↓
Strategy Optimizer (Kelly Criterion or Geometric Mean) → Bet Sizing per State
    ↓
Backtester → Portfolio Performance vs. Buy-and-Hold + Random Baseline
    ↓
Report Generator → PDF Graphs + JSON Results
```

## Components

```
Markov_Structured/
├── Scrapers/                  # Data fetching
│   └── yf_scraper.py         # Yahoo Finance integration
│
├── Basic_Feature_Selection/   # Technical indicator generation
│   └── feature_addition.py   # 20+ indicators (RSI, MACD, Bollinger, CMF, Aroon, etc.)
│
├── Markov_State_Determiners/  # State space definitions
│   ├── State_Determiner.py   # Abstract base class
│   ├── Czech_State_Determiner.py    # 8 states from academic model (g1-4, d1-4)
│   ├── MA_State_Determiner.py      # Moving average crossover states
│   └── Czech_MA_Safe_State_Determiner.py  # Hybrid model
│
├── Transition_Probability_Calculation/  # Probability estimation
│   ├── Empirical_Calculator.py         # 1D empirical transition probabilities
│   └── Contour_Empirical_Calculator.py # 2D intersecting model probabilities
│
├── Markov_Strategy_Determiner/  # Position sizing optimization
│   ├── Geometric_Mean_Probability_Optimizer.py  # Weighted geometric mean scoring
│   └── Kelly_Strategy_Determiner.py  # Kelly criterion via KDE-fitted distributions
│
├── Markov_Strategies/         # Executable trading strategies
│   └── Czech_State_Determiner/
│       ├── Czech_Strategy1.py # Pre-optimized leverage per state
│       └── Geometric_Mean_Optimal_Strategy.py
│
├── Backtester/                # Performance evaluation
│   └── Markov_Backtester.py   # vs. buy-and-hold + percentile vs. 100 random simulations
│
├── Markov_Analytics/          # Statistical analysis
│   ├── Analytics_Util.py      # Covariance analysis (normal, injected-state, injected-return)
│   ├── Intersecting_Models_Analytics_Util.py  # Multi-model correlation
│   └── Optimal_Quick_Calculation.py
│
├── Kelly_Box/                 # Kelly criterion utilities
│   └── Kelly_Box.py          # Optimal bet fraction from return distributions
│
├── Driver/                    # Pipeline orchestration
│   └── driver.py             # End-to-end: scrape → states → optimize → backtest → report
│
└── report_processor.py        # PDF report generation with matplotlib
```

## State Models

**Czech Model** (based on academic literature): Classifies each trading day into one of 8 states based on return magnitude relative to rolling standard deviation:
- `g1`–`g4`: Growth phases (increasing intensity)
- `d1`–`d4`: Decline phases (increasing intensity)

**Moving Average Model**: States defined by price position relative to moving averages.

**Contour Analysis**: Intersects two state models (e.g., Return × Volume) into a 2D transition matrix, identifying when specific combinations of conditions predict favorable transitions.

## Optimization

**Kelly Criterion**: Fits kernel density estimates to state-conditional return distributions, then derives the mathematically optimal bet fraction that maximizes long-run geometric growth.

**Geometric Mean Optimizer**: Scores each state by the probability-weighted geometric mean of returns across all possible transitions. States with positive expected geometric growth get allocated; others are skipped.

## Backtesting

The backtester validates strategies against two baselines:
1. **Buy-and-hold**: Standard benchmark
2. **Random simulation (N=100)**: Generates 100 random trading strategies with the same activity frequency but random entry/exit days. Reports the strategy's percentile rank against this null distribution.

Also computes three covariance variants (normal, state-injected-zero, return-injected-zero) to decompose the relationship between state predictions and returns.

## Tech Stack

Python, NumPy, Pandas, SciPy (KDE), matplotlib (PDF reports), Yahoo Finance API, `ta` (technical analysis library)

## Status

Research framework / proof of concept. Built for exploring whether Markov state transitions provide a statistically significant edge in equity trading.
