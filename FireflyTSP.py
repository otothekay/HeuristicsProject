import pandas as pd
import numpy as np
import random
import time
from Graspy_TSP import cost

tsp_lab_data = pd.read_excel('Lab Data.xlsx', index_col=None)
lab_data_optimal = 211

tsp_data_bays29 = pd.read_excel("Bays29.xlsx", index_col=None)
tsp_data_bays29_optimal = 2020

tsp_data_eil51 = pd.read_excel("EIL51.xlsx", index_col=None)
tsp_data_eil51_optimal = 426

tsp_data_KroA100 = pd.read_excel("KroA100.xlsx", index_col=None)
tsp_data_KroA100_optimal = 21282


class FireflyTSP:

    def __init__(self,
                 population_size,
                 maximum_generations=1,
                 max_time=10,  # minutes
                 tsp_data=tsp_data_bays29,
                 test_optimal=tsp_data_bays29_optimal,
                 ):

        # experiment parameters
        self.pop_size = population_size
        self.max_gens = maximum_generations
        self.max_time = max_time
        self.dist_matrix = tsp_data
        self.optimal = test_optimal

        # initial population
        self.generate_initial_pop()

        # state variables
        self.unsolved = True
        self.best_solution = None
        self.best_tour = None

        # variables for logging events
        self.event_log = dict()
        self.event_log['generation'] = list()
        self.event_log['time'] = list()
        self.event_log['current_optimal'] = list()
        self.event_log['optimality_gap'] = list()

    def generate_initial_pop(self):
        population = []
        values = []
        costs = []
        for i in range(0, self.pop_size):
            new_tour = random.sample(range(0, len(self.dist_matrix[0])), len(self.dist_matrix[0]))
            new_tour.append(new_tour[0])
            population.append(new_tour)

            true_cost = cost(new_tour, self.dist_matrix)
            costs.append(true_cost)

            intensity = 1 / true_cost
            values.append(intensity)

        self.population = population
        self.values = values
        self.costs = costs

    def distance_calculator(self, i, j):

        n = len(i)
        A = 0  # edge distance
        scalar = 10  # scalar multiple

        for (allele_i, allele_j) in zip(i, j):
            if allele_i != allele_j:
                A += 1
        distance = A / n * scalar

        return distance, A

    def inverse_mutation(self, i, j):


        distance, A = self.distance_calculator(i, j)

        # print(A)
        #### Alex, you're code was bugging out when A was 2 or less so randint below didn't have a valid range

        if A <= 2:
            A = 2

        ####
        x = random.randint(2, A)
        start = random.randint(0, len(i))

        # determining the starting allele and ending allele
        if start + x > len(i):
            end = start + x - len(i)
        else:
            end = start + x

        if end < start:
            section_ndx = [end, start]
            if start == 16 or start == 15:
                section_ndx = [end, 14]
        else:
            section_ndx = [start, end]
            if end == 16 or end == 15:
                section_ndx = [start, 14]

        if end == start:
            return i

        section = i[section_ndx[0]:section_ndx[1] + 1]
        section.reverse()

        if section_ndx[0] == 0:
            new_i = section + i[section_ndx[1] + 1:]

        elif section_ndx[1] == 16:
            new_i = i[:section_ndx[0]] + section + i[0]
        else:
            new_i = i[:section_ndx[0]] + section + i[section_ndx[1] + 1:]

        return new_i

    def firefly_fixer(self, firefly):

        """Fireflies would return to the starting city, and one of the city would repeat itself in the list"""

        # check for duplicate cities
        for city in range(0, len(firefly)):
            city_counter = 0
            for index in range(0, len(firefly)):

                if city == firefly[index]:
                    city_counter += 1

                if city_counter == 2:
                    # delete second instance of city
                    del firefly[index]
                    return firefly

        if firefly[0] != firefly[-1]:
            firefly.append(firefly[0])

        return firefly

    def check_valid_firefly(self, firefly):

        valid = True

        if firefly[0] != firefly[-1]:
            valid = False

        return valid

    def create_new_pop(self):
        for i in range(0, self.pop_size - 1):
            for j in range(0, self.pop_size - 1):

                firefly_i = self.population[i]

                if i != j:
                    firefly_j = self.population[j]
                    if self.values[j] > self.values[i]:
                        mutation = self.inverse_mutation(firefly_i, firefly_j)
                        #### Alex, I added the firefly fixer to this bit of the code below inside the append function
                        valid = self.check_valid_firefly(mutation)
                        while valid == False:
                            # print(mutation)
                            mutation = self.firefly_fixer(mutation)
                            valid = self.check_valid_firefly(mutation)
                        self.population.append(mutation)
                        ####
        new_values = []
        for i in self.population:
            value = cost(i, self.dist_matrix)
            new_values.append(value)
            sort = np.argsort(new_values)

        new_pop = []

        for i in sort:
            new_pop.append(self.population[i])
            if len(new_pop) == self.pop_size:
                break

        return new_pop

    def firefly_heuristic(self):

        for i in range(0, self.pop_size):
            self.population = self.create_new_pop()

        total_cost = 0
        for i in self.population:
            cost1 = cost(i, self.dist_matrix)

            # check if best solution
            if cost1 < self.best_solution:
                self.best_solution = cost1
                self.best_tour = i

                #log the event
                current_run_time = time.time() - self.start_time
                current_gap = self.best_solution - self.optimal
                self.log_events(current_run_time, self.best_solution, current_gap)

            # append to total cost for averaging later?
            total_cost += cost1

        avg_cost = total_cost / self.pop_size

        return self.population, avg_cost

    def Unleash_Firefly(self):

        self.unsolved = True
        self.gen = 0
        self.start_time = time.time()

        avg_cost_list = []

        while self.unsolved:

            if self.gen == 0:

                self.generate_initial_pop()
                self.best_value = 10 ** 10  # intensity
                self.best_tour = []

                #evaluate initial population
                for index, (firefly, value) in enumerate(zip(self.population, self.values)):
                    if value < self.best_value:
                        #update best solution / tour
                        self.best_tour = self.population[index]
                        self.best_solution = cost(self.population[index], self.dist_matrix)

                # log events for gen 0
                current_run_time = time.time() - self.start_time
                current_gap = self.best_solution - self.optimal
                self.log_events(current_run_time, self.best_solution, current_gap)

                #incriment past gen 0
                self.gen += 1

            self.population, avg_cost = self.firefly_heuristic()
            print(f'the avg cost of tours in this generation is {avg_cost}')
            avg_cost_list.append(avg_cost)

            # check stopping criteria: Max time, Max Gens, Known Best solution found, stuck in local optima
            current_run_time = time.time() - self.start_time
            current_gap = self.best_solution - self.optimal

            if self.gen == self.max_gens:
                self.unsolved = False
                print("Hit max gens")
                self.log_events(current_run_time, self.best_solution, current_gap)
                print(self.best_tour)

            if current_run_time >= self.max_time * 60:
                self.unsolved = False
                print("Hit max run time")
                self.log_events(current_run_time, self.best_solution, current_gap)
                print(self.best_tour)

            if current_gap == 0:
                self.unsolved = False
                print("Best solution found")
                self.log_events(current_run_time, self.best_solution, current_gap)
                print(self.best_tour)

            # check for stuck in local optima after few generations
            if self.gen > 6:
                if avg_cost_list[self.gen - 1] == avg_cost_list[self.gen - 5]:
                    self.unsolved = False
                    print('stuck in local optima')
                    self.log_events(current_run_time, self.best_solution, current_gap)
                    print(self.best_tour)

            #increment the generation
            self.gen += 1

    def log_events(self, current_run_time, current_optimal, current_gap):

        self.event_log['generation'].append(self.gen)
        self.event_log['time'].append(current_run_time)
        self.event_log['current_optimal'].append(current_optimal)
        self.event_log['optimality_gap'].append(current_gap)



