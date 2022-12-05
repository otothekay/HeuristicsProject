from FireflyTSP import *
from Zombie_Starfish import *

datasets = [tsp_lab_data, tsp_data_bays29, tsp_data_eil51, tsp_data_KroA100]
optimals = [lab_data_optimal, tsp_data_bays29_optimal, tsp_data_eil51_optimal, tsp_data_KroA100_optimal]
runs_per_dataset = 5

results_df = None
filename = 'Firefly_Algorithm_run_data.csv'

for index, (dataset, optimal_value) in enumerate(zip(datasets[1:], optimals[1:])):
    for run in range(0, runs_per_dataset):
        print('')
        print(f'Run {run} for dataset {index}')

        model = FireflyTSP(
            population_size=24,
            maximum_generations=40,
            max_time=20,  # minutes
            tsp_data=dataset,
            test_optimal=optimal_value,
                            )

        model.Unleash_Firefly()
        event_data = model.event_log
        event_data['index'] = [index] * len(event_data['time'])
        event_data['run'] = [run] * len(event_data['time'])

        if results_df is None:
            results_df = pd.DataFrame(columns=event_data.keys())

            data_df = pd.DataFrame(data=event_data)
            copy = results_df.copy()
            results_df = pd.concat([copy, data_df], axis=0)

        else:
            data_df = pd.DataFrame(data=event_data)
            copy = results_df.copy()
            results_df = pd.concat([copy, data_df], axis=0)

        print('')

    results_df.to_csv(filename)
