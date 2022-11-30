import pandas as pd

from Zombie_Starfish import ZombieStarfish, tsp_data

# best result found with value of 160
#initial_starfish = [7, 10, 9, 13, 1, 14, 0, 2, 12, 8, 4, 11, 3, 6, 5]

model = ZombieStarfish(legs_per_starfish=4,
                        maximum_population=10,
                        maximum_generations=10,
                        # initial_starfish= initial_starfish,
                        tsp_data=tsp_data
                        )
print('model loaded')

model.Unleash_Zombie_Starfish()
results = model.ranked_population_dict
results_df = pd.DataFrame(results)