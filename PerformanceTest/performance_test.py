"""
Comprehensive Performance Testing Framework
Tests both SimPy and SimLuxJS across multiple dimensions:
- Pool capacity
- Simulation duration 

This script runs performance tests, analyzes performance, and generates reports.
Usage Examples:
1. Quick test with default parameters:
   python performance_test.py --type quick
2. Comprehensive test with all configurations:
   python performance_test.py --type comprehensive
3. Stress test with high load scenarios:
   python performance_test.py --type stress
4. Custom output directory and filenames:
   python performance_test.py --output-dir my_results --csv-filename custom_results.csv --log-filename custom_log.log
"""

import subprocess
import sys
import os
import csv
import statistics
import json
from itertools import product
import numpy as np
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


OUTPUT_DIR = 'output'
POOL_CAPACITY_DIM = 'pool_capacity'
SIM_DURATION_DIM = 'sim_duration'
SIMPY = "SimPy"
SIMLUXJS = "SimLuxJS"

class TestResult:
    def __init__(self, framework, pool_capacity, sim_duration, avg_time, min_time, max_time, total_time, avg_customers, avg_served_customers, avg_waiting_time, config_id=None):
        self.framework = framework
        self.pool_capacity = pool_capacity
        self.sim_duration = sim_duration
        self.avg_time = avg_time # in milliseconds
        self.min_time = min_time # in milliseconds
        self.max_time = max_time # in milliseconds
        self.total_time = total_time # in milliseconds
        self.total_time_s = total_time / 1000  
        self.avg_customers = avg_customers  # average number of customers
        self.avg_served_customers = avg_served_customers  # average number of served customers
        self.avg_waiting_time = avg_waiting_time  # in minutes
        self.capacity_customer_per_hour = avg_customers / (sim_duration / 60)   # customers per hour
        self.config_id = config_id  # Unique identifier for the configuration
    
    def to_dict(self):
        return {
            'framework': self.framework,
            'pool_capacity': self.pool_capacity,
            'sim_duration': self.sim_duration,
            'total_time': self.total_time,
            'total_time_s': self.total_time_s,
            'avg_customers': self.avg_customers,
            'avg_served_customers': self.avg_served_customers,
            'avg_waiting_time': self.avg_waiting_time,
            'config_id': self.config_id,
            'capacity_customer_per_hour': self.capacity_customer_per_hour
        }

