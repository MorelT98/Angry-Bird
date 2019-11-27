import pygame
import pymunk

FPS = 30    # frames per second

# SIZES
screen_size = (1200, 650)
bird_size = (30, 30)
bird_radius = 15
pig_size = (30, 30)
pig_radius = 15
beam_size = (85, 20)
column_size = (20, 85)
sling_front_size = (20, 65)
sling_back_size = (22, 101)
ground_y = 560
button_small_size = (30, 30)
button_med_size = (50, 50)
button_large_size = (60, 60)
pig_failed_size = (200, 200)
star_size = (75, 75)
rope_thickness = 5
background_x_y = (0, -100)

# aiming bounds
aiming_bounds_x = (111, 175)
aiming_bounds_y = (451, 562)

# pygame initialization
pygame.init()
pygame.display.set_caption('Angry Birds')
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()

# COLORS
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 153)
WHITE = (255, 255, 255)
PURPLE = (102, 51, 153)

# FONTS
big_font = pygame.font.SysFont('arial', 50, bold=True)
med_font = pygame.font.SysFont('arial', 30, bold=True)
small_font = pygame.font.SysFont('arial', 20, bold=True)

impulse_multiplier = 75 # proportion of power of the sling
time_before_next_bird = 500 # lag time before drawing next bird in sling
birds_min_speed = 30 # birds with speed lower than this will be destroyed

### COLLISION HANDLERS
BIRD_COLLISION_TYPE = 0
PIG_COLLISION_TYPE = 1
WOOD_COLLISION_TYPE = 2
GROUND_COLLISION_TYPE = 3
WALL_COLLISION_TYPE = 4

def to_pygame(p):
    '''Converts a pymunk Vec2d object into pygame coordinates'''
    return int(p.x), int(screen_size[1] - p.y)

def to_pymunk(x, y):
    '''Converts pygame coordinates into pygmunk coordinates'''
    return x, screen_size[1] - y

# GROUND
ground_body = pymunk.Body(1000000, 10, body_type=pymunk.Body.STATIC)
a_x, a_y = to_pymunk(-100, ground_y)
b_x, b_y = to_pymunk(screen_size[0] + 100, ground_y)
ground_shape = pymunk.Segment(ground_body, (a_x, int(a_y)), (b_x, int(b_y)), 0)
ground_shape.elasticity = 0.95
ground_shape.friction = 1.05
ground_shape.collision_type = GROUND_COLLISION_TYPE

# RIGHT WALL
right_wall_body = pymunk.Body(100000, 10, body_type=pymunk.Body.STATIC)
r_a_x, r_a_y = to_pymunk(screen_size[0] - 10, screen_size[1] + 100)
r_b_x, r_b_y = to_pymunk(screen_size[0] - 10, 0)
right_wall_shape = pymunk.Segment(right_wall_body, (r_a_x, r_a_y), (r_b_x, r_b_y), 0)
right_wall_shape.elasticity = 0.95
right_wall_shape.collision_type = WALL_COLLISION_TYPE

# LEFT WALL
left_wall_body = pymunk.Body(1000000, 10, body_type=pymunk.Body.STATIC)
l_a_x, l_a_y = to_pymunk(10, screen_size[1] + 100)
l_b_x, l_b_y = to_pymunk(10, -100)
left_wall_shape = pymunk.Segment(left_wall_body, (l_a_x, l_a_y), (l_b_x, l_b_y), 0)
left_wall_shape.elasticity = 0.95
left_wall_shape.collision_type = WALL_COLLISION_TYPE

# SPACE
space = pymunk.Space()
space.gravity = (0, -700)
space.add(ground_shape, ground_body)
space.add(left_wall_shape, left_wall_body)
space.add(right_wall_shape, right_wall_body)

### LOAD IMAGES ###

# background image
background = pygame.image.load('./resources/images/background.png')

# bird image
bird = pygame.image.load('./resources/images/angry_birds.png')
rect = pygame.Rect((183, 32), (67, 64))
bird = bird.subsurface(rect).copy()
bird = pygame.transform.scale(bird, bird_size)

# sling images (front and back)
sling = pygame.image.load('./resources/images/sling-2.png')
rect = pygame.Rect((19, 0), (41, 131))
sling_front = sling.subsurface(rect).copy()
sling_front = pygame.transform.scale(sling_front, sling_front_size)
rect = pygame.Rect((98, 8), (45, 203))
sling_back = sling.subsurface(rect).copy()
sling_back = pygame.transform.scale(sling_back, sling_back_size)

