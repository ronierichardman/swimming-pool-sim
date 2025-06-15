#!/usr/bin/env python3

import subprocess
import time
import sys

swimmingpool_py = 'swimmingpool_simple.py' 
swimmingpool_js = 'swimmingpool_simple.js'

def run_python_performance():
    """Run the Python SimPy performance test"""
    print("Running Python SimPy performance test...")
    try:
        start_time = time.perf_counter()
        result = subprocess.run([sys.executable, swimmingpool_py], 
                              capture_output=True, text=True, timeout=120)
        end_time = time.perf_counter()

        if result.returncode != 0:
            print(f"Python test failed: {result.stderr}")
            return None
            
        # Parse the output to extract performance metrics
        output_lines = result.stdout.strip().split('\n')
        python_results = {
            'total_time': end_time - start_time,
            'output': result.stdout,
            'success': True
        }
        
        # Extract key metrics from output
        for line in output_lines:
            if 'Average time:' in line:
                python_results['avg_time'] = float(line.split(':')[1].strip().split()[0])
            elif 'Total time:' in line and 'seconds' in line:
                python_results['sim_total_time'] = float(line.split(':')[1].strip().split()[0])
                
        return python_results
        
    except subprocess.TimeoutExpired:
        print("Python test timed out")
        return None
    except Exception as e:
        print(f"Error running Python test: {e}")
        return None

def run_javascript_performance():
    """Run the JavaScript SimLuxJS performance test"""
    print("Running JavaScript SimLuxJS performance test...")
    try:
        start_time = time.perf_counter()
        result = subprocess.run(['node', swimmingpool_js], 
                              capture_output=True, text=True, timeout=120)
        end_time = time.perf_counter()

        if result.returncode != 0:
            print(f"JavaScript test failed: {result.stderr}")
            return None
            
        # Parse the output to extract performance metrics
        output_lines = result.stdout.strip().split('\n')
        js_results = {
            'total_time': end_time - start_time,
            'output': result.stdout,
            'success': True
        }
        
        # Extract key metrics from output
        for line in output_lines:
            if 'Average time:' in line:
                js_results['avg_time'] = float(line.split(':')[1].strip().split()[0])
            elif 'Total time:' in line and 'seconds' in line:
                js_results['sim_total_time'] = float(line.split(':')[1].strip().split()[0])
                
        return js_results
        
    except subprocess.TimeoutExpired:
        print("JavaScript test timed out")
        return None
    except Exception as e:
        print(f"Error running JavaScript test: {e}")
        return None


def compare_results(python_results, js_results):
    """Compare and display the performance results"""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON: SimPy vs SimLuxJS")
    print("="*60)
    
    if python_results and js_results:
        print(f"\nPython SimPy Results:")
        print(f"  - Total execution time: {python_results['total_time']:.2f} seconds")
        if 'avg_time' in python_results:
            print(f"  - Average per experiment: {python_results['avg_time']:.2f} ms")
        if 'sim_total_time' in python_results:
            print(f"  - Simulation total time: {python_results['sim_total_time']:.2f} seconds")
            
        print(f"\nJavaScript SimLuxJS Results:")
        print(f"  - Total execution time: {js_results['total_time']:.2f} seconds")
        if 'avg_time' in js_results:
            print(f"  - Average per experiment: {js_results['avg_time']:.2f} ms")
        if 'sim_total_time' in js_results:
            print(f"  - Simulation total time: {js_results['sim_total_time']:.2f} seconds")
            
        # Calculate performance ratio
        speed_ratio = python_results['total_time'] / js_results['total_time']
        print(f"\nPerformance Comparison:")
        if speed_ratio > 1:
            print(f"  - JavaScript is {speed_ratio:.2f}x faster than Python")
        else:
            print(f"  - Python is {1/speed_ratio:.2f}x faster than JavaScript")
            
        print(f"  - Speed ratio (Python/JavaScript): {speed_ratio:.3f}")
        
    else:
        print("\nCould not complete comparison due to test failures")
        if python_results:
            print("Python test completed successfully")
        else:
            print("Python test failed")
            
        if js_results:
            print("JavaScript test completed successfully")
        else:
            print("JavaScript test failed")

def main():
    print("Starting SimPy vs SimLuxJS Performance Comparison")
    print("=" * 50)
    
    # Run both performance tests
    python_results = run_python_performance()
    js_results = run_javascript_performance()
    
    # Compare and display results
    compare_results(python_results, js_results)

if __name__ == "__main__":
    main()
