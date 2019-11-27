import pygame
import pymunk
import math
from pymunk import Vec2d
from pygame.locals import *
from characters import Bird, Wood, Pig
from config import *
import levels
from levels import levels_list


class Button:
    def __init__(self, x, y, image, size=None):
        if size is None:
            self.image = pygame.transform.scale(image, button_small_size)
            self.image_clicked = pygame.transform.scale(image, button_med_size)
            self.size = button_small_size
        else:
            self.image = pygame.transform.scale(image, size)
            self.image_clicked = pygame.transform.scale(image, (size[0] + 10, size[1] + 10))
            self.size = size
        self.x = x
        self.y = y

    def has_mouse_on_it(self):
        x, y = pygame.mouse.get_pos()
        return self.x <= x <= self.x + self.size[0] and self.y <= y <= self.y + self.size[1]


    def draw(self, screen):
        if self.has_mouse_on_it():
            screen.blit(self.image_clicked, (self.x, self.y))
        else:
            screen.blit(self.image, (self.x, self.y))

    def action_attached(self):
        pass


impulse = Vec2d(0,0)
x_bird = 0
y_bird = 0

birds = []
birds_trails = []
current_level = 0
level = levels_list[current_level]
level.add_objects_to_space(space)

# buttons
#play = Button(10, 10, play_button)
pause = Button(10, 10, pause_button)
# restart = Button(x, y, restart_button)

score = 0


def solve_collision_bird_pig(arbiter, space, _):
    a, b = arbiter.shapes
    a_body = a.body
    b_body = b.body

    # Draw a red circle around pig and bird to mimic explosion
    x, y = to_pygame(b_body.position)
    pygame.draw.circle(screen, YELLOW, (x, y), pig_radius + 5)
    x, y = to_pygame(a_body.position)
    pygame.draw.circle(screen, RED, (x, y), bird_radius + 5)

    # Remove the pig and the bird from the space
    space.remove(a)
    space.remove(a_body)
    space.remove(b)
    space.remove(b_body)

    # remove the pig and bird from their respective lists
    pigs_to_remove = []
    for pig_ in level.pigs:
        if pig_.body == b_body:
            pigs_to_remove.append(pig_)

    for pig_ in pigs_to_remove:
        level.pigs.remove(pig_)

    birds_to_remove = []
    for bird_ in birds:
        if bird_.body == a_body:
            birds_to_remove.append(bird_)
    for bird_ in birds_to_remove:
        birds.remove(bird_)

    # update score
    global score
    score += 10000

def solve_collision_pig_wood(arbiter, space, _):
    a, b = arbiter.shapes
    if arbiter.total_impulse.length > pig_wood_minimum_impulse:
        # draw a circle around the pig to mimic an explosion
        x, y = to_pygame(a.body.position)
        pygame.draw.circle(screen, YELLOW, (x, y), pig_radius)

        for pig_ in level.pigs:
            if pig_.shape == a:
                level.pigs.remove(pig_)
                break

        space.remove(a)
        space.remove(a.body)

        # update score
        global score
        score += 10000


space.add_collision_handler(BIRD_COLLISION_TYPE, PIG_COLLISION_TYPE).post_solve = solve_collision_bird_pig
space.add_collision_handler(PIG_COLLISION_TYPE, WOOD_COLLISION_TYPE).post_solve = solve_collision_pig_wood

def distance(x0, y0, x1, y1):
    return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

def unit_vector(v):
    if v.length == 0:
        return v
    return v / v.length


def in_aiming_bounds(x, y):
    return aiming_bounds_x[0] <= x <= aiming_bounds_x[1] \
           and aiming_bounds_y[0] <= y <= aiming_bounds_y[1]

