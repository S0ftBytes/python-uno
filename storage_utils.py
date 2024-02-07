import os
from csv import writer, reader
from pathlib import Path
from shutil import rmtree
import numpy as np
import ast

def store_move(instance, old_state, action, reward, new_state, game_over):
    print('store move')
    rows = [old_state, action, reward, new_state, game_over]

    Path("instance_data").mkdir(parents=True, exist_ok=True)

    file_name = str(instance) + '.csv'
    with open(f'instance_data/{file_name}', 'a') as csv_obj:
        writer_obj = writer(csv_obj)
        writer_obj.writerow(rows)

        csv_obj.close()

def update_master(number_of_instances, file_name='training_data.csv'):
    for instance in range(1, number_of_instances + 1):
        instance_file_name = f'instance_data/{instance}.csv'
        
        if not os.path.exists(instance_file_name):
            print(f"File {instance_file_name} does not exist.")
            continue

        with open(instance_file_name, 'r') as instance_file:
            csv_reader = reader(instance_file)
            instance_data = list(csv_reader)
        
        with open(file_name, 'a', newline='') as master_file:
            writer_obj = writer(master_file)
            writer_obj.writerows(instance_data)
        
    rmtree('instance_data')

def get_master(file_name='training_data.csv'):
    data = None
    with open(file_name, 'r') as instance_file:
        csv_reader = reader(instance_file)
        data = list(csv_reader)

    return data

def restore_row(row):
    state = np.array([int(x) for x in row[0].strip("[]").split()], dtype=int)
    next_state = np.array([int(x) for x in row[3].strip("[]").split()], dtype=int)
    
    action = ast.literal_eval(row[1])
    
    reward = int(row[2])
    
    game_finished = row[4] == 'True'
    
    return state, action, reward, next_state, game_finished