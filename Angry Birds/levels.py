from characters import Pig, Wood
from config import *
import copy

class Level:
    ''' Class Representing a level in Angry Birds.
        Each level comes with a base dictionary that should contain:
        - n_birds: the number of birds
        - pigs: An array containing the locations of all the pigs of the level, as tuples
        - beams: An array containing the locations of all the beams of the level, as tuples
        - columns: An array containing the locations of all the columns of the level, as tuples
    '''
    def __init__(self, base_dict):
        self.base_dict = base_dict
        self.n_birds = base_dict['n_birds']
        self.create_objects()


    def create_objects(self):
        # create the Pigs
        pigs = []
        for x, y in self.base_dict['pigs']:
            pig_ = Pig(x, y)
            pigs.append(pig_)
        self.pigs = pigs

        # create the beams
        beams = []
        for x, y in self.base_dict['beams']:
            beam_ = Wood(x, y, beam_size[0], beam_size[1], type='beam')
            beams.append(beam_)
        self.beams = beams

        # create the columns
        columns = []
        for x, y in self.base_dict['columns']:
            column_ = Wood(x, y, column_size[0], column_size[1], type='column')
            columns.append(column_)
        self.columns = columns

    def add_objects_to_space(self, space):
        for pig_ in self.pigs:
            space.add(pig_.shape, pig_.body)
        for beam_ in self.beams:
            space.add(beam_.shape, beam_.body)
        for column_ in self.columns:
            space.add(column_.shape, column_.body)

    def add_n_shape(self, x, y, pig_inside=False):
        beam_x, beam_y = x + beam_size[0] / 2, y - beam_size[1] / 2
        column_1_x, column_1_y = x + column_size[0] / 2, y - beam_size[1] - column_size[1] / 2
        column_2_x, column_2_y = x + beam_size[0] - column_size[0] + column_size[0] / 2, y - beam_size[1] - column_size[1] / 2
        beam = Wood(beam_x, beam_y, beam_size[0], beam_size[1], type='beam')
        column_1 = Wood(column_1_x, column_1_y, column_size[0], column_size[1], type='column')
        column_2 = Wood(column_2_x, column_2_y, column_size[0], column_size[1], type='column')

        if pig_inside:
            pig_x = beam_x
            pig_y = y - beam_size[1] - column_size[1] + pig_radius
            pig = Pig(pig_x, pig_y)
            self.pigs.append(pig)
            self.base_dict['pigs'].append((pig_x, pig_y))

        self.beams.append(beam)
        self.columns.append(column_1)
        self.columns.append(column_2)

        # update dictionnary
        self.base_dict['beams'].append((beam_x, beam_y))
        self.base_dict['columns'].append((column_1_x, column_1_y))
        self.base_dict['columns'].append((column_2_x, column_2_y))

    def add_t_shape(self, x, y, length=1, pig_on_top=False):
        beam_x, beam_y = x + beam_size[0] / 2, y - beam_size[1] / 2
        column_x, column_y = beam_x, y - beam_size[1] - column_size[1] / 2

        # Create top beam
        beam = Wood(beam_x, beam_y, beam_size[0], beam_size[1], type='beam')
        self.beams.append(beam)
        self.base_dict['beams'].append((beam_x, beam_y))

        # create columns
        for i in range(length):
            column = Wood(column_x, column_y, column_size[0], column_size[1], type='column')
            self.columns.append(column)
            self.base_dict['columns'].append((column_x, column_y))
            column_y -= column_size[1]

        # add pig
        if pig_on_top:
            pig_x = beam_x
            pig_y = y + pig_radius
            pig = Pig(pig_x, pig_y)
            self.pigs.append(pig)
            self.base_dict['pigs'].append((pig_x, pig_y))

    def add_pile_of_beams(self, x, y, length, pig_on_top=False):
        b_x, b_y = x + beam_size[0] / 2, y - beam_size[1] / 2
        if pig_on_top:
            pig_x, pig_y = b_x, y + pig_radius
            pig = Pig(pig_x, pig_y)
            self.pigs.append(pig)
            self.base_dict['pigs'].append((pig_x, pig_y))

        for i in range(length):
            beam_x, beam_y = b_x, b_y
            beam = Wood(beam_x, beam_y, beam_size[0], beam_size[1], type='beam')
            self.beams.append(beam)
            self.base_dict['beams'].append((beam_x, beam_y))

            b_y -= beam_size[1]



    def draw(self, screen):
        # display remaining birds
        for i in range(self.n_birds - 1):
            screen.blit(bird, (100 - i * bird_size[0], ground_y - bird_size[1]))

        # display beams:
        for beam_ in self.beams:
            beam_.draw(screen)

        # display columns:
        for column_ in self.columns:
            column_.draw(screen)

        # display pigs:
        for pig_ in self.pigs:
            pig_.draw(screen)

    def remove_objects_from_space(self, space):
        for beam_ in self.beams:
            space.remove(beam_.shape, beam_.body)
        for column_ in self.columns:
            space.remove(column_.shape, column_.body)
        for pig_ in self.pigs:
            space.remove(pig_.shape, pig_.body)

    def restart(self, space):
        self.n_birds = self.base_dict['n_birds']
        # remove beams
        beams_to_remove = []
        for beam_ in self.beams:
            beams_to_remove.append(beam_)
        for beam_ in beams_to_remove:
            self.beams.remove(beam_)
            space.remove(beam_.shape, beam_.body)

        # remove columns
        columns_to_remove = []
        for column_ in self.columns:
            columns_to_remove.append(column_)
        for column_ in columns_to_remove:
            self.columns.remove(column_)
            space.remove(column_.body, column_.shape)

        # remove pigs
        pigs_to_remove = []
        for pig_ in self.pigs:
            pigs_to_remove.append(pig_)
        for pig_ in pigs_to_remove:
            self.pigs.remove(pig_)
            space.remove(pig_.body, pig_.shape)

        self.create_objects()

    def get_star_rating(self):
        if self.base_dict['n_birds'] <= 1:
            return 3
        return int(3 * self.n_birds / (self.base_dict['n_birds'] - 1))


