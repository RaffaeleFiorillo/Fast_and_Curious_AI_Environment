import pygame
import random as rd
from math import tanh

parts_colors = ((255, 128, 0), (255, 242, 0), (34, 177, 76), (252, 130, 19), (237, 28, 36), (255, 0, 255),
				(120, 0, 120), (0, 255, 255), (0, 0, 255))
road_colors = ((0, 0, 0), (108, 108, 108), (255, 255, 255))
CAR_MAX_SPEED = 300
CAR_STE_MIN_DAMAGE_DISTANCE = 400  # distance at which the car starts getting damage from the Space-Time-Entity
CAR_MAX_DISTANCE = 470  # maximum distance the car can reach (right)
CAR_MIN_DISTANCE = CAR_STE_MIN_DAMAGE_DISTANCE - 20  # minimum distance the car can reach (left)
obstacles_distance = 290
parts_distance = 5
space_between_obstacles = [o for o in range(300, 1290, obstacles_distance)]
SCREEN_LENGTH = 1080
LANES = [20, 121, 240]
MAX_TIME = 150


# returns an image ready to be displayed on the screen. "convert_alpha" makes it much faster to display
def load_image(directory: str):
	try:
		return pygame.image.load(f"images/{directory}").convert_alpha()
	except FileNotFoundError:
		exit(f"Error: Directory *images/{directory}* Not Found")


def get_distances(x, y, obj):
	return [obj.x-x, obj.y-y]


# based on given screen coordinates, gives back what type of object is at that position
def see(screen, coo: (int, int)) -> int:
	if coo[1] <= 0:
		return 0
	elif coo[1] > 308:
		return 0
	color = screen.get_at(coo)
	if color in road_colors:
		current_code = 0
	elif color in parts_colors:
		current_code = 1
	else:
		current_code = -1
	# sign = code_meaning[current_code]  # -> turns rgb values into words
	# print(sign)
	return current_code


# Given all seen values, gives back a code value for what to do
def make_a_choice(info: [int], weights, bias) -> int:
	soma = sum([weights[i] * info[i] + bias[i] for i in range(len(info))])
	refined_value = tanh(soma)
	if refined_value >= 0.70:
		return 1
	elif refined_value <= -0.70:
		return -1
	else:
		return 0


