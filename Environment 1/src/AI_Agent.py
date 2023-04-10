import math
import neat.nn
import src.Adaptations as Adp

TIME_W = 50/Adp.MAX_TIME  # [goal-dist-points(pts)]/[goal-time(sec)]= (pts/sec)
PARTS_W = 50/60  # [goal-part-points(pts)]/[goal-parts(part)] = (pts/part)
# STEADY_W = 225/45000  # [times-chosen-to-stay-still(unit)]/[goal-distance] = (unit/pix)


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
        distance_contribute = self.time_alive*TIME_W  # goal : 45000 pixels | total: 50 points  |
        parts_contribute = self.parts_collected*PARTS_W  # goal: 2.5 pts/part | total: 50 points  |
        # steady_contribute = self.steady*STEADY_W
        self.genome.fitness = parts_contribute+distance_contribute  # +steady_contribute
        if self.genome.fitness >= 10:
            print(f"Fitness = {self.genome.fitness}"
                  f" p={self.parts_collected} -> pc: {parts_contribute} |"
                  f" t={self.time_alive} -> tc: {distance_contribute}")
