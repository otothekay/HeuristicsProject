import pandas as pd
import numpy as np
import random
import time
from Graspy_TSP import cost

tsp_data_bays29 = pd.read_excel("Bays29.xlsx", index_col=None)
tsp_data_bays29_optimal = 2020

class FireflyTSP():

    def __init__(self,
                 population_size,
                 gamma,
                 maximum_generations=1,
                 max_time=10,  # minutes
                 tsp_data=tsp_data_bays29,
                 test_optimal=tsp_data_bays29_optimal,
                 ):

        # experiment parameters
        self.pop_size = population_size
        self.gamma = gamma
        self.max_gens = maximum_generations
        self.max_time = max_time
        self.dist_matrix = tsp_data
        self.optimal = test_optimal

        #initial population
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
        for i in range(0, self.pop_size):
            new_tour = random.sample(range(0, len(self.dist_matrix[0])), len(self.dist_matrix[0]))
            new_tour.append(new_tour[0])
            population.append(new_tour)

            I = 1 / cost(new_tour, self.dist_matrix)
            values.append(I)

        self.population = population
        self.values = values

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

        new_i = []
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

        best_cost = 10 ** 10  # arbitrarily large
        best_solution = []

        for i in range(0, self.pop_size):
            self.population = self.create_new_pop()

        total_cost = 0
        for i in self.population:
            cost1 = cost(i, self.dist_matrix)

            # check if best solution
            if cost1 < best_cost:
                best_cost = cost1
                best_solution = i

            # append to total cost for averaging later?
            total_cost += cost1

        avg_cost = total_cost / self.pop_size

        return self.population, avg_cost, best_cost, best_solution