class Car:
	def __init__(self):
		self.y_values = [20, 121, 240]
		self.middle = (
			self.y_values[1] - 1, self.y_values[1], self.y_values[1] - 1)  # +-1 error when checking if centered
		self.image = self.get_car_image()
		self.speed = CAR_MAX_SPEED
		self.direction = "STOP"
		self.x = CAR_MAX_DISTANCE - 20
		self.y = self.y_values[1]
		self.hit_box = pygame.mask.from_surface(self.image)
		self.rect = (self.x, self.y, self.image.get_size()[0], self.image.get_size()[1])
		self.distance_to_obstacles = [3000, 0]  # x and y distance to the closest 2 obstacles
		self.distance_to_parts = [3000, 0]  # x and y distance to the closest Parts

	@staticmethod
	def get_car_image():
		return load_image(f"cars/12.png")

	# sort the list of object based on proximity to the car and check for collision only for the closest
	def obstacle_collision(self, l_obstacles):
		# sorting the list and taking only the closest (ahead of the car) to use them for creating the input layer
		f_obstacles = filter(lambda obs: obs.x >= self.x, l_obstacles)  # we only need obstacles in front of the car
		# first_obst, second_obst = sorted(f_obstacles, key=lambda o: ((self.x - o.x)**2 + (self.y - o.y)**2)**0.5)[:2]
		first_obst = sorted(f_obstacles, key=lambda o: ((self.x - o.x)**2 + (self.y - o.y)**2)**0.5)[0]
		# distances_first_object = get_distances(self.x, self.y, first_obst)
		# distances_second_object = get_distances(self.x, self.y, second_obst)
		# self.distance_to_obstacles = distances_first_object+distances_second_object
		self.distance_to_obstacles = get_distances(self.x, self.y, first_obst)
		# checking for collision
		offset = (self.x - first_obst.x + first_obst.adjust, self.y - first_obst.y + first_obst.adjust)
		return self.hit_box.overlap(first_obst.hit_box, offset)

	def get_inputs(self):
		# [x, y, distance_obstacle1, distance_obstacle2, distance_obstacle3, distance_parts]
		inputs = [self.x, self.y] + self.distance_to_obstacles + self.distance_to_parts
		return inputs

	def parts_collision(self, l_parts, dt):
		value, indexes_to_remove = 0, []
		# sorting the list and taking only the closest two to use them for creating the input layer
		f_parts = filter(lambda p: p.x >= self.x, l_parts)  # we only need parts in front of the car
		first_part = sorted(f_parts, key=lambda o: ((self.x - o.x)**2 + (self.y - o.y)**2)**0.5)[0]
		self.distance_to_parts = get_distances(self.x, self.y, first_part)
		for i, part in enumerate(l_parts):
			if part.y + 24 >= self.rect[1] and part.y <= self.rect[1] + self.rect[3]:
				if part.x + 44 >= self.rect[0] and part.x <= self.rect[0] + self.rect[2]:
					value += 1*dt
					# l_parts.pop(i)
					# value += int(l_parts.pop(i))  # part.value-> line to keep for the actual game
		return l_parts, value

	def draw(self, screen):
		screen.blit(self.image, (self.x, round(self.y)))
		# pygame.draw.rect(screen, (255, 255, 0), self.rect, 5)
		# obstacles
		pygame.draw.line(screen, (159, 159, 0), (self.x+22, self.y+10), (self.x+self.distance_to_obstacles[0], self.y+self.distance_to_obstacles[1]), 2)
		# pygame.draw.line(screen, (159, 159, 0), (self.x+22, self.y+10), (self.x+self.distance_to_obstacles[2], self.y+self.distance_to_obstacles[3]), 2)
		# parts
		pygame.draw.line(screen, (255, 0, 255), (self.x+22, self.y+10), (self.x+self.distance_to_parts[0], self.y+self.distance_to_parts[1]), 3)

	def movement(self, new_direction, dt):
		if self.y in LANES:
			self.direction = new_direction
		self.y += self.direction * self.speed * dt  # y = y0+speed_modulo*speed*time

		if self.y >= LANES[2]:  # make sure the car doesn't exit the upper limit
			self.direction = 0
			self.y = LANES[2]
		elif self.y <= LANES[0]:  # make sure the car doesn't exit the lower limit
			self.direction = 0
			self.y = LANES[0]
		elif abs(LANES[1] - self.y) < 2 and self.direction:  # make sure the car stops in the middle lane
			self.direction = 0
			self.y = LANES[1]

		self.rect = (self.x, self.y, self.image.get_size()[0], self.image.get_size()[1])


class Road:
	def __init__(self):
		self.rect = (0, 0, SCREEN_LENGTH, 308)  # characteristics of the road (how it will be drawn)
		self.color = (108, 108, 108)  # color of the road's background
		self.step = 0  # how much the road division has moved backwards for every cycle

	def draw(self, screen, dt):
		pygame.draw.rect(screen, self.color, self.rect)  # draw road background
		self.step = self.step + CAR_MAX_SPEED * dt if 0 <= self.step <= 170 else 0  # updating the step allowing a cycle
		# draw road separations (white rectangles)
		for i in range(8):
			pygame.draw.rect(screen, (255, 255, 255), (round(i * 170 - self.step), 81, 100, 13))  # upper separation
			pygame.draw.rect(screen, (255, 255, 255), (round(i * 170 - self.step), 200, 100, 13))  # lower separation


class _Obstacle:
	def __init__(self, location, ultimo_y):
		self.x = location
		self.adjust = 0  # -10
		self.y = self.calculate_position_y(ultimo_y) - 10
		self.folder = None
		self.image = None
		self.hit_box = None
		self.rect = None
		self.choose_image()
		self.length = 100
		self.frame = 21

	def choose_image(self):
		self.folder = str(rd.randint(1, 4))
		if self.folder == "4":
			self.image = load_image(f"obstacles/4/{rd.randint(1, 11)}.png")
		else:
			self.image = load_image(f"obstacles/{self.folder}/1.png")
		self.hit_box = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()

	def calculate_position_y(self, ultimo_y):
		if ultimo_y == 0:
			return rd.choice([20, 130, 240]) + self.adjust
		possibilities = {20: [130, 240], 130: [20, 240], 240: [130, 20]}
		return rd.choice(possibilities[ultimo_y+10])

	def draw(self, screen):
		screen.blit(self.image, (round(self.x), self.y))

	def mover(self, dt):
		self.x -= CAR_MAX_SPEED * dt
		self.frame += dt*10
		round_frame = round(self.frame)
		if self.frame-round_frame < 0.1 and 20 <= self.frame <= 27 and self.folder != "4":
			self.image = load_image(f"obstacles/{self.folder}/{round_frame-20}.png")


class Obstacles:
	def __init__(self):
		self.internal_list = []
		self.max = len(space_between_obstacles)
		self.first_born = True
		self.ultimo_y = 0
		self.create_obstacles()

	def control_last(self):
		return self.internal_list[-1].x <= space_between_obstacles[-2]

	def create_obstacles(self):
		if self.first_born:
			for i in range(self.max):
				self.first_born = False
				ob = _Obstacle(space_between_obstacles[i], self.ultimo_y)
				if ob.x >= 700:
					self.internal_list.append(ob)
		elif self.control_last():
			self.internal_list.append(_Obstacle(space_between_obstacles[-1], self.ultimo_y))
		self.ultimo_y = self.internal_list[-1].y

	def remove_obstacles(self):
		for obst in self.internal_list:
			if obst.x < -obst.length:
				self.internal_list.remove(obst)
		if len(self.internal_list) <= self.max:
			self.create_obstacles()

	def draw(self, screen, dt):
		for obst in self.internal_list:
			obst.draw(screen)
			obst.mover(dt)


class _Part:
	def __init__(self, x, type_p, y, cardinality):
		self.type_p = type_p
		self.adjust = 15
		self.y_middle = y + self.adjust
		self.y = self.y_middle + cardinality
		self.x = x
		self.value: int = self.type_p ** 2
		self.image = load_image(f"parts/part{self.type_p}.png")
		self.hit_box = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()
		self.length = 32
		self.movement_module = 10
		self.upwards = True

	def __int__(self):
		return self.value

	def draw(self, screen):
		screen.blit(self.image, (round(self.x), round(self.y)))

	def mover(self, dt):
		self.x -= CAR_MAX_SPEED * dt
		self.y += {True: -1, False: 1}[self.upwards]*20*dt  # y direction * y speed * dt
		if abs(self.y_middle - self.y) >= 10:
			self.upwards = not self.upwards


class Parts:
	def __init__(self):
		self.internal_list = []
		self.first_parts = True
		self.choices = [20, 121, 240]
		self.y = rd.choice(self.choices)
		self.dist_between_parts = 5 + 44
		self.min_dist_between_blocs = 100
		self.max_dist_between_blocs = 200
		self.min_parts = 3
		self.max_parts = 7
		self.create_parts()

	def control_last(self):
		return self.internal_list[-1].x <= space_between_obstacles[-2]

	def create_parts(self):
		dist_between_blocs = rd.randint(self.min_dist_between_blocs, self.max_dist_between_blocs)
		type_p = self.calculate_type_part()
		if self.first_parts:
			for i in range(rd.randint(self.min_parts, self.max_parts)):
				self.internal_list.append(
					_Part(space_between_obstacles[-1] + dist_between_blocs + i * self.dist_between_parts, type_p,
						  self.y, i % 10))
			self.first_parts = False
			return 0
		if self.control_last():
			for i in range(rd.randint(self.min_parts, self.max_parts)):
				self.internal_list.append(
					_Part(space_between_obstacles[-1] + dist_between_blocs + i * self.dist_between_parts,
						  type_p, self.y, i % 10))
			self.y = rd.choice(self.choices)
			return 0

	@staticmethod
	def calculate_type_part():
		return rd.choice([1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5])  # random type (some are rarer than others)

	def remove_parts(self, internal_list_obst):
		for part, obst in zip(self.internal_list, internal_list_obst):
			if part.x < -part.length:  # part is outside the screen
				self.internal_list.remove(part)
			# parts are overlapping with obstacle
			"""elif obst.x + obst.length > part.x + part.length and obst.x < part.x:
				print(self.y, obst.y, (self.y - 10)//100 == (obst.y-10)//100, sep=" | ")
				if (self.y - 10)//100 == (obst.y-10)//100:
					self.internal_list.remove(part)"""

	def draw(self, screen, dt):
		for part in self.internal_list:
			part.draw(screen)
			part.mover(dt)
