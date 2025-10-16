# FP-Growth Algorithm Implementation

This project implements the **FP-Growth (Frequent Pattern Growth) algorithm** for mining frequent itemsets from transactional data using Python. The implementation is validated with small illustrative examples and benchmarked on the real-world [Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail) from UCI Machine Learning Repository.

## Prerequisites

- Python 3.7 or higher
- pip package manager

Setup: install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Run Validation Tests

Validate the implementation with comprehensive test cases:

```bash
python validate.py
```

This runs 4 test suites:
- Simple transaction examples
- Classic textbook examples
- Edge cases (empty, single item, etc.)
- Support threshold variations

### 2. Run Benchmark Experiments

Run comprehensive experiments on the Online Retail dataset:

```bash
python run_benchmark.py
```

This will:
- Attempt to download and preprocess the Online Retail dataset
- Run support variation experiments (0.01 to 0.15)
- Run scalability experiments (500 to 10000 transactions)
- Track running time and memory consumption for all experiments
- Create visualizations and save results



Results are saved to the `results/` directory, including the raw data and visualizations.

## Project Structure

```
ESE589-FP-growth-project/
├── fp_growth.py          # Core FP-growth algorithm implementation with memory tracking
├── validate.py           # Validation test suite
├── preprocess.py         # Data preprocessing for Online Retail dataset
├── benchmark.py          # Benchmark experiment functions with memory profiling
├── run_benchmark.py      # Main benchmark script with data fallback
├── requirements.txt      # Python package dependencies
├── README.md            # This file
├── data/                # Downloaded datasets (created automatically)
└── results/             # Experiment results (created automatically)
```
