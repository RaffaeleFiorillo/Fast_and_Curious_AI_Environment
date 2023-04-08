import math
import neat.nn
import src.Adaptations as Adp


def normalize(max_value, min_value, value):
    return (value-min_value) / (max_value-min_value)


def activation_function(value):
    return 1/(1+math.e**(-value))


def make_discrete(value):
    if -0.7 <= value <= 0.7:  # comes first because it is the most likely
        return 0
    elif -1 <= value <= -0.7:
        return -1
    return 1


class Agent:
    def __init__(self, g, nn, avatar):
        self.genome = g  # genome of the agent
        self.genome.fitness = 0
        self.neural_network: neat.nn.FeedForwardNetwork = nn  # neural network that defines the agent's behaviour
        self.Avatar: Adp.Car = avatar  # the class that performs actions in the environment
        self.parts_collected = 0
        self.time_alive = 0
        self.steady = 0  # times the agent chose not to move

    def move(self, dt):
        nn_input = self.Avatar.get_inputs()
        output = make_discrete(self.neural_network.activate(nn_input)[0])  # 3 possible values instead of infinite
        self.Avatar.movement(output, dt)  # makes the Agent move based on the Neural network output
        self.time_alive += dt
        self.steady += 1-abs(output)  # rewards only outputs of 0. Because it means the Agent is more steady

    def update_fitness(self):
        parts_contribute = self.parts_collected*0.12  # goal: 1.3 parts/s | total: 25% points
        time_alive_contribute = self.time_alive*0.33  # goal : 150 seconds reward 50 points
        steady_contribute = self.steady*0.0026  # goal: choosing not to move 127 times each second | total: 25% points
        print(f"sc: {steady_contribute} | pc: {parts_contribute} | tc: {time_alive_contribute}")
        self.genome.fitness = parts_contribute+time_alive_contribute+steady_contribute