def sling_action(x, y):
    # get the vector from sling to streching point
    v_back = Vec2d(x - sling_back_x, y - sling_back_y)

    # If that vector is too long, restrict it to the length of the rope
    if v_back.length > rope_length:
        v_back = unit_vector(v_back) * rope_length
        x = sling_back_x + v_back.x
        y = sling_back_y + v_back.y

    # Get the endpoint pf the rope
    final_v_back = v_back + bird_radius * unit_vector(v_back)
    x_final = sling_back_x + final_v_back.x
    y_final = sling_back_y + final_v_back.y

    # draw back rope, bird and front rope
    pygame.draw.line(screen, BLACK, (sling_back_x, sling_back_y), (x_final, y_final), rope_thickness)
    screen.blit(bird, (x - bird_radius, y - bird_radius))
    pygame.draw.line(screen, BLACK, (sling_front_x, sling_front_y), (x_final, y_final), rope_thickness)

    # Update bird location
    global x_bird
    global y_bird
    x_bird = x
    y_bird = y

    # get the impulse
    global impulse
    impulse_x = - (x_bird - sling_back_x)
    impulse_y = (y_bird - sling_back_y)
    impulse = Vec2d(impulse_x, impulse_y) * impulse_multiplier

def get_max_speed():
    max_speed = 0
    for bird_ in birds:
        x, y = to_pygame(bird_.body.position)
        if in_bounds_x(x):
            bird_speed = bird_.body.velocity.length
            if bird_speed > max_speed:
                max_speed = bird_speed
    return max_speed

def game_over_loop():
    global score
    restart = Button(game_over_restart_button_x, game_over_restart_button_y, restart_button, button_large_size)
    game_over = True
    while game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONUP and restart.has_mouse_on_it():
                game_over = False
                score = 0
                birds_trails.clear()
                for bird_ in birds:
                    space.remove(bird_.shape, bird_.body)
                birds.clear()
                level.restart(space)
                level.add_objects_to_space(space)

        rect = pygame.Rect(game_over_rect_x_y, game_over_rect_size)
        pygame.draw.rect(screen, BLACK, rect)

        message = big_font.render('Level Failed', True, WHITE)
        screen.blit(message, game_over_message_x_y)

        screen.blit(pig_failed, pig_failed_x_y)

        restart.draw(screen)
        pygame.display.flip()

def level_cleared_loop():
    global level
    global current_level
    global score
    restart = Button(level_cleared_restart_button_x, level_cleared_restart_button_y, restart_button, button_large_size)
    next_level = Button(next_level_button_x, next_level_button_y, next_level_button, button_large_size)
    level_cleared = True
    while level_cleared:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONUP:
                if restart.has_mouse_on_it():
                    score = 0
                    level_cleared = False
                    birds_trails.clear()
                    for bird_ in birds:
                        space.remove(bird_.shape, bird_.body)
                    birds.clear()
                    level.restart(space)
                    level.add_objects_to_space(space)
                elif next_level.has_mouse_on_it():
                    level_cleared = False
                    score = 0
                    birds_trails.clear()
                    for bird_ in birds:
                        space.remove(bird_.shape, bird_.body)
                    birds.clear()
                    if current_level >= len(levels_list) - 1:
                        current_level = 0
                    else:
                        current_level += 1
                    level.restart(space)
                    level = levels_list[current_level]
                    level.add_objects_to_space(space)


        rect = pygame.Rect(level_cleared_rect_x_y, level_cleared_rect_size)
        pygame.draw.rect(screen, PURPLE, rect)

        message = big_font.render('Level Cleared!', True, WHITE)
        screen.blit(message, level_cleared_message_x_y)

        # display score
        score_msg_1 = big_font.render('SCORE', True, WHITE)
        screen.blit(score_msg_1, level_cleared_score_1_x_y)
        score_msg_2 = big_font.render(str(score), True, WHITE)
        screen.blit(score_msg_2, level_cleared_score_2_x_y)

        # draw stars
        star_rating = level.get_star_rating()
        if star_rating >= 1:
            # draw middle star
            screen.blit(middle_star, middle_star_x_y)
        if star_rating >= 2:
            # draw left star
            screen.blit(left_star, left_star_x_y)
        if star_rating >= 3:
            # draw right star
            screen.blit(right_star, right_star_x_y)

        restart.draw(screen)
        next_level.draw(screen)
        pygame.display.flip()

