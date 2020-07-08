

def check_light(light, light_board):
    """checks if the light is in a given interval"""
    l = 0
    s = 0
    if light_board > 300:
        # lower shutters
        s = shut_val
    elif light_board < 200:
        # rise shutters
        s = - shut_val
    if light < lower_bound:
        # adapt lamps
        l = max(min(500, 750 - light), 0)
    return l, s


lower_bound = 700
shut_val = 0.05
