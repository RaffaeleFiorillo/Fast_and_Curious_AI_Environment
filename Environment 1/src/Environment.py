import pygame
import src.Adaptations as adp
import src.config as c


# returns an image ready to be displayed on the screen. "convert_alpha" makes it much faster to display
def load_image(directory: str):
    try:
        return pygame.image.load(f"images/{directory}").convert_alpha()
    except FileNotFoundError:
        exit(f"Error: Directory *images/{directory}* Not Found")


# Creates a world where the AI can be trained
class Training_World:
    def __init__(self, screen_i):
        self.screen = screen_i
        # Game objects
        self.agents = None
        self.road = adp.Road()
        self.obstacles_list = adp.Obstacles()
        self.parts_list = adp.Parts()
        self.hud_image = load_image("HUD/backgrounds/HUD_background_1.png")
        # loop stuff
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.run = True
        self.time_passed = 0
        self.total_time = 0.0
        self.choice = None
        self.resistance = True

    def refresh_game(self):
        self.screen.blit(self.hud_image, (0, 308))
        for entity in [self.road, self.parts_list, self.obstacles_list]:
            entity.draw(self.screen, self.dt)
        for agent in self.agents:
            agent.Avatar.draw(self.screen)
        pygame.display.update()

    def car_movement_y(self):
        for agent in self.agents:
            agent.move(self.dt)

    def continue_game(self):
        return len(self.agents) and self.time_passed < 150

    def start(self, agents):
        self.agents = agents
        while self.run:
            # terminate execution
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                """if event.type == pygame.KEYDOWN:
                    self.manage_buttons(event.key)"""
            # parts effects
            self.parts_list.remove_parts(self.obstacles_list.internal_list)
            self.parts_list.create_parts()
            new_parts_list = []
            # collision & damage
            for i, agent in enumerate(self.agents):
                new_parts_list, value = agent.Avatar.parts_collision(self.parts_list.internal_list)
                agent.parts_collected += value
                if agent.Avatar.obstacle_collision(self.obstacles_list.internal_list):
                    agent.update_fitness()
                    self.agents.pop(i)
            self.parts_list.internal_list = new_parts_list  # must be here for all agents to be able to collect parts
            # obstacles effects
            self.obstacles_list.remove_obstacles()
            self.obstacles_list.create_obstacles()
            # car movement
            self.car_movement_y()
            # Refresh screen
            if self.run:
                self.run = self.continue_game()
            self.refresh_game()
            self.dt = self.clock.tick(c.FRAME_RATE)/1000
            self.time_passed += self.dt
        # af.play(game_over_sound)
        # return False  # if it gets here, it means it not good enough
        [agent.update_fitness() for agent in self.agents]


class Testing_World:
    def __init__(self, screen_i):
        self.screen = screen_i
        # Game objects
        self.agent = None
        self.road = adp.Road()
        self.obstacles_list = adp.Obstacles()
        self.parts_list = adp.Parts()
        self.hud_image = load_image("HUD/backgrounds/HUD_background_1.png")
        # loop stuff
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.run = True
        self.time_passed = 0
        self.total_time = 0.0
        self.choice = None
        self.resistance = True

    def refresh_game(self):
        self.screen.blit(self.hud_image, (0, 308))
        for entity in [self.road, self.parts_list, self.obstacles_list]:
            entity.draw(self.screen, self.dt)
        self.agent.Avatar.draw(self.screen)
        pygame.display.update()

    def car_movement_y(self):
        self.agent.move(self.dt)

    def continue_game(self):
        return self.time_passed < 150

    def start(self, agent):
        self.agent = agent
        while self.run:
            # terminate execution
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                """if event.type == pygame.KEYDOWN:
                    self.manage_buttons(event.key)"""
            # parts effects
            self.parts_list.remove_parts(self.obstacles_list.internal_list)
            self.parts_list.create_parts()
            # collision & damage
            self.parts_list.internal_list, value = self.agent.Avatar.parts_collision(self.parts_list.internal_list)
            if self.agent.Avatar.obstacle_collision(self.obstacles_list.internal_list):
                # self.run = False
                print("Failure!!!")
            # obstacles effects
            self.obstacles_list.remove_obstacles()
            self.obstacles_list.create_obstacles()
            # car movement
            self.car_movement_y()
            # Refresh screen
            if self.run:
                self.run = self.continue_game()
            self.refresh_game()
            self.dt = self.clock.tick(c.FRAME_RATE)/1000
            self.time_passed += self.dt
        # af.play(game_over_sound)
        # return False  # if it gets here, it means it not good enough
        print("Success!!!")