class PerformanceTestRunner:
    def __init__(self, output_dir=OUTPUT_DIR):
        self.results: list[TestResult] = []
        self.pool_capacities = [25, 50, 100, 200]  
        self.sim_durations = [2400, 4800, 7200, 9600, 12000]  # in minutes
        self.test_dimensions = {
            POOL_CAPACITY_DIM: self.pool_capacities,
            SIM_DURATION_DIM: self.sim_durations,
        }
        self.output_dir = output_dir
        self.setup_output_directory()

    def setup_output_directory(self):
        """Create output directory structure"""
        from datetime import datetime
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.csv_file = os.path.join(self.output_dir, f"performance_results_{self.timestamp}.csv")
        self.log_file = os.path.join(self.output_dir, f"performance_analysis_{self.timestamp}.log")
        self.summary_file = os.path.join(self.output_dir, f"performance_summary_{self.timestamp}.md")
        
        print(f"Output directory: {os.path.abspath(self.output_dir)}")
        
    def create_test_configurations(self, test_type='quick'):
        """Create different test configuration sets"""
        configs = []
        if test_type == 'quick':
            # Quick test - fewer combinations 
            # Test pool capacity scaling
            for capacity in self.pool_capacities[:3]:
                configs.append({
                    POOL_CAPACITY_DIM: capacity,
                    SIM_DURATION_DIM: self.sim_durations[0],
                })
            
            # Test simulation duration scaling
            for duration in self.sim_durations[:3]:
                configs.append({
                    POOL_CAPACITY_DIM: self.pool_capacities[0],
                    SIM_DURATION_DIM: duration,
                })

        elif test_type == 'comprehensive':
            # Full factorial test - all combinations
            for combo in product(*self.test_dimensions.values()):
                configs.append(dict(zip(self.test_dimensions.keys(), combo)))

        elif test_type == 'stress':
            # Stress test - high load scenarios
            configs = [
                {
                    POOL_CAPACITY_DIM: self.pool_capacities[-1],
                    SIM_DURATION_DIM: self.sim_durations[-1],
                },
                {
                    POOL_CAPACITY_DIM: self.pool_capacities[-2],
                    SIM_DURATION_DIM: self.sim_durations[-2],
                }
            ]
        return configs

    def run_single_test(self, config, framework):
        """Run test by passing parameters via command line"""
        print(f"Running {framework} test with config: {config}")
        
        if framework == SIMPY:
            cmd = [
                sys.executable, 'swimmingpool_simple.py',
                '--pool-capacity', str(config[POOL_CAPACITY_DIM]),
                '--sim-duration', str(config[SIM_DURATION_DIM]),
            ]
        else:
            cmd = [
                'node', 'swimmingpool_simple.js',
                '--pool-capacity', str(config[POOL_CAPACITY_DIM]),
                '--sim-duration', str(config[SIM_DURATION_DIM]),
            ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120) # 2 minute timeout
            # Parse Summary: line from output
            for line in result.stdout.split('\n'):
                if line.startswith('Summary:'):
                    json_result = json.loads(line[8:])  # Remove "Summary:" prefix
                    if json_result:
                        return TestResult(
                            framework=framework,
                            pool_capacity=config[POOL_CAPACITY_DIM],
                            sim_duration=config[SIM_DURATION_DIM],
                            total_time=json_result.get('total_time', 0),
                            avg_time=json_result.get('average_time', 0),
                            min_time=json_result.get('min_time', 0),
                            max_time=json_result.get('max_time', 0),
                            avg_customers=json_result.get('avg_customers', 0),
                            avg_served_customers=json_result.get('avg_served_customers', 0),
                            avg_waiting_time=json_result.get('average_waiting_time', 0)
                        )
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def run_all_tests(self, test_type='quick'):
        """Run the complete performance test suite"""
        configurations = self.create_test_configurations(test_type)
        
        print(f"Starting {test_type} performance tests")
        print(f"Testing {len(configurations)} configurations for both frameworks")
        print("=" * 60)
        
        for i, config in enumerate(configurations):
            print(f"\nConfiguration {i+1}/{len(configurations)}: {config}")
            
            # Test Python
            python_result = self.run_single_test(config, SIMPY)
            if python_result:
                python_result.config_id = i
                self.results.append(python_result)

            # Test JavaScript
            js_result = self.run_single_test(config, SIMLUXJS)
            if js_result:
                js_result.config_id = i
                self.results.append(js_result)

            # Quick comparison for this configuration
            if python_result and js_result:
                ratio = python_result.total_time / js_result.total_time
                print(f"  Speed ratio (Python/JS): {ratio:.3f}")
                if ratio > 1:
                    print(f"  -> JavaScript is {ratio:.2f}x faster")
                else:
                    print(f"  -> Python is {1/ratio:.2f}x faster")

    def save_results(self, filename=None):
        """Save results to CSV file"""
        if not self.results:
            print("No results to save")
            return
        
        if filename is None:
            filename = self.csv_file
        else:
            filename = os.path.join(self.output_dir, filename)

        json_results = [r.to_dict() for r in self.results]
        fieldnames = json_results[0].keys() if json_results else []
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(json_results)
        print(f"Results saved to {filename}")

    def analyze_performance(self):
        """Analyze and display performance results"""
        if not self.results:
            print("No results to analyze")
            return
            
        print("\n" + "="*60)
        print("PERFORMANCE ANALYSIS RESULTS")
        print("="*60)

        py_results = [r for r in self.results if r.framework == SIMPY]
        js_results = [r for r in self.results if r.framework == SIMLUXJS]

        print(f"\nTested {len(py_results)} Python configurations")
        print(f"Tested {len(js_results)} JavaScript configurations")

        # Performance comparison by dimension
        self._analyze_performance_by_dimension(py_results=py_results, js_results=js_results, dimension=POOL_CAPACITY_DIM, title='Pool Capacity')
        self._analyze_performance_by_dimension(py_results=py_results, js_results=js_results, dimension=SIM_DURATION_DIM, title='Simulation Duration') 

        # Overall performance summary
        if py_results and js_results:
            py_avg = statistics.mean([r.total_time_s for r in py_results])
            js_avg = statistics.mean([r.total_time_s for r in js_results])
            ratio = py_avg / js_avg
            print(f"\nOverall Performance Summary:")
            print(f"  Python average: {py_avg:.2f} s")
            print(f"  JavaScript average: {js_avg:.2f} s")
            print(f"  Average speed ratio (Python/JS): {ratio:.3f}")
            if ratio > 1:
                print(f"  -> JavaScript is {ratio:.2f}x faster")
            else:
                print(f"  -> Python is {1/ratio:.2f}x faster")


    def _analyze_performance_by_dimension(self, py_results, js_results, dimension, title):
        """Analyze results by specific dimension: pool_capacity, sim_duration, or num_experiments"""
        print(f"\n{title} Scaling Analysis:")
        print("-" * 30)

        py_dim_results = [r for r in py_results if getattr(r, dimension, None) is not None]
        js_dim_results = [r for r in js_results if getattr(r, dimension, None) is not None]
        if not py_dim_results or not js_dim_results:
            print(f"  No results available for {title} analysis")
            return
        
        py_avg = statistics.mean([r.total_time_s for r in py_dim_results])
        js_avg = statistics.mean([r.total_time_s for r in js_dim_results])
        ratio = py_avg / js_avg
        print(f"  Average Python {title}: {py_avg:.2f} s")
        print(f"  Average JavaScript {title}: {js_avg:.2f} s")
        print(f"  Speed ratio (Python/JS): {ratio:.3f}")
        if ratio > 1:
            print(f"  -> JavaScript is {ratio:.2f}x faster")
        else:
            print(f"  -> Python is {1/ratio:.2f}x faster")

    def create_simulation_results_plot(self):
        """Create separate plots for each simulation metric"""
        
        if not self.results:
            print("No results available for simulation plots")
            return
            
        print("\nCreating individual simulation metric plots...")
        
        # Convert results to DataFrame
        json_results = [r.to_dict() for r in self.results]
        df = pd.DataFrame(json_results)
        
        # Metrics to plot separately
        metrics = [
            ('avg_waiting_time', 'Average Waiting Time (minutes)'),
            ('avg_customers', 'Average Total Customers'),
            ('total_time_s', 'Execution Time (seconds)'),
            ('capacity_customer_per_hour', 'Capacity (customers/hour)')
        ]
        
        # Color scheme for frameworks
        colors = {SIMPY: '#2E86AB', SIMLUXJS: "#F2DE04"}
        
        # Get unique configurations
        configs = df[[POOL_CAPACITY_DIM, SIM_DURATION_DIM]].drop_duplicates().reset_index(drop=True)

        # Create separate plot for each metric
        for metric_key, metric_title in metrics:
            plt.figure(figsize=(14, 8))  # Increased width to accommodate legend
            
            # Prepare data for plotting
            simpy_values = []
            simlux_values = []
            x_labels = []
            
            for _, config in configs.iterrows():
                pool_cap = config[POOL_CAPACITY_DIM]
                sim_dur = config[SIM_DURATION_DIM]

                # Create label showing actual config values
                config_label = f"P{pool_cap}\nD{sim_dur//60}h"
                x_labels.append(config_label)
                
                # Get values for each framework
                simpy_data = df[(df['framework'] == SIMPY) & 
                            (df[POOL_CAPACITY_DIM] == pool_cap) & 
                            (df[SIM_DURATION_DIM] == sim_dur)]
                simlux_data = df[(df['framework'] == SIMLUXJS) & 
                                (df[POOL_CAPACITY_DIM] == pool_cap) & 
                                (df[SIM_DURATION_DIM] == sim_dur)]

                simpy_val = simpy_data[metric_key].mean() if not simpy_data.empty else 0
                simlux_val = simlux_data[metric_key].mean() if not simlux_data.empty else 0
                
                simpy_values.append(simpy_val)
                simlux_values.append(simlux_val)
            
            # Create grouped bar chart
            x = np.arange(len(x_labels))
            width = 0.35
            
            bars1 = plt.bar(x - width/2, simpy_values, width, label='SimPy', 
                        color=colors[SIMPY], alpha=0.8, edgecolor='black', linewidth=0.5)
            bars2 = plt.bar(x + width/2, simlux_values, width, label='SimLuxJS', 
                        color=colors[SIMLUXJS], alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Customize plot
            plt.title(f'{metric_title}\nSimPy vs SimLuxJS Comparison', 
                    fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Configuration (Pool Capacity / Simulation Duration)', fontsize=12, fontweight='bold')
            plt.ylabel(metric_title.split('(')[0].strip(), fontsize=12, fontweight='bold')
            plt.xticks(x, x_labels, rotation=0)
            plt.legend(fontsize=11, loc='upper left')
            plt.grid(True, alpha=0.3, axis='y')

            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom', 
                            fontsize=7, fontweight='bold', rotation=45)

            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom', 
                            fontsize=7, fontweight='bold', rotation=45)

            # Use tight_layout with padding to accommodate the legend
            plt.tight_layout()
            
            # Save plot
            safe_metric_name = metric_key.replace('_', '-')
            plot_file = os.path.join(self.output_dir, f'{safe_metric_name}_{self.timestamp}.png')
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"{metric_title} plot saved: {os.path.basename(plot_file)}")
    
    
    def create_detailed_metrics_table(self):
        """Create a detailed metrics comparison table"""
        print("\nDetailed Metrics Summary:")
        print("=" * 80)
        
        if not self.results:
            print("No results available")
            return
        
        # Group results by framework
        simpy_results = [r for r in self.results if r.framework == SIMPY and r.pool_capacity == 100 and r.sim_duration == 2400]
        simlux_results = [r for r in self.results if r.framework == SIMLUXJS and r.pool_capacity == 100 and r.sim_duration == 2400]

        if not simpy_results or not simlux_results:
            print("Insufficient data for comparison")
            return
        
        # Calculate metrics
        metrics = [
            ('avg_waiting_time', 'Average Waiting Time (min)'),
            ('avg_customers', 'Average Total Customers'),
            ('avg_served_customers', 'Average Served Customers'),
            ('capacity_customer_per_hour', 'Capacity (customers/hour)'),
        ]
        
        print(f"{'Metric':<30} {'SimPy':<15} {'SimLuxJS':<15} {'Difference':<15}")
        print("-" * 80)
        
        for metric_key, metric_name in metrics:
            simpy_avg = statistics.mean([getattr(r, metric_key) for r in simpy_results])
            simlux_avg = statistics.mean([getattr(r, metric_key) for r in simlux_results])
            
            if simpy_avg != 0:
                diff_pct = ((simlux_avg - simpy_avg) / simpy_avg) * 100
                diff_str = f"{diff_pct:+.3f}%"
            else:
                diff_str = "N/A"
            
            print(f"{metric_name:<30} {simpy_avg:<15.2f} {simlux_avg:<15.2f} {diff_str:<15}")


    def create_performance_heatmap(self):
        """Create heat maps showing performance patterns"""
        print("\nCreating performance heat maps...")

        if not self.results:
            return
        # Convert results to DataFrame
        json_results = [r.to_dict() for r in self.results]
        df = pd.DataFrame(json_results)

        # Create pivot tables for heat maps
        for framework in [SIMPY, SIMLUXJS]:
            framework_df = df[df['framework'] == framework]
            
            if len(framework_df) < 4:
                continue
                
            # Create heat map for pool_capacity vs sim_duration
            try:
                pivot_table = framework_df.pivot_table(
                    values='total_time_s', 
                    index='pool_capacity', 
                    columns='sim_duration', 
                    aggfunc='mean'
                )
                
                plt.figure(figsize=(12, 8))
                sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='YlOrRd', 
                        cbar_kws={'label': 'Execution Time (seconds)'})
                plt.title(f'{framework} Performance Heat Map', fontsize=16, fontweight='bold')
                plt.xlabel('Simulation Duration (minutes)', fontsize=12)
                plt.ylabel('Pool Capacity', fontsize=12)
                plt.tight_layout()
                
                # Save in output directory
                heatmap_file = os.path.join(self.output_dir, f'{framework.lower()}_heatmap__{self.timestamp}.png')
                plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
    
            except Exception as e:
                print(f"Error creating {framework} heatmap: {e}")
            finally:
                plt.close()
                print(f"{framework} heatmap saved: {os.path.basename(heatmap_file)}")

    def analyze_results(self):
        """Comprehensive analysis with all metrics including file outputs"""
         # Run all analyses
        self.analyze_performance()
        # Create visualizations
        self.create_simulation_results_plot()
        self.create_detailed_metrics_table()
        self.create_performance_heatmap()        
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)


