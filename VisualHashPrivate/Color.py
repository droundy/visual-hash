

def DistinctColorFloat(random):
    h = 6*random.random()
    saturation = random.random()**.5
    value = random.random()
    cutoff = 0.4
    power = .25
    if value < cutoff:
        value = cutoff*(value/cutoff)**power
    if value > 1.0 - cutoff:
        value = (1.0-cutoff) + cutoff*(value - (1.0 - cutoff))**power
    c = saturation*value
    x = c*(1-(h % 2 - 1))
    if h < 1:
        r, g, b = c, x, 0
    elif h < 2:
        r, g, b = x, c, 0
    elif h < 3:
        r, g, b = 0, c, x
    elif h < 4:
        r, g, b = 0, x, c
    elif h < 5:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    m = value - c
    r = r + m
    g = g + m
    b = b + m
    r = random.random()
    g = random.random()
    b = random.random()
    return r, g, b

def DistinctColor(random):
    r, g, b = DistinctColorFloat(random)
    return int(256*r), int(256*g), int(256*b)