base_dict = {
    'n_birds': 4,
    'pigs': [],
    'beams': [],
    'columns': []
}
level_1 = Level(copy.deepcopy(base_dict))
x, y = to_pymunk(900, ground_y - column_size[1] - beam_size[1])
level_1.add_n_shape(x, y, pig_inside=True)
x, y = to_pymunk(900, ground_y - 2 * column_size[1] - 2 * beam_size[1])
level_1.add_n_shape(x, y, pig_inside=True)



level_2 = Level(copy.deepcopy(base_dict))
x, y = to_pymunk(900, ground_y - column_size[1] - beam_size[1])
level_2.add_t_shape(x, y, length=1, pig_on_top=True)
x, y = to_pymunk(1000, ground_y - 2 * column_size[1] - beam_size[1])
level_2.add_t_shape(x, y, length=2, pig_on_top=True)

level_3 = Level(copy.deepcopy(base_dict))
a_x, a_y = 800, ground_y - column_size[1] - beam_size[1]
for i in range(3):
    x, y = to_pymunk(a_x, a_y)
    level_3.add_n_shape(x, y, pig_inside=False)
    a_x += 2 * beam_size[0] - 2 * column_size[0]
a_x, a_y = 800 + beam_size[0] - column_size[0], ground_y - column_size[1] - 2 * beam_size[1]

for i in range(2):
    beam_x, beam_y = to_pymunk(a_x + beam_size[0] / 2, a_y + beam_size[1] / 2)
    beam = Wood(beam_x, beam_y, beam_size[0], beam_size[1], type='beam')
    level_3.beams.append(beam)
    level_3.base_dict['beams'].append((beam_x, beam_y))

    n_x, n_y = to_pymunk(a_x, a_y - column_size[1] - beam_size[1])
    level_3.add_n_shape(n_x, n_y, pig_inside=True)

    a_x += 2 * beam_size[0] - 2 * column_size[0]

a_x, a_y = 800 + 2 * beam_size[0] - 2 * column_size[0], ground_y - 2 * column_size[1] - 4 * beam_size[1]
beam_x, beam_y = to_pymunk(a_x + beam_size[0] / 2, a_y + beam_size[1] / 2)
beam = Wood(beam_x, beam_y, beam_size[0], beam_size[1], type='beam')
level_3.beams.append(beam)
level_3.base_dict['beams'].append((beam_x, beam_y))

n_x, n_y = to_pymunk(a_x, a_y - column_size[1] - beam_size[1])
level_3.add_n_shape(n_x, n_y, pig_inside=True)


level_4 = Level(copy.deepcopy(base_dict))
p_x, p_y = 800, ground_y - pig_radius - 100
for i in range(3):
    pig_x, pig_y = to_pymunk(p_x, p_y)
    pig = Pig(pig_x, pig_y)
    level_4.pigs.append(pig)
    level_4.base_dict['pigs'].append((pig_x, pig_y))

    p_x += 150
    if i == 0:
        p_y -= 100
    else:
        p_y += 100

level_5 = Level(copy.deepcopy(base_dict))
p_x, p_y = to_pymunk(750, ground_y - 9 * beam_size[1])
level_5.add_pile_of_beams(p_x, p_y, 9, pig_on_top=True)

p_x, p_y = to_pymunk(750 + 2 * beam_size[0], ground_y - 4 * beam_size[1])
level_5.add_pile_of_beams(p_x, p_y, 4, pig_on_top=False)

p_x, p_y = to_pymunk(750 + 2 * beam_size[0], ground_y - 5 * beam_size[1] - column_size[1])
level_5.add_n_shape(p_x, p_y, pig_inside=True)

levels_list = [level_1, level_2, level_3, level_4, level_5]