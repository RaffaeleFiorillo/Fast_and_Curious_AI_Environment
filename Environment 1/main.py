import neat
import os
import pickle
import src.Environment as Env
import src.AI_Agent as AIa
import src.Adaptations as Adp
import pygame as pg
pg.init()

# screen stuff
screen = pg.display.set_mode((1080, 700))
pg.display.set_caption("Fast and Curious-AI Training")

# Algorithm Steps:
# 1: initialize population of agents
# 2: spawn every agent in the environment
# 3: test their performance when they die or reach a certain goal
# 4: make the best agents reproduce (creating 70% of a new population) and spawn random agents (remaining percentage)
# 5: go back to number 2 until a certain performance goal is achieved


def get_fitness(genomes, config):
    agents = [AIa.Agent(g, neat.nn.FeedForwardNetwork.create(g, config), Adp.Car()) for _, g in genomes]
    world = Env.Training_World(screen)
    fitness = world.start(agents)
    return fitness


# if no pop is provided, upload it from the checkpoint
def run_training(pop=neat.Checkpointer.restore_checkpoint("neat-checkpoint-3")):
    # display training information in the console
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    return pop.run(get_fitness, 300)  # returns the winner of the population


def train_population(config):
    population = neat.Population(config)

    # get the best agent and save its data
    winner = run_training(population)  # returns the winner of the population
    checkpointer = neat.Checkpointer()
    checkpointer.save_checkpoint(config, population, population.species, population.generation)
    with open(f"best{population.generation}.pickle", "wb") as f:
        pickle.dump(winner, f)


def use_winner(config):
    with open(f"best{1}.pickle", "rb") as f:
        winner = pickle.load(f)
    neural_net = neat.nn.FeedForwardNetwork.create(winner, config)
    agent = AIa.Agent(winner, neural_net, Adp.Car())

    world = Env.Testing_World(screen)
    world.start(agent)


if __name__ == "__main__":
    # create the population based on the configuration file
    config_path = os.path.join(os.path.dirname(__file__), "config-feedforward.txt")
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # train_population(config)
    use_winner(config)



