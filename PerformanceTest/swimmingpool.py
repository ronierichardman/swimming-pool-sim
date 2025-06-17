"""
Swimming Pool Simulation (Python) - WITH LOGGING
====================================================
This script simulates a swimming pool environment using SimPy.
It models customer arrivals, swimming durations, and pool capacity constraints.
With configurable logging modes, it allows for testing and debugging.

LOGGING MODES:
- 'console': Real-time output to terminal
- 'file': Write all messages to LOG_FILE
- 'none': No output (for performance testing)

USAGE:
1. Change OUTPUT_MODE constant below to desired mode
2. Run: python swimmingpool.py
3. Check results in console or LOG_FILE
"""

import simpy
import random
import statistics
import time

OUTPUT_MODE = 'none'  # 'console', 'file', or 'none'
LOG_FILE = 'simulation_py_output.log'

RANDOM_SEED = 42
SIM_DURATION = 5 * 8 * 60 
POOL_CAPACITY = 100
MAX_QUEUE_LENGTH = 30
NUMBER_SIM_EXPERIMENTS = 20

# Logging function that respects OUTPUT_MODE
def log_message(message):
    if OUTPUT_MODE == 'console':
        print(message)
    elif OUTPUT_MODE == 'file':
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    # 'none' mode does nothing - for performance testing

# Initialize log file (clear previous content if using file output)
def initialize_logging():
    if OUTPUT_MODE == 'file':
        # Clear the log file at the start
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write('')
        print(f"Logging to file: {LOG_FILE}")
    elif OUTPUT_MODE == 'console':
        print('Logging to console')
    else:
        print('Logging disabled for performance testing')

class Statistics:
    def __init__(self):
        self.waiting_times = []
        self.total_customers = 0
        self.served_customers = 0

    def record_wait(self, wait_time):
        self.waiting_times.append(wait_time)

    def report(self):
        if not self.waiting_times:
            log_message("No waiting time data.")
            return
        log_message("\nWaiting Time Report:")
        log_message(f"- Average: {statistics.mean(self.waiting_times):.2f} min")
        log_message(f"- Max: {max(self.waiting_times):.2f} min")
        log_message(f"- Min: {min(self.waiting_times):.2f} min")
        log_message(f"- Total waiting times recorded: {len(self.waiting_times)}")
        log_message(f"- Total waiting time: {sum(self.waiting_times):.2f} min")
        log_message("\nCustomer Report:")
        log_message(f"- Total customers: {self.total_customers}")
        log_message(f"- Total served customers: {self.served_customers}")
        log_message(f"- Capacity (customers/hour): {len(self.waiting_times) / (SIM_DURATION / 60):.2f} customers/hour")


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
            log_message(f"\n[{self.env.now:>5}] GATE OPEN")
            yield self.env.timeout(1)
            self.gate_open = False
            log_message(f"[{self.env.now:>5}] GATE CLOSED")
            yield self.env.timeout(59)

    def report(self):
        self.stats.report()

class Customer:
    id_counter = 0

    def __init__(self, env, pool):
        Customer.id_counter += 1
        self.name = f"Swimmer {Customer.id_counter}"
        env.process(self.run(env, pool))

    def run(self, env, pool):
        pool.num_waiting += 1
        wait_start = env.now
        log_message(f"[{env.now:>5}] {self.name} arrives (waiting: {pool.num_waiting}, inside: {pool.num_inside})")

        while not pool.can_enter():
            yield env.timeout(1)

        pool.num_waiting -= 1
        wait_end = env.now
        pool.stats.record_wait(wait_end - wait_start)
        pool.add_swimmer()

        log_message(f"[{env.now:>5}] {self.name} enters the pool (inside: {pool.num_inside})")

        # Determine stay duration
        w = random.random()
        if w <= 0.6:
            swim_time = random.uniform(115, 125)  # ~2h +/- 5min
        else:
            swim_time = random.uniform(75, 120)   # up to 45 min earlier

        yield env.timeout(swim_time)

        pool.remove_swimmer()
        pool.stats.served_customers += 1
        log_message(f"[{env.now:>5}] {self.name} leaves the pool (inside: {pool.num_inside})")

def arrival_process(env, pool):
    while env.now < SIM_DURATION:
        yield env.timeout(random.expovariate(1))  # Mean interarrival: 1 min
        if pool.num_waiting < MAX_QUEUE_LENGTH:
            Customer(env, pool)
            pool.stats.total_customers += 1


def run_single_experiment(experiment_number=0):
    random.seed(RANDOM_SEED + experiment_number)
    Customer.id_counter = 0  
    env = simpy.Environment()
    pool = SwimmingPool(env)

    # Start arrival process
    env.process(arrival_process(env, pool))
    # Start gate cycle process
    env.process(pool.open_gate_cycle())
    
    log_message(f"Running simulation experiment {experiment_number}...")
    env.run(until=SIM_DURATION)
    log_message(f"\nSimulation {experiment_number} finished at {env.now} minutes")
    
    pool.report()
    if hasattr(env, 'reset'):
        env.reset()

def run_all_experiments():
    initialize_logging()

    total_times = []
    for experiment in range(1, NUMBER_SIM_EXPERIMENTS + 1):
        start_time = time.perf_counter()
        run_single_experiment(experiment)
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
        total_times.append(elapsed_time)

    avg_time = sum(total_times) / len(total_times)
    min_time = min(total_times)
    max_time = max(total_times)
    
    print(f"\nSimPy Performance Summary:")
    print(f"- Average time: {avg_time:.2f} ms")
    print(f"- Min time: {min_time:.2f} ms")
    print(f"- Max time: {max_time:.2f} ms")
    print(f"- Total experiments: {NUMBER_SIM_EXPERIMENTS}")
    print(f"- Total time: {(sum(total_times) / 1000):.2f} seconds")

# Start the performance test
run_all_experiments()