def main():
    parser = argparse.ArgumentParser(description='Run comprehensive performance tests')
    parser.add_argument('--type', choices=['quick', 'comprehensive', 'stress'], 
                       default='quick', help='Type of test to run')
    parser.add_argument('--output-dir', default=OUTPUT_DIR,
                       help='Output directory for all results')
    parser.add_argument('--csv-filename', 
                       help='Custom CSV filename (optional)')
    parser.add_argument('--log-filename',
                       help='Custom log filename (optional)')
    
    args = parser.parse_args()
    
    # Create runner with output directory
    runner = PerformanceTestRunner(output_dir=args.output_dir)
    
    # Setup custom log file if specified
    if args.log_filename:
        log_file = os.path.join(runner.output_dir, args.log_filename)
    else:
        log_file = runner.log_file
    
    # Setup output redirection
    tee_output = TeeOutput(log_file)
    
    try:
        # Redirect stdout to both console and file
        sys.stdout = tee_output
        
        print("SimPy vs SimLuxJS Comprehensive Performance Testing Framework")
        print("=" * 70)

        # Run tests
        runner.run_all_tests(args.type)

        # Save CSV results
        if args.csv_filename:
            runner.save_results(args.csv_filename)
        else:
            runner.save_results()
        
        # Comprehensive analysis (creates all outputs)
        runner.analyze_results()

                
    finally:
        # Restore stdout and close file
        sys.stdout = tee_output.console
        tee_output.close()


class TeeOutput:
    """Write to both file and console"""
    def __init__(self, file_path):
        self.file = open(file_path, 'w')
        self.console = sys.stdout
    
    def write(self, message):
        self.file.write(message)
        self.file.flush()  # Ensure immediate write
        self.console.write(message)
    
    def flush(self):
        self.file.flush()
        self.console.flush()
    
    def close(self):
        self.file.close()


if __name__ == "__main__":
    main()
