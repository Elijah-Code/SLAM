from environment import Wall
import random



def is_horizontal(tl,br):
    return tl[1] == br[1]

def get_surrounding_walls(surface, size=5):
    """
    Surround a surface with walls
    :param surface: pygame.Surface
    :param size: (int) size of the wall
    """
    walls_divisions = 10

    w = surface.get_width()
    h = surface.get_height()
    rects = [
        [(size,size), (w-size, size)],
        [(w-size, size), (w-size,h-size)],
        [ (size,h-size), (size, size)],
        [(w-size,h-size), (size,h-size)]
    ]
    walls =[] 
    for topleft, botright in rects:
        if is_horizontal(topleft, botright):
            dx = (botright[0] - topleft[0]) // walls_divisions
            for n in range(walls_divisions):
                sub_tl = (topleft[0] + n * dx, topleft[1])
                sub_br = (topleft[0] + (n + 1) * dx, botright[1])

                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                walls.append(Wall(sub_tl, sub_br, color=color))
        else:
            
            dy = (botright[1] - topleft[1]) // walls_divisions
            for n in range(walls_divisions):
                sub_tl = (topleft[0], topleft[1] + n * dy)
                sub_br = (botright[0], topleft[1]  + (n + 1) * dy)

                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                walls.append(Wall(sub_tl, sub_br, color=color))

    return walls



