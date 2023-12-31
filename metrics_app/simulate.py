import simpy
import random

import math

import statistics

from typing import List

DAY_DURATION = 24 * 60 * 60
SIM_DAYS = 10

NUM_GITHUB_RUNNERS = 1

simulated_lttc = []
test_pass_results = []
simulated_none = []
simulated_low = []
simulated_medium = []
simulated_high = []
simulated_crictical = []


class Distribution:
    def __init__(self, values: List[int], step_size: int):
        """
        Generates a discrete distribution approximation from a set of input samples,
        and a discrete step size.
        """
        self.step_size = step_size
        max_index = 0
        dist = {0: 0}
        # Count occurences within step_size blocks
        for v in values:
            idx = int(v / self.step_size)
            max_index = max(idx, max_index)
            dist[idx] = dist.get(idx) + 1 if dist.get(idx) else 1
        
        self.dist = [
            dist[i] if dist.get(i) else 0 
            for i in range(0, max_index + 1)
        ]

        # Transform to cumulative sum
        self.dist = [
            sum(self.dist[0:i+1])
            for i in range(len(self.dist))
        ]
        print (self.dist)

        self.max_roll = self.dist[-1]

    
    def sample(self) -> int:
        """
        Samples the distribution
        """
        roll = random.randint(0, self.max_roll)
        for i in range(len(self.dist)):
            no_chance = self.dist[i] == 0 or self.dist[i] == self.dist[i - 1]
            if roll > self.dist[i] or no_chance:
                continue
            return i * self.step_size
        
class SimulationConfiguration:
    def __init__(self, 
        sast_configuration: str,
        num_runners: int,
        pipeline_delay: Distribution,
        sast_runtime: Distribution,
        test_dist: Distribution,
        none_dist: Distribution,
        low_dist: Distribution,
        medium_dist: Distribution,
        high_dist: Distribution,
        critical_dist: Distribution,
        commits_per_day: int
    ):
        """
        Defines the configuration of the pipeline simulation.
        sast_configuration:             a string ('seq' or 'par') which defines whether the SAST tool runs at the same time as build and test, or before
        num_runners:                    the amount of GitHub VMs available to run builds in parralel
        pipeline_delay, sast_runtime:   distributions of our sampled metric data
        commits_per_day:                user input determining how many commits they expect to have per day
        """
        self.sast_configuration = sast_configuration
        self.num_runners = num_runners
        self.pipeline_delay = pipeline_delay
        self.sast_runtime = sast_runtime
        self.test_dist = test_dist
        self.none_dist = none_dist
        self.low_dist = low_dist
        self.medium_dist = medium_dist
        self.high_dist = high_dist
        self.critical_dist = critical_dist
        self.commits_per_day = commits_per_day


class SimulationState:
    def __init__(self):
        self.simulated_lttc = []
        self.successful_deployments = 0


class Pipeline:
    def __init__(self, env: simpy.Environment, conf: SimulationConfiguration):
        """
        Initialises a Pipeline simulation.
        """
        self.env = env
        self.conf = conf

        self.runner = simpy.Resource(env, conf.num_runners)
        self.cloud_deployer = simpy.Resource(env, 1)

    def deploy(self, commit: int):
        if self.conf.sast_configuration == 'par':
            yield self.env.process(self.par_deploy(commit))
        else:
            yield self.env.process(self.seq_deploy(commit))

    def seq_deploy(self, commit: int):
        # We require a GitHub runner to execute our request
        with self.runner.request() as runr:
            yield runr
            # Simulate SAST runtime
            yield self.env.timeout(self.conf.sast_runtime.sample())

            # Deploy
            with self.cloud_deployer.request() as depl:
                yield depl
                yield self.env.timeout(self.conf.pipeline_delay.sample())
        self.did_tests_pass()
        self.calculate_cvss()
    
    def par_deploy(self, commit: int):
        def run_sast():
            with self.runner.request() as runr:
                yield self.env.timeout(self.conf.sast_runtime.sample())
        
        def run_deploy():
            # Need deployer (to be only one deploying to Vercel) and GitHub runner to deploy
            with self.runner.request() as runr:
                with self.cloud_deployer.request() as depl:
                    yield self.env.all_of([runr, depl])

                    yield self.env.timeout(self.conf.pipeline_delay.sample())
        
        yield self.env.all_of([
            self.env.process(run_sast()),
            self.env.process(run_deploy())
        ])

        self.did_tests_pass()
        self.calculate_cvss()

    def did_tests_pass(self):
        """Simulate if the test passed based on the test pass rate distribution."""
        test_pass_results.append(random.randint(1, 100) <= self.conf.test_dist.sample())
    
    def calculate_cvss(self):
        """Simulate the CVSS score of the commit based on the CVSS distribution."""

        simulated_none.append(self.conf.none_dist.sample())
        simulated_low.append(self.conf.low_dist.sample())
        simulated_medium.append(self.conf.medium_dist.sample())
        simulated_high.append(self.conf.high_dist.sample())
        simulated_crictical.append(self.conf.critical_dist.sample())

        





def commit_to_pipeline(env: simpy.Environment, commit: int, pipeline: Pipeline):
    """
    Simulates a single commit to a pipeline
    """

    global simulated_lttc, test_pass_results
    # Sample our simulated LTTC
    start_time = env.now

    yield env.process(pipeline.deploy(commit))

    simulated_lttc.append(env.now - start_time)


def __run_sim(env: simpy.Environment, conf: SimulationConfiguration):
    global simulated_lttc
    simulated_lttc = []
    commit = 0

    pipeline = Pipeline(env, conf)

    average_wait = DAY_DURATION / conf.commits_per_day
    while True:
        # Commit at a slightly random frequency around our deployments per day
        yield env.timeout(random.uniform(average_wait * 0.8, average_wait * 1.2))

        commit += 1
        env.process(commit_to_pipeline(env, commit, pipeline))
    

def simulatedCvssResults():
    #print("none", simulated_none, "low", simulated_low, "medium", simulated_medium, "high", simulated_high, "critical", simulated_crictical)
    return 0, math.floor(sum(simulated_low) / len(simulated_low)), math.floor(sum(simulated_medium) / len(simulated_medium)), math.floor(sum(simulated_high) / len(simulated_high)), math.floor(sum(simulated_crictical) / len(simulated_crictical))

def simulate(conf: SimulationConfiguration):
    global simulated_lttc, test_pass_results

    env = simpy.Environment()
    env.process(__run_sim(env, conf))
    env.run(until=DAY_DURATION * SIM_DAYS)

    test_pass_rate = (sum(test_pass_results) / len(test_pass_results)) * 100
    none, low, medium, high, crtical = simulatedCvssResults()
    return statistics.mean(simulated_lttc), math.ceil(len(simulated_lttc) / SIM_DAYS), test_pass_rate, none, low, medium, high, crtical



if __name__ == "__main__":
    dist = Distribution([6,6,7,7,7,7,7,8,8,9], 1)
    
    conf = SimulationConfiguration(
        'seq',
        2,
        dist,
        dist,
        100
    )

    print(simulate(conf))
    

