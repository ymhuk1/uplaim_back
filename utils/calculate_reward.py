
def calculate_reward(base_reward, level):
    reward = base_reward / (1.5 ** (level - 1))
    return int(round(reward))
