import torch

def predict_action(model, state):
    action = [0,0,0]

    state0 = torch.tensor(state, dtype=torch.float)
    prediction = model(state0)
    move = torch.argmax(prediction).item()
    action[move] = 1

    return action