import random


def GRASP_TSP(number_iterations, tsp_data):
    best_tour = 0
    best_cost = 10 ** 10  # arbitrarily large

    # Generate unique starting solutions
    for n in range(number_iterations):

        # Find a starting solution
        tour, tour_length = GRASPY_nearest_neighbor_TSP(tsp_data)

        # Perform Local Search on that solution
        tour, tour_cost = two_opt(tour, tsp_data)

        # Update best solution and best cost as applicable
        if tour_cost < best_cost:
            best_tour = tour
            best_cost = tour_cost

            print(best_tour)
            print(best_cost)

        if n % 10 == 0:
            print(f'your currently on iteration {n}')

    return best_tour, best_cost


def GRASPY_nearest_neighbor_TSP(tsp_data):
    tour = []

    tour_length = 0
    starting_city = get_starting_city(list(range(len(tsp_data))))
    tour.append(starting_city)

    city_last_added = starting_city
    all_cities_list = list(range(len(tsp_data)))

    while len(tour) != len(all_cities_list):
        # look for valid moves given what is in the tour
        valid_cities = valid(tour, all_cities_list)

        # Look for nearest 3 neighbors out of valid cities
        best_city, next_best, third_best = next_city_to_add_GRASPY(valid_cities, city_last_added, tsp_data)

        # Use Randomness to pick out of our top 3
        next_city = pick_a_city(best_city, next_best, third_best)

        # add the next city
        tour.append(next_city)
        distance = tsp_data.iloc[city_last_added, next_city]
        city_last_added = next_city
        tour_length += distance

    # add the final leg
    last_distance = tsp_data.iloc[starting_city, city_last_added]
    tour.append(tour[0])
    tour_length += last_distance

    return tour, tour_length


def get_starting_city(list_of_cities):
    starting_city = random.choice(list_of_cities)
    # print(starting_city)

    return starting_city


def two_opt(tour, tsp_data):
    best_tour = tour[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(tour) - 3):  # i is index of first city
            for j in range(i + 2, len(tour)):  # j is index of second city
                new_tour = tour[:]  # clone tour
                new_tour[i:j] = tour[j - 1:i - 1:-1]  # swap the order of the tour between these two cities
                if cost(new_tour, tsp_data) < cost(best_tour, tsp_data):
                    best_tour = new_tour[:]
                    improved = True
        tour = best_tour[:]
        # print("I found a new tour:",best_tour, cost(best_tour))
    return best_tour, cost(best_tour, tsp_data)


def cost(tour, tsp_data):
    cost = 0
    for i in range(0, len(tour)-1):  # Python is 0 index and goes up to *but not including* last element in range
        cost += tsp_data.iat[tour[i], tour[i + 1]]
    return cost


def valid(Tour, all_cities):
    """Inputs the current tour and cities not in tour

    Returns cities not currently in the tour"""
    all_cities_copy = all_cities.copy()

    if Tour != []:
        for city in Tour:
            all_cities_copy.remove(city)

    return all_cities_copy


def next_city_to_add_GRASPY(valid_cities, last_city_added, tsp_data):
    closest_distance = 10000  # arbitrarily large
    best_city = -1  # neg so it's easy to tell if func did not work

    # These two variables are additions
    next_best = -1
    third_best = -1

    for valid_city in valid_cities:
        distance = tsp_data.iloc[valid_city, last_city_added]

        if distance < closest_distance:
            closest_distance = distance
            third_best = next_best
            next_best = best_city
            best_city = valid_city

            # print(f'best city is {best_city}')
    # print(f'next best city is {next_best}')
    # print(f'third best city is {third_best}')

    return best_city, next_best, third_best


def pick_a_city(best_city, next_best, third_best):
    random_num = random.random()

    # Edge cases: When third_Best or next_best is -1
    if third_best == -1:
        third_best = next_best

    if next_best == -1:
        next_best = best_city
        third_best = best_city

    if random_num <= (1 / 6):
        city_to_add = third_best

    elif (1 / 2) > random_num > (1 / 6):
        city_to_add = next_best

    else:
        city_to_add = best_city

    # print(city_to_add)

    return city_to_add