def in_bounds(x, y):
    return 0 <= x <= screen_size[0] and 0 <= y <= screen_size[1]

def in_bounds_x(x):
    return 0 <= x <= screen_size[0]


def pause_loop():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONDOWN:
                if pause.has_mouse_on_it():
                    paused = False

pause.action = pause_loop

def main():
    running = True
    in_sling_action = False
    t1 = 0
    trail_counter = 0
    waiting = False
    wait_counter = 0
    global score
    score = 0

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEMOTION:
                pass
                #print(pygame.mouse.get_pos())
            elif pygame.mouse.get_pressed()[0] and in_aiming_bounds(*pygame.mouse.get_pos()):
                in_sling_action = True
            elif event.type == MOUSEBUTTONUP and in_sling_action:
                in_sling_action = False
                print(len(birds))
                if level.n_birds > 0:
                    # release the bird
                    x, y = to_pymunk(x_bird, y_bird)
                    bird_ = Bird(x, y, impulse)
                    space.add(bird_.shape, bird_.body)
                    birds.append(bird_)
                    if level.n_birds > 0:
                        level.n_birds -= 1
                    t1 = pygame.time.get_ticks()
            elif event.type == MOUSEBUTTONDOWN and pause.has_mouse_on_it():
                pause_loop()


        # draw background
        screen.blit(background, background_x_y)

        birds_to_remove = []
        # display moving birds:
        for bird_ in birds:
            x, y = to_pygame(bird_.body.position)
            # screen.blit(bird, (x - bird_radius, y - bird_radius))
            bird_.draw(screen)
            if bird_.body.velocity.length <= 0 or not in_bounds_x(x):
                birds_to_remove.append(bird_)

        for bird_ in birds_to_remove:
            birds.remove(bird_)
            space.remove(bird_.body)
            space.remove(bird_.shape)

        # display bird's trails
        trail_counter += 1
        changed = False
        for bird_ in birds:
            if trail_counter % trail_counter_interval == 0 and bird_.body.velocity.length > trail_counter_speed_limit:
                changed = True
                x, y = to_pygame(bird_.body.position)
                birds_trails.append((x, y))
        if changed:
            trail_counter = 1
        for x, y in birds_trails:
            pygame.draw.circle(screen, WHITE, (x, y), 4)

        # display level
        level.draw(screen)

        # display buttons
        pause.draw(screen)

        if in_sling_action and level.n_birds > 0:
            x, y = pygame.mouse.get_pos()
            sling_action(x, y)

        # display sling's back
        screen.blit(sling_back, sling_back_x_y)
        # draw bird here
        if level.n_birds > 0 and not in_sling_action and pygame.time.get_ticks() - t1 > time_before_next_bird:
            screen.blit(bird, bird_init_x_y)
        elif not in_sling_action:
            pygame.draw.line(screen, BLACK, (sling_back_x, sling_back_y), (sling_front_x, sling_front_y), 2)
        # display sling's front
        screen.blit(sling_front, sling_front_x_y)

        # check for game over
        if level.n_birds == 0 and len(level.pigs) > 0 and get_max_speed() < birds_min_speed:
            game_over_loop()

        # check for level cleared
        if len(level.pigs) == 0:
            level_cleared_loop()

        # display score
        score_msg_1 = med_font.render('SCORE', True, WHITE)
        screen.blit(score_msg_1, score_1_x_y)
        score_msg_2 = med_font.render(str(score), True, WHITE)
        screen.blit(score_msg_2, score_2_x_y)

        # draw walls
        # pygame.draw.line(screen, BLACK, to_pygame(Vec2d(r_a_x, r_a_y)), to_pygame(Vec2d(r_b_x, r_b_y)), 3)
        # pygame.draw.line(screen, BLACK, to_pygame(Vec2d(l_a_x, l_a_y)), to_pygame(Vec2d(l_b_x, l_b_y)), 3)


        for i in range(2):
            space.step(1/(2 * FPS))
        pygame.display.flip()
        clock.tick(FPS)

main()