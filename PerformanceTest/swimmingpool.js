/*
 * Swimming Pool Simulation (JavaScript) - WITH LOGGING
 * ====================================================
 * This script simulates a swimming pool environment using the SimLuxJS framework.
 * It models customer arrivals, swimming durations, and pool capacity constraints.
 * With configurable logging modes, it allows for testing and debugging.
 *
 * LOGGING MODES:
 * - 'console': Real-time output to terminal
 * - 'file': Write all messages to LOG_FILE
 * - 'none': No output (for performance testing)
 *
 * USAGE:
 * 1. Change OUTPUT_MODE constant below to desired mode
 * 2. Run: node swimmingpool.js
 * 3. Check results in console or LOG_FILE
 */

const SimLuxJS = require('../SimLuxJS/SimLuxJS.js').SimLuxJS; 
const SimEntity = require('../SimLuxJS/SimLuxJS.js').SimEntity;  
const seedrandom = require('seedrandom');
const fs = require('fs');

const OUTPUT_MODE = 'file'; // 'console', 'file', or 'none'
const LOG_FILE = 'simulation_js_output.log';

const RANDOM_SEED = 42;
const SIM_DURATION = 5 * 8 * 60;
const POOL_CAPACITY = 50;
const MAX_QUEUE_LENGTH = 30;
const NUMBER_SIM_EXPERIMENTS = 20;

// Logging function that respects OUTPUT_MODE
function logMessage(message) {
    switch(OUTPUT_MODE) {
        case 'console':
            console.log(message);
            break;
        case 'file':
            fs.appendFileSync(LOG_FILE, message + '\n');
            break;
        case 'none':
            // No output - for performance testing
            break;
    }
}

// Initialize log file (clear previous content if using file output)
function initializeLogging() {
    if (OUTPUT_MODE === 'file') {
        // Clear the log file at the start
        fs.writeFileSync(LOG_FILE, '');
        console.log(`Logging to file: ${LOG_FILE}`);
    } else if (OUTPUT_MODE === 'console') {
        console.log('Logging to console');
    } else {
        console.log('Logging disabled for performance testing');
    }
}

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

    report() {
        if (this.waitingTimes.length === 0) {
            logMessage("No waiting time data.");
            return;
        }
        const avg = this.waitingTimes.reduce((a, b) => a + b, 0) / this.waitingTimes.length;
        logMessage("\nWaiting Time Report:");
        logMessage(`- Average: ${avg.toFixed(2)} min`);
        logMessage(`- Max: ${Math.max(...this.waitingTimes).toFixed(2)} min`);
        logMessage(`- Min: ${Math.min(...this.waitingTimes).toFixed(2)} min`);
        logMessage(`- Total customers: ${this.totalCustomers}`);
        logMessage(`- Total served: ${this.servedCustomers}`);
        logMessage(`- Total waiting times recorded: ${this.waitingTimes.length}`);
        logMessage(`- Total waiting time: ${this.waitingTimes.reduce((a, b) => a + b, 0).toFixed(2)} min`);
        logMessage(`- Average waiting time per customer: ${(this.waitingTimes.reduce((a, b) => a + b, 0) / this.waitingTimes.length).toFixed(2)} min`);
        logMessage(`- Capacity: ${(this.waitingTimes.length / (SIM_DURATION / 60)).toFixed(2)} persons/hour`);
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
            logMessage(`\n[${this.sim.getTime().toString().padStart(5)}] GATE OPEN`);
            await this.sim.advance(1);
            this.gateOpen = false;
            logMessage(`[${this.sim.getTime().toString().padStart(5)}] GATE CLOSED`);
            await this.sim.advance(59);
        }
    }

    report() {
        this.stats.report();
    }
}

class Customer {
    static idCounter = 0;

    constructor(sim, pool) {
        Customer.idCounter++;
        this.name = `Swimmer ${Customer.idCounter}`;
        this.pool = pool;
        this.sim = sim;
        this.sim.addSimEntity(new SimEntity(simEntity => this.run()));
    }

    async run() {
        this.pool.numWaiting++;
        const waitStart = this.sim.getTime();
        logMessage(`[${this.sim.getTime().toString().padStart(5)}] ${this.name} arrives (waiting: ${this.pool.numWaiting}, inside: ${this.pool.numInside})`);

        while (!this.pool.canEnter()) {
            await this.sim.advance(1);
        }

        this.pool.numWaiting--;
        const waitEnd = this.sim.getTime();
        this.pool.stats.recordWait(waitEnd - waitStart);
        this.pool.addSwimmer();

        logMessage(`[${this.sim.getTime().toString().padStart(5)}] ${this.name} enters the pool (inside: ${this.pool.numInside})`);

        // Determine stay duration
        const w = random();
        let swimTime;
        if (w <= 0.6) {
            swimTime = uniform(115, 125); // ~2h +/- 5min
        } else {
            swimTime = uniform(75, 120);  // up to 45 min earlier
        }

        await this.sim.advance(swimTime);

        this.pool.removeSwimmer();
        this.pool.stats.servedCustomers++;
        logMessage(`[${this.sim.getTime().toString().padStart(5)}] ${this.name} leaves the pool (inside: ${this.pool.numInside})`);
    }
}

class ArrivalProcess {
    constructor(sim, pool) {
        this.pool = pool;
        this.sim = sim;
        this.sim.addSimEntity(new SimEntity(simEntity => this.run()));
    }

    async run() {
        while (this.sim.getTime() < SIM_DURATION) {
            await this.sim.advance(exponential(1)); // Mean interarrival: 1 min
            if (this.pool.numWaiting < MAX_QUEUE_LENGTH) {
                new Customer(this.sim, this.pool);
                this.pool.stats.totalCustomers++;
            }
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
    new ArrivalProcess(simLuxJS, pool);

    // Start gate cycle process
    simLuxJS.addSimEntity(new SimEntity(simEntity => pool.openGateCycle()));

    logMessage(`\nRunning simulation experiment ${experimentNumber}...`);
    await simLuxJS.run(until=SIM_DURATION);
    logMessage(`\nSimulation ${experimentNumber} finished at ${simLuxJS.getTime()} minutes`);

    pool.report();

    return pool.stats;
}   

async function runAllExperiments() {
    initializeLogging();
    
    const totalTimes = [];
    for (let experiment = 1; experiment <= NUMBER_SIM_EXPERIMENTS; experiment++) {        
        const startTime = performance.now();
        await runSingleExperiment(experiment);
        const endTime = performance.now();

        const elapsedTime = endTime - startTime;
        totalTimes.push(elapsedTime);
    }
    
    const totalTime = totalTimes.reduce((a, b) => a + b, 0);
    const avgTime = totalTime / totalTimes.length;
    const minTime = Math.min(...totalTimes);
    const maxTime = Math.max(...totalTimes);
    
    console.log("\nSimLuxJS Performance Summary:");
    console.log(`- Average time: ${avgTime.toFixed(2)} ms`);
    console.log(`- Min time: ${minTime.toFixed(2)} ms`);
    console.log(`- Max time: ${maxTime.toFixed(2)} ms`);
    console.log(`- Total experiments: ${NUMBER_SIM_EXPERIMENTS}`);
    console.log(`- Total time: ${(totalTime / 1000).toFixed(2)} seconds`);
}

// Start the performance test
runAllExperiments().catch(console.error);