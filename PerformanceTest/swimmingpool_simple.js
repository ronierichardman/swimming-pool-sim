/*
 * Swimming Pool Simulation (JavaScript) - WITHOUT LOGGING
 * ====================================================
 * This script simulates a swimming pool environment using the SimLuxJS framework.
 * It models customer arrivals, swimming durations, and pool capacity constraints.
 * It is designed for performance testing without logging overhead, 
 * Although we can disable logging if needed (as with another script "swimmingpool.js"), 
 * the toggle logic still takes some time to execute.
 *
 * USAGE:
 * node swimmingpool_simple.js --sim-duration 2400 --pool-capacity 50 --num-experiments 20
 * OPTIONS:
 * --sim-duration: Total simulation duration in minutes (default: 2400, which is 5 shifts of 8 hours)
 * --pool-capacity: Maximum number of swimmers allowed in the pool at a time (default: 50)
 * --num-experiments: Number of simulation experiments to run (default: 20)
 */

const SimLuxJS = require('../SimLuxJS/SimLuxJS.js').SimLuxJS; 
const SimEntity = require('../SimLuxJS/SimLuxJS.js').SimEntity;  
const seedrandom = require('seedrandom');
const args = require('minimist')(process.argv.slice(2));

const RANDOM_SEED = 42;
const SIM_DURATION = args['sim-duration'] || 5 * 8 * 60; 
const POOL_CAPACITY = args['pool-capacity'] || 100;
const NUMBER_SIM_EXPERIMENTS = args['num-experiments'] || 20;
const MAX_QUEUE_LENGTH = 30;

let random;
const uniform = (min, max) => random() * (max - min) + min;
const exponential = (lambda) => -Math.log(1 - random()) / lambda;

class Statistics {
    constructor() {
        this.waitingTimes = [];
        this.totalCustomers = 0;
        this.servedCustomers = 0;
    }

    recordWait(waitTime) {
        this.waitingTimes.push(waitTime);
    }
}

class SwimmingPool {
    constructor(sim) {
        this.sim = sim;
        this.gateOpen = true;
        this.numInside = 0;
        this.numWaiting = 0;
        this.capacity = POOL_CAPACITY;
        this.stats = new Statistics();
    }

    canEnter() {
        return this.gateOpen && this.numInside < this.capacity;
    }

    addSwimmer() {
        this.numInside++;
    }

    removeSwimmer() {
        this.numInside--;
    }

    async openGateCycle() {
        while (this.sim.getTime() < SIM_DURATION) {
            this.gateOpen = true;
            await this.sim.advance(1);
            this.gateOpen = false;
            await this.sim.advance(59);
        }
    }
}

class Customer {
    static idCounter = 0;

    constructor(sim, pool) {
        Customer.idCounter++;
        this.name = `Swimmer ${Customer.idCounter}`;
        sim.addSimEntity(new SimEntity(simEntity => this.run(sim, pool)));
    }

    async run(sim, pool) {
        pool.numWaiting++;
        const waitStart = sim.getTime();

        while (!pool.canEnter()) {
            await sim.advance(1);
        }

        pool.numWaiting--;
        const waitEnd = sim.getTime();
        pool.stats.recordWait(waitEnd - waitStart);
        pool.addSwimmer();

        // Determine stay duration
        const w = random();
        let swimTime;
        if (w <= 0.6) {
            swimTime = uniform(115, 125); // ~2h +/- 5min
        } else {
            swimTime = uniform(75, 120);  // up to 45 min earlier
        }

        await sim.advance(swimTime);
        pool.removeSwimmer();
        pool.stats.servedCustomers++;
    }
}

async function arrivalProcess(sim, pool) {
    while (sim.getTime() < SIM_DURATION) {
        await sim.advance(exponential(1)); // Mean interarrival: 1 min
        if (pool.numWaiting < MAX_QUEUE_LENGTH) {
            new Customer(sim, pool);
            pool.stats.totalCustomers++;
        }
    }   
}

async function runSingleExperiment(experimentNumber = 0) {
    // Set up random number generator with different seed for each experiment
    random = seedrandom(RANDOM_SEED + experimentNumber);
    
    Customer.idCounter = 0;
    let simLuxJS = new SimLuxJS();
    simLuxJS.enableLogging = false; // Disable logging for performance
    const pool = new SwimmingPool(simLuxJS);

    // Start arrival process
    simLuxJS.addSimEntity(new SimEntity(simEntity => arrivalProcess(simLuxJS, pool)));

    // Start gate cycle process
    simLuxJS.addSimEntity(new SimEntity(simEntity => pool.openGateCycle()));

    await simLuxJS.run(until=SIM_DURATION);
    return pool.stats;
}

async function runAllExperiments() {
    const totalTimes = [];
    let totalCustomers = [];
    let totalServedCustomers = [];
    let avgWaitTimes = [];

    for (let experiment = 1; experiment <= NUMBER_SIM_EXPERIMENTS; experiment++) {
        const startTime = performance.now();
        const stats = await runSingleExperiment(experiment);
        const endTime = performance.now();

        const elapsedTime = (endTime - startTime); 
        totalTimes.push(elapsedTime);
        totalCustomers.push(stats.totalCustomers);
        totalServedCustomers.push(stats.servedCustomers);
        avgWaitTimes.push(stats.waitingTimes.reduce((a, b) => a + b, 0) / stats.waitingTimes.length || 0);
    }

    const avgTime = totalTimes.reduce((a, b) => a + b, 0) / totalTimes.length;
    const minTime = Math.min(...totalTimes);
    const maxTime = Math.max(...totalTimes);
    const totalTime = totalTimes.reduce((a, b) => a + b, 0);
    const avgWaitTime = avgWaitTimes.reduce((a, b) => a + b, 0) / avgWaitTimes.length;
    const avgCustomers = totalCustomers.reduce((a, b) => a + b, 0) / totalCustomers.length || 0;
    const avgServedCustomers = totalServedCustomers.reduce((a, b) => a + b, 0) / totalServedCustomers.length || 0;
    const summary = {
        framework: 'SimLuxJS',
        pool_capacity: POOL_CAPACITY,
        sim_duration: SIM_DURATION,
        num_experiments: NUMBER_SIM_EXPERIMENTS,
        average_time: parseFloat(avgTime.toFixed(2)), // in milliseconds
        min_time: parseFloat(minTime.toFixed(2)), // in milliseconds
        max_time: parseFloat(maxTime.toFixed(2)), // in milliseconds
        total_time: parseFloat(totalTime.toFixed(2)), // in milliseconds
        avg_customers: avgCustomers, // customers
        avg_served_customers: avgServedCustomers, // customers
        average_waiting_time: parseFloat(avgWaitTime.toFixed(2)) // in minutes
    };

    console.log(`Summary:${JSON.stringify(summary)}`);
}

async function main() {
    console.log("Starting SimLuxJS Swimming Pool Simulation...");
    await runAllExperiments();
}

main().catch(console.error);