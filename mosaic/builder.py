import os
import random
import re
from collections import defaultdict
from functools import partial

from PIL import Image
from scipy.spatial import distance


def get_tiles(file_paths):
    color_re = re.compile(r'.+_([0-9a-f]{6})\..+')
    tiles = defaultdict(list)
    for file_path in file_paths:
        match = re.match(color_re, file_path)
        if not match:
            continue

        key = tuple(int(c, 16) for c in re.findall(r'..', match.group(1)))
        tiles[key].append(file_path)

    return tiles


def get_best_matching_tile(tiles, color):
    return random.choice(tiles[sorted(
        tiles.keys(),
        key=partial(distance.euclidean, color)
    )[0]])


def build(image, data_dir, output):
    img = Image.open(image)
    tiles = get_tiles(os.listdir(data_dir))
