import itertools
import multiprocessing
import os
import random
import re
from collections import defaultdict
from functools import partial

import numpy
from PIL import Image
from scipy.spatial import distance


def get_tiles(file_paths):
    color_re = re.compile(r'.+_([0-9a-f]{6})\..+')
    tiles = defaultdict(list)
    for file_path in file_paths:
        match = re.match(color_re, file_path)
        if match:
            key = tuple(int(c, 16) for c in re.findall(r'..', match.group(1)))
            tiles[key].append(file_path)

    return tiles


def get_best_matching_tile(tiles, color):
    return random.choice(tiles[sorted(
        tiles.keys(),
        key=partial(distance.euclidean, color)
    )[0]])


def get_tile_thumb(tiles, data_dir, img, pos):
    x, y = pos
    pixels = numpy.array(img.crop((x, y, x+20, y+20)).getdata())
    mean_color = tuple(numpy.mean(pixels, axis=0))

    tile_filename = get_best_matching_tile(tiles, mean_color)
    tile = Image.open(os.path.join(data_dir, tile_filename))
    return tile.resize((20, 20))


def build(image, data_dir, output):
    img = Image.open(image)

    width, height = img.size
    mosaic_width = round(width / 20) * 20
    mosaic_height = round(height / 20) * 20
    mosaic = Image.new('RGB', (mosaic_width, mosaic_height))
    mosaic.paste(img, (0, 0, width, height))

    positions = list(itertools.product(range(0, width, 20),
                                       range(0, height, 20)))

    tiles = get_tiles(os.listdir(data_dir))

    with multiprocessing.Pool(processes=4) as pool:
        tile_thumbs = pool.map(partial(get_tile_thumb, tiles, data_dir, img),
                               positions)

    for tile, pos in zip(tile_thumbs, positions):
        mosaic.paste(tile, pos)
    mosaic.save(output)
