# Fast_and_Curious_AI_Environment
A collection of Environments to Create, Train and Test different kinds of Artificial Intelligente algorithms to be used inside the Fast and Curious game, which you can find here: https://github.com/RaffaeleFiorillo/Fast_and_Curious.


## Environment 1 -> Car-Avoiding-Obstacles:
### Introduction:
Inside some Missions of the game, there is a Car trying to run away from a Space-Time entity which wants to destroy it. The road is filled with various types of obstacles (which cause harm on impact) and collectables (the more collected the better).

### Goal:
Make the Car avoid ALL obstacles while collecting as many collectables as possible.

### Approach 1:
- Model: Neural Networks; 
- Training Algorithm: NEAT (https://neat-python.readthedocs.io/en/latest/neat_overview.html);
- Inputs: x and y position of the car, x and y distance to the 2 closest obstacles, x and y distance to the closest collectable;
- Results: Goal is easly achieved in under 5 minutes in terms of avoiding obstacles, but it could be improved in terms of collecting items. The algorithm was ran just for a maximum of 20 minutes, which means a better result could be achieved for longer training times.
