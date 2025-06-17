# Swimming Pool Simulation: SimPy vs SimLuxJS Performance Comparison

## Project Status: COMPLETED 

This project implements and compares identical swimming pool simulations using two different discrete event simulation frameworks: Python's SimPy and JavaScript's SimLuxJS. 

## Project Structure

```
swimming-pool-sim/
├── PerformanceTest/
│   ├── performance_test.py         # Main testing framework 
│   ├── compare_tool.py             # Quick performance comparison tool
│   ├── swimmingpool_simple.py      # SimPy implementation (performance optimized)
│   ├── swimmingpool_simple.js      # SimLuxJS implementation (performance optimized)
│   ├── swimmingpool.py             # SimPy implementation (full logging)
│   ├── swimmingpool.js             # SimLuxJS implementation (full logging)
│   ├── output/                     # Generated results and visualizations
│   └── SLX/                        # Reference SLX models
├── SimLuxJS/                       # SimLuxJS framework
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies
└── README.md                       # Project documentation
```

## Prerequisites

This project requires both Python and Node.js to be installed on your system.

### Install Python (3.8 or higher)

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python

# Or download from https://www.python.org/downloads/
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Windows:**
```bash
# Download from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

### Install Node.js (16.0 or higher)

**macOS:**
```bash
# Using Homebrew (recommended)
brew install node

# Or download from https://nodejs.org/
```

**Linux (Ubuntu/Debian):**
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or download from https://nodejs.org/
```

**Windows:**
```bash
# Download from https://nodejs.org/
# The installer includes npm by default
```

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ronierichardman/swimming-pool-sim.git
cd swimming-pool-sim
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Node.js Dependencies
```bash
# Install Node.js dependencies
npm install
```

## Running the Project

### Quick Performance Comparison Tool

For a fast head-to-head performance comparison between SimPy and SimLuxJS:

```bash
# Activate Python environment (if not already active)
source venv/bin/activate

# Navigate to PerformanceTest directory
cd PerformanceTest

# Run quick comparison
python compare_tool.py
```

**What it does:**
- Runs both SimPy and SimLuxJS simulations with default parameters
- Measures total execution time for each framework
- Extracts key performance metrics (average time per experiment, total simulation time)
- Displays a direct comparison showing which framework is faster
- Calculates speed ratios between the frameworks

### Performance Testing Framework

The main performance testing framework provides comprehensive analysis and visualization:

```bash
# Activate Python environment (if not already active)
source venv/bin/activate

# Navigate to PerformanceTest directory
cd PerformanceTest

# Run quick performance test (recommended for development)
python performance_test.py --type quick

# Run comprehensive test (all combinations - takes longer)
python performance_test.py --type comprehensive

# Run stress test (high-load scenarios)
python performance_test.py --type stress

# Custom output directory
python performance_test.py --type quick --output-dir my_results
```

### Individual Simulation Runs

#### Python (SimPy) Implementation
```bash
cd PerformanceTest

# Basic run with default parameters
python swimmingpool_simple.py

# Custom parameters
python swimmingpool_simple.py --pool-capacity 100 --sim-duration 4800 --num-experiments 20

# Full logging version
python swimmingpool.py
```

#### JavaScript (SimLuxJS) Implementation
```bash
cd PerformanceTest

# Basic run with default parameters
node swimmingpool_simple.js

# Custom parameters
node swimmingpool_simple.js --pool-capacity 100 --sim-duration 4800 --num-experiments 20

# Full logging version
node swimmingpool.js
```

## Output and Results

The performance testing framework generates:

- **CSV Files**: Raw performance data (`performance_results_TIMESTAMP.csv`)
- **Heat Maps**: Visual performance patterns (`*_heatmap_TIMESTAMP.png`)
- **Log Files**: Detailed execution logs (`performance_analysis_TIMESTAMP.log`)
- **Simulation results Plots**: Visual representations of simulation performance metrics and comparisons (`*_TIMESTAMP.png`)

All outputs are saved in the `PerformanceTest/output/` directory by default.

## Simulation Model

The swimming pool simulation models a real-world scenario with:

- **Pool Capacity**: Configurable maximum number of concurrent swimmers
- **Customer Arrivals**: Exponential inter-arrival times with time-varying rates
- **Service Process**: Swimming sessions with normally distributed durations
- **Queue Management**: FIFO queue with maximum length limits
- **Gate Control**: Periodic opening/closing cycles for crowd management
- **Statistics Collection**: Waiting times, total customers and total served customers

## Development Workflow

### Quick Performance Check
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Quick comparison to see which framework is faster
cd PerformanceTest
python compare_tool.py
```

### Quick Analysis Cycle
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Make changes to simulation files
# 3. Run quick test
cd PerformanceTest
python performance_test.py --type quick

# 4. Check results in output/ directory
```

### Full Analysis Cycle
```bash
python performance_test.py --type comprehensive
```
