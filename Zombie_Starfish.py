from Graspy_TSP import *
import pandas as pd
from math import floor
import random
from py2opt_github import CustomRouteFinder
import time

tsp_lab_data = pd.read_excel('Lab Data.xlsx', index_col=None)
lab_data_optimal = 211

tsp_data_bays29 = pd.read_excel("Bays29.xlsx", index_col=None)
tsp_data_bays29_optimal = 2020

tsp_data_eil51 = pd.read_excel("EIL51.xlsx", index_col=None)
tsp_data_eil51_optimal = 426

tsp_data_KroA100 = pd.read_excel("KroA100.xlsx", index_col=None)
tsp_data_KroA100_optimal = 21282


class ZombieStarfish:

    def __init__(self,
                 legs_per_starfish,
                 maximum_population,
                 maximum_generations,
                 max_time=10,                      # minutes
                 tsp_data=tsp_data_bays29,
                 test_optimal=tsp_data_bays29_optimal,
                 initial_starfish=None
                 ):

        self.limbs = legs_per_starfish
        self.max_pop = maximum_population
        self.max_gens = maximum_generations
        self.max_time = max_time
        self.dist_matrix = tsp_data
        self.optimal = test_optimal
        # print(self.dist_matrix)
        self.tsp_data = tsp_data

        self.starfish_population = []
        # create a random starfish
        if initial_starfish is None:
            # default to the city list
            self.initial_starfish = list(range(0, len(tsp_data[0])))
            random.shuffle(self.initial_starfish)
        else:
            self.initial_starfish = initial_starfish

        self.starfish_population.append(self.initial_starfish)

        self.ranked_population_dict = dict()  # keys will be tour length, values will be the tour

        self.starfish_limb_len = floor(len(self.dist_matrix[0]) / self.limbs)

        self.unsolved = True

        self.best_solution = None
        self.best_tour = None

        self.event_log = dict()
        self.event_log['generation'] = list()
        self.event_log['time'] = list()
        self.event_log['current_optimal'] = list()
        self.event_log['optimality_gap'] = list()


    def chop_up_starfish(self):

        """This method takes a single starfish and cuts it up into limbs.  It returns a list of the new limbs"""

        limb_list = []

        for starfish in self.starfish_population:
            for limb_number in range(0, self.limbs):
                first_index = 0 + limb_number * self.starfish_limb_len
                second_index = self.starfish_limb_len + limb_number * self.starfish_limb_len
                limb = starfish[first_index:second_index]
                if limb_number == self.limbs - 1:
                    # last limb can be extra long
                    limb = starfish[first_index:]
                limb_list.append(limb)

        self.limb_list = limb_list
        #print("The new limbs are:")
        #print(self.limb_list)
        #print("Starfish is chopped up")

    def first_limb_starfish_construction(self, limb):
        """For the first limb in the list, build the starfish using Graspy NN TSP.
        Then, run 2-OPT on it to find best solution in that space.  This is tantamount to intensification on this
            particular area of the search space.
        This starfish is then saved to ranked population dict, where the key is the score and value is the tour.
        """

        new_starfish, new_starfish_length = self.GRASPY_nearest_neighbor_TSP(limb)

        # non-optimized 2 opt from heuristics lab
        # best_tour, cost = two_opt(new_starfish, self.dist_matrix)

        # PyPi 2-opt optimized code
        city_names = list(range(0, len(self.tsp_data[0])))
        route_finder = CustomRouteFinder(self.dist_matrix, city_names, iterations=1, initial_route=new_starfish)
        cost, best_tour = route_finder.solve()

        # routefinder doesn't add last city to starting city distance so need to correct for that
        last_leg = self.dist_matrix.iloc[best_tour[0], best_tour[-1]]
        # print(last_leg)
        cost = cost + last_leg
        best_tour.append(best_tour[0])

        if cost not in self.ranked_population_dict.keys():
            self.ranked_population_dict.update({float(f'{int(cost)}'): best_tour})
        else:
            # if there is a tie, add a really small number so new result doesn't overwrite the previous result
            self.ranked_population_dict.update({float(f'{cost + 0.01*random.random()}'): best_tour})

    def other_limbs_starfish_construction(self, limb):
        """For all other limbs, build a graspy new starfish.
        This starfish is then saved to ranked population dict, where the key is the score and value is the tour."""

        new_starfish, new_starfish_length = self.GRASPY_nearest_neighbor_TSP(limb)

        if cost not in self.ranked_population_dict.keys():
            self.ranked_population_dict.update({float(f'{new_starfish_length}'): new_starfish})
        else:
            # if there is a tie, add a really small number so new result doesn't overwrite the previous result
            self.ranked_population_dict.update({float(f'{new_starfish_length + 0.1* random.random()}'): new_starfish})

    def report_new_starfish(self):

        # print(self.ranked_population_dict)
        pass

    def cull_the_starfish_heard(self):
        """ This method checks the size of the evaluated population by looking at the number of keys in the
        population dictionary.  Rather than actually deleting data (i.e. culling), we'll sort the performers and
        only allow the algorithm to continue to act on the top performers"""

        if len(self.ranked_population_dict.keys()) > self.max_pop:
            sorted_keys = sorted(self.ranked_population_dict.keys(), reverse=False)
            if len(sorted_keys) < 10:
                #print(sorted_keys)
                pass
            else:
                #print(sorted_keys[0:10])
                pass

            # rebuild the population variable
            self.starfish_population = []
            for rank_of_starfish in range(0, self.max_pop):
                starfish_to_add = self.ranked_population_dict[sorted_keys[rank_of_starfish]]
                self.starfish_population.append(starfish_to_add)

            #print("The population has been culled")

        else:
            sorted_keys = sorted(self.ranked_population_dict.keys(), reverse=False)
            if len(sorted_keys) < 10:
                #print(sorted_keys)
                pass
            else:
                #print(sorted_keys[0:10])
                pass

            # print("Population is still under max threshold")

    def check_stopping_criteria(self):
        """This class has 2 stopping criteria: Max generations, Max Time, and Finding known best solution

        """
        sorted_keys = sorted(self.ranked_population_dict.keys(), reverse=False)
        self.time_now = time.time()
        current_run_time = self.time_now - self.start_time

        # Max Gens
        if self.current_gen == self.max_gens:
            self.unsolved = False
            self.report_solution()
            print('run hit max gens')
            self.time_now = time.time()
            current_run_time = self.time_now - self.start_time
            optimality_gap = self.best_solution - self.optimal

            print(f'current best value found is {sorted_keys[0]}')
            print(f'current best tour found is {self.ranked_population_dict[sorted_keys[0]]}')
            print(f'current best solution found at {current_run_time} seconds into run time')
            print(f'current optimality gap is {optimality_gap}')

        # Time Out
        elif current_run_time >= self.max_time * 60:
            self.unsolved = False
            self.report_solution()
            print('run timed out')

        # Found best tour
        elif sorted_keys[0] == self.optimal:
            self.unsolved = False
            self.report_solution()
            print('found absolute best tour')

        self.report_solution()

    def report_solution(self):


        sorted_keys = sorted(self.ranked_population_dict.keys(), reverse=False)


        if self.best_solution is None:
            self.best_solution = sorted_keys[0]
            self.best_tour = self.ranked_population_dict[sorted_keys[0]]

            self.time_now = time.time()
            current_run_time = self.time_now - self.start_time
            optimality_gap = self.best_solution - self.optimal

            print(f'current best value found is {sorted_keys[0]}')
            print(f'current best tour found is {self.ranked_population_dict[sorted_keys[0]]}')
            print(f'current best solution found at {current_run_time} seconds into run time')
            print(f'current optimality gap is {optimality_gap}')
            print('')
            self.log_events(current_run_time,
                            current_optimal=self.best_solution,
                            current_gap=optimality_gap)


        elif sorted_keys[0] < self.best_solution:
            self.best_solution = sorted_keys[0]
            self.best_tour = self.ranked_population_dict[sorted_keys[0]]

            self.time_now = time.time()
            current_run_time = self.time_now - self.start_time
            optimality_gap = self.best_solution - self.optimal

            print(f'current best value found is {sorted_keys[0]}')
            print(f'current best tour found is {self.ranked_population_dict[sorted_keys[0]]}')
            print(f'current best solution found at {current_run_time} seconds into run time')
            print(f'current optimality gap is {optimality_gap}')
            print('')
            self.log_events(current_run_time,
                            current_optimal=self.best_solution,
                            current_gap=optimality_gap)


    def Unleash_Zombie_Starfish(self):

        self.start_time = time.time()
        self.current_gen = 0
        # to enable testing
        self.unsolved = True

        while self.unsolved:

            self.chop_up_starfish()

            for limb_index in range(0, len(self.limb_list)):

                # build first leg into starfish
                if limb_index % self.limbs == 0:
                    self.first_limb_starfish_construction(self.limb_list[limb_index])

                # build 2-n legs into starfishes
                else:
                    self.other_limbs_starfish_construction(self.limb_list[limb_index])

            self.report_new_starfish()
            self.cull_the_starfish_heard()
            self.check_stopping_criteria()

            # increment the generation
            self.current_gen += 1

    def GRASPY_nearest_neighbor_TSP(self, starfish_limb):
        """

        :param starfish_limb:
        :return:

        """
        all_cities_list = list(range(len(self.dist_matrix[0])))
        tour = starfish_limb
        starting_city = starfish_limb[0]

        new_starfish = list()
        new_starfish.append(starfish_limb[0])
        new_starfish_length = 0

        for n in range(1, len(tour)):
            current_city = tour[n - 1]
            next_city = tour[n]
            distance = self.dist_matrix.iloc[current_city, next_city]
            new_starfish_length += distance
            new_starfish.append(next_city)

        city_last_added = next_city

        while len(new_starfish) != len(all_cities_list):
            # look for valid moves given what is in the tour
            valid_cities = valid(new_starfish, all_cities_list)

            # Look for nearest 3 neighbors out of valid cities
            best_city, next_best, third_best = next_city_to_add_GRASPY(valid_cities,
                                                                       city_last_added, self.dist_matrix)

            # Use Randomness to pick out of our top 3
            next_city = pick_a_city(best_city, next_best, third_best)

            # add the next city
            new_starfish.append(next_city)
            distance = self.dist_matrix.iloc[city_last_added, next_city]
            city_last_added = next_city
            new_starfish_length += distance

        # add the final leg
        last_distance = self.dist_matrix.iloc[starting_city, city_last_added]
        tour.append(tour[0])
        new_starfish_length += last_distance

        return new_starfish, new_starfish_length

    def log_events(self, current_run_time, current_optimal, current_gap):

        self.event_log['generation'].append(self.current_gen)
        self.event_log['time'].append(current_run_time)
        self.event_log['current_optimal'].append(current_optimal)
        self.event_log['optimality_gap'].append(current_gap)

