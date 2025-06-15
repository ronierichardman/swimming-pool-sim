"""
Swimming Pool Simulation (Python) - WITHOUT LOGGING
====================================================
This script simulates a swimming pool environment using the SimPy framework.
It models customer arrivals, swimming durations, and pool capacity constraints.
It is designed for performance testing without logging overhead.
Although we can disable logging if needed (as with another script "swimmingpool.py"),
the toggle logic still takes some time to execute.

USAGE:
python swimmingpool_simple.py --sim-duration 2400 --pool-capacity 50 --num-experiments 20
OPTIONS:
--sim-duration: Total simulation duration in minutes (default: 2400, which is 5 shifts of 8 hours)
--pool-capacity: Maximum number of swimmers allowed in the pool at a time (default: 50)
--num-experiments: Number of simulation experiments to run (default: 20)
"""

import simpy
import random
import time
import argparse
import json

RANDOM_SEED = 42
SIM_DURATION = 5 * 8 * 60 
POOL_CAPACITY = 50
MAX_QUEUE_LENGTH = 30
NUMBER_SIM_EXPERIMENTS = 20

class Statistics:
    def __init__(self):
        self.waiting_times = []
        self.total_customers = 0
        self.total_served = 0

    def record_wait(self, wait_time):
        self.waiting_times.append(wait_time)

class SwimmingPool:
    def __init__(self, env):
        self.env = env
        self.gate_open = True
        self.num_inside = 0
        self.num_waiting = 0
        self.capacity = POOL_CAPACITY
        self.stats = Statistics()

    def can_enter(self):
        return self.gate_open and self.num_inside < self.capacity

    def add_swimmer(self):
        self.num_inside += 1

    def remove_swimmer(self):
        self.num_inside -= 1

    def open_gate_cycle(self):
        while self.env.now < SIM_DURATION:
            self.gate_open = True
            yield self.env.timeout(1)
            self.gate_open = False
            yield self.env.timeout(59)

class Customer:
    id_counter = 0

    def __init__(self, env, pool):
        Customer.id_counter += 1
        self.name = f"Swimmer {Customer.id_counter}"
        self.pool = pool
        env.process(self.run(env))

    def run(self, env):
        self.pool.num_waiting += 1
        wait_start = env.now

        while not self.pool.can_enter():
            yield env.timeout(1)

        self.pool.num_waiting -= 1
        wait_end = env.now
        self.pool.stats.record_wait(wait_end - wait_start)
        self.pool.add_swimmer()

        # Determine stay duration
        w = random.random()
        if w <= 0.6:
            swim_time = random.uniform(115, 125)  # ~2h +/- 5min
        else:
            swim_time = random.uniform(75, 120)   # up to 45 min earlier

        yield env.timeout(swim_time)
        self.pool.remove_swimmer()
        self.pool.stats.total_served += 1

def arrival_process(env, pool):
    while env.now < SIM_DURATION:
        yield env.timeout(random.expovariate(1))  # Mean interarrival: 1 min
        if pool.num_waiting < MAX_QUEUE_LENGTH:
            Customer(env, pool)
            pool.stats.total_customers += 1

def run_single_experiment(experiment_number=0):
    # Set up random number generator with different seed for each experiment
    random.seed(RANDOM_SEED + experiment_number)
    Customer.id_counter = 0  
    env = simpy.Environment()
    pool = SwimmingPool(env)
    # Start arrival process
    env.process(arrival_process(env, pool))
    # Start gate cycle process
    env.process(pool.open_gate_cycle())
    env.run(until=SIM_DURATION)
    if hasattr(env, 'reset'):
        env.reset()
    return pool.stats

def run_all_experiments():
    total_times = []
    total_customers = 0
    total_served = 0
    avg_wait_times = []

    for experiment in range(1, NUMBER_SIM_EXPERIMENTS + 1):
        start_time = time.perf_counter()
        stats = run_single_experiment(experiment)
        end_time = time.perf_counter()

        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
        total_times.append(elapsed_time)
        total_customers += stats.total_customers
        total_served += stats.total_served
        avg_wait_times.append(sum(stats.waiting_times) / len(stats.waiting_times) if stats.waiting_times else 0)

    avg_time = sum(total_times) / len(total_times)
    min_time = min(total_times)
    max_time = max(total_times)
    avg_wait_time = sum(avg_wait_times) / len(avg_wait_times) if avg_wait_times else 0

    summary = {
        'framework': 'SimPy',
        'pool_capacity': POOL_CAPACITY,
        'sim_duration': SIM_DURATION,
        'num_experiments': NUMBER_SIM_EXPERIMENTS,
        'average_time': round(avg_time, 2),
        'min_time': round(min_time, 2),
        'max_time': round(max_time, 2),
        'total_time': round(sum(total_times) / 1000, 2),
        'total_customers': total_customers,
        'total_served': total_served,
        'average_waiting_time': round(avg_wait_time, 2)
    }
    
    print(f"Summary:{json.dumps(summary)}")

def main():
    parser = argparse.ArgumentParser(description='Starting SimPy Swimming Pool Simulation')
    parser.add_argument('--pool-capacity', type=int, default=50)
    parser.add_argument('--sim-duration', type=int, default=2400)
    parser.add_argument('--num-experiments', type=int, default=20)
    args = parser.parse_args()

    global POOL_CAPACITY, SIM_DURATION, NUMBER_SIM_EXPERIMENTS
    POOL_CAPACITY = args.pool_capacity
    SIM_DURATION = args.sim_duration
    NUMBER_SIM_EXPERIMENTS = args.num_experiments

    run_all_experiments()

if __name__ == "__main__":
    main()