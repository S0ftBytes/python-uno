from agent import Trainer
import storage_utils
from concurrent.futures import ProcessPoolExecutor

def run_trainer(mode, instance, number_of_games):
    Trainer(mode, instance, number_of_games).start()

def get_int(log):
    instances = None

    try:
        while instances == None:
            instances_input = int(input(log))

            instances = instances_input
    except:
        print("The input must be a number!")

    return instances

def get_training_mode():
    options = ['live', 'dataset']

    print("Please enter the training mode:")
    print("\n live (default)")
    print("\n dataset")

    selection_input = input().lower()

    if selection_input not in options: mode = options[0]
    else: mode = selection_input

    return mode

if __name__ == '__main__':
    mode = get_training_mode()
    instance_count = get_int('Please enter the amount of instances to run: ')
    games = 1

    if mode == 'live':
        games = get_int('Please enter the amount of games to run per instance: ')

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(run_trainer, mode, instance, games) for instance in range(1, instance_count + 1)]
    
    if mode == 'live': storage_utils.update_master(instance_count)
