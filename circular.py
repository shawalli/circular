#!/usr/bin/env python3
import logging

from PIL import Image, ImageDraw
import click
import numpy

logging.basicConfig()
LOGGER = logging.getLogger(__name__)

class Circularizer:
    def __init__(self):
        self.image_handle = None
        self.height = None
        self.width = None
        self.base_layer = None
        self.alpha_layer = None

    def open(self, path):
        LOGGER.info(f'Opening: "{path}"')
        self.image_handle = Image.open(path).convert("RGB")
        self.width, self.height = self.image_handle.size
        LOGGER.info(f"Image dimensions: {self.width} x {self.height}")

    def crop(self, side=None, x_offset=None, y_offset=None):
        max_height = self.height
        if y_offset is not None:
            absolute_offset = min(y_offset, (100 - y_offset))
            max_height = int((float(absolute_offset) / 100) * self.height * 2)

        max_width = self.width
        if x_offset is not None:
            absolute_offset = min(x_offset, (100 - x_offset))
            max_width = int((float(absolute_offset) / 100) * self.width * 2)

        if side is None:
            side = min(max_height, max_width)
        else:
            LOGGER.info(f'Requested size is: {side}')
        final_side = min(max_height, max_width, side)

        if side != final_side:
            LOGGER.warn("Unable to crop to requested size")

        y_offset_start = 0
        y_offset_center = final_side / 2
        y_offset_end = final_side
        if y_offset:
            y_offset_center = int((float(y_offset) / 100) * self.height)
            y_offset_start = y_offset_center - (final_side / 2)
            y_offset_end = y_offset_start + final_side
        LOGGER.debug(f"Calculated starting y-offset to be: {y_offset_start}")
        LOGGER.debug(f"Calculated center y-offset to be:   {y_offset_center}")
        LOGGER.debug(f"Calculated ending y-offset to be:   {y_offset_end}")

        x_offset_start = 0
        x_offset_center = final_side / 2
        x_offset_end = final_side
        if x_offset:
            x_offset_center = int((float(x_offset) / 100) * self.width)
            x_offset_start = x_offset_center - (final_side / 2)
            x_offset_end = x_offset_start + final_side
        LOGGER.debug(f"Calculated starting x-offset to be: {x_offset_start}")
        LOGGER.debug(f"Calculated center x-offset to be:   {x_offset_center}")
        LOGGER.debug(f"Calculated ending x-offset to be:   {x_offset_end}")

        LOGGER.info(f"Calculated image center at: {x_offset_center} x {y_offset_center}")

        LOGGER.info(f"Cropping image to: {final_side} x {final_side}")
        self.image_handle = self.image_handle.crop((x_offset_start, y_offset_start, x_offset_end, y_offset_end))
        self.height, self.width = self.image_handle.size

        LOGGER.debug("Creating base layer from cropped image")
        self.base_layer = numpy.array(self.image_handle)

    def draw_circle(self):
        LOGGER.info("Drawing circle on image")
        LOGGER.debug("Creating alpha image")
        alpha_image = Image.new("L", (self.height, self.width), 0)

        LOGGER.debug("Creating draw layer")
        draw_layer = ImageDraw.Draw(alpha_image)
        LOGGER.debug("Drawing circle")
        draw_layer.pieslice([0, 0, self.height, self.width], 0, 360, fill=255)

        # flatten alpha and draw layers
        LOGGER.debug("Flattening circle into alpha image")
        self.alpha_layer = numpy.array(alpha_image)

    def save(self, path):
        # flatten base and alpha layers
        LOGGER.debug("Flattening alpha image into base layer")
        flattened = numpy.dstack((self.base_layer, self.alpha_layer))

        LOGGER.info(f'Saving circular image to: "{path}"')
        Image.fromarray(flattened).save(path)

@click.command()
@click.argument("path")
@click.option("-v", "--verbose", count=True)
@click.option("--out")
@click.option("--diameter", type=int, default=None)
@click.option("--x-offset", type=int, default=None)
@click.option("--y-offset", type=int, default=None)
def run(path, verbose, out, diameter, x_offset, y_offset):
    if verbose == 1:
        LOGGER.setLevel(logging.INFO)
    elif verbose > 1:
        LOGGER.setLevel(logging.DEBUG)

    if out is None:
        out = path

    circle = Circularizer()
    circle.open(path)
    circle.crop(diameter, x_offset, y_offset)
    circle.draw_circle()
    circle.save(out)

if __name__ == "__main__":
    run()
