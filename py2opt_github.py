#### This code is copy/pasted from github.  Normally invoked by typing
# "from py2opt.routefinder import RouteFinder"

# I'm customizing this to be able to receive an initial route

import random2
import time

from py2opt.solver import Solver


class CustomRouteFinder:
    def __init__(self, distance_matrix, cities_names, iterations=5, writer_flag=False, initial_route=None, method='py2opt'):
        self.distance_matrix = distance_matrix
        self.iterations = iterations
        self.writer_flag = writer_flag
        self.cities_names = cities_names

        # add an initial route to init
        self.initial_route = initial_route


    def solve(self):
        start_time = round(time.time() * 1000)
        elapsed_time = 0
        iteration = 0
        best_distance = 0
        best_route = []
        best_distances = []

        while iteration < self.iterations:
            num_cities = len(self.distance_matrix)
            #print(round(elapsed_time), 'msec')
            if self.initial_route == None:
                self.initial_route = [0] + random2.sample(range(1, num_cities), num_cities - 1)
            tsp = Solver(self.distance_matrix, self.initial_route)
            new_route, new_distance, distances = tsp.two_opt()

            if iteration == 0:
                best_distance = new_distance
                best_route = new_route
            else:
                pass

            if new_distance < best_distance:
                best_distance = new_distance
                best_route = new_route
                best_distances = distances

            elapsed_time = round(time.time() * 1000) - start_time
            iteration += 1

        if self.writer_flag:
            self.writer(best_route, best_distance, self.cities_names)

        if self.cities_names:
            best_route = [self.cities_names[i] for i in best_route]
            return best_distance, best_route
        else:
            return best_distance, best_route

    @staticmethod
    def writer(best_route, best_distance, cities_names):
        f = open("../results.txt", "w+")
        for i in best_route:
            f.write(cities_names[i])
            f.write("\n")
            print(cities_names[i])
        f.write(str(best_distance))
        f.close()