# Pig image
# 405, 1 -- 137, 148
pig = pygame.image.load('./resources/images/angry_birds_chrome_pigs_by_chinzapep-d5bnxdz.png')
rect = pygame.Rect((405, 1), (137, 148))
pig = pig.subsurface(rect).copy()
pig = pygame.transform.scale(pig, pig_size)

# Wood images (beams and columns)
# 252, 225 -- 464x417 for beam
beam = pygame.image.load('./resources/images/wood.png')
rect = pygame.Rect((252, 225), (206, 23))
beam = beam.subsurface(rect).copy()
beam = pygame.transform.scale(beam, beam_size)

# 127, 165 -- 43x86 for column
column = pygame.image.load('./resources/images/wood2.png')
rect = pygame.Rect((127, 165), (43, 86))
column = column.subsurface(rect).copy()
column = pygame.transform.scale(column, column_size)

# Pause button
# 1577, 235
pause_button = pygame.image.load('./resources/images/buttons-image.png')
rect = pygame.Rect((1577, 235), (88, 86))
pause_button = pause_button.subsurface(rect).copy()

# Play button
# 1576, 339
play_button = pygame.image.load('./resources/images/buttons-image.png')
rect = pygame.Rect((1576, 339), (84, 81))
play_button = play_button.subsurface(rect).copy()

# Restart button
# 1579, 129
restart_button = pygame.image.load('./resources/images/buttons-image.png')
rect = pygame.Rect((1579, 129), (86, 86))
restart_button = restart_button.subsurface(rect).copy()

# next level button
# 340, 807 -- 147x134
next_level_button = pygame.image.load('./resources/images/buttons-image.png')
rect = pygame.Rect((340, 807), (147, 134))
next_level_button = next_level_button.subsurface(rect).copy()

# Pig failed image
pig_failed = pygame.image.load('./resources/images/pig_failed.png')
pig_failed = pygame.transform.scale(pig_failed, pig_failed_size)

# Stars
# middle star: 219, 11 -- 187x184
middle_star = pygame.image.load('./resources/images/stars-edited.png')
rect = pygame.Rect((219, 11), (187, 184))
middle_star = middle_star.subsurface(rect).copy()
middle_star = pygame.transform.scale(middle_star, star_size)

# left star: 18,18 -- 171x171
left_star = pygame.image.load('./resources/images/stars-edited.png')
rect = pygame.Rect((18, 18), (171, 171))
left_star = left_star.subsurface(rect).copy()
left_star = pygame.transform.scale(left_star, star_size)

# right star: 443, 16 -- 175x171
right_star = pygame.image.load('./resources/images/stars-edited.png')
rect = pygame.Rect((443, 16), (175, 171))
right_star = right_star.subsurface(rect).copy()
right_star = pygame.transform.scale(right_star, star_size)

### Sling arms
sling_front_x = 133
sling_front_y = 486
sling_back_x = 155
sling_back_y = 482
rope_length = 100
bird_init_x_y = (130, 471)
sling_back_x_y = (140, ground_y - sling_back.get_height())
sling_front_x_y = (147 - sling_front.get_width(), ground_y - sling_back.get_height())

pig_wood_minimum_impulse = 700  # minimum impulse required between pig and wood to destroy the pig

# game over loop parameters
game_over_restart_button_x = 550
game_over_restart_button_y = 450
game_over_rect_x_y = (350, 0)
game_over_rect_size = (470, screen_size[1])
game_over_message_x_y = (455, 21)
pig_failed_x_y = (475, 150)

# Level cleared parameters
level_cleared_restart_button_x = 490
level_cleared_restart_button_y = 500
next_level_button_x = 590
next_level_button_y = 500
level_cleared_rect_x_y = (350, 0)
level_cleared_rect_size = (470, screen_size[1])
level_cleared_message_x_y = (440, 21)
level_cleared_score_1_x_y = (490, 150)
level_cleared_score_2_x_y = (500, 200)
left_star_x_y = (450, 325)
middle_star_x_y = (550, 325)
right_star_x_y = (650, 325)

# birds trails parameters
trail_counter_interval = 5 # number of frames in between two trails
trail_counter_speed_limit = 50 # birds will speed lower than this won't have a trail

# score
score_1_x_y = (1000, 10)
score_2_x_y = (1000, 40)

