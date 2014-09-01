from cStringIO import StringIO
from PIL import Image


def crop_and_scale(image, size, aoi=None):
    ow, oh = image.size
    ratio = float(size[0]) / float(size[1])

    # Find center of aoi (Area Of Interest):
    if aoi:
        x1, y1, x2, y2 = map(float, aoi)
        old_ratio = 0
    else:
        x1, y1, x2, y2 = 0.0, 0.0, 1.0, 1.0
        old_ratio = float(ow) / float(oh)
    centerX = (x2 + x1) * ow / 2
    centerY = (y2 + y1) * oh / 2

    # Define (dx, dy), the crop boundaries:
    if (aoi and ratio < 1) or (old_ratio and ratio > old_ratio):
        # portrait
        dx = (x2 - x1) * ow / 2
        dy = dx / ratio
    elif (aoi and ratio > 1) or (old_ratio):
        # landscape
        dy = (y2 - y1) * oh / 2
        dx = dy * ratio
    else:
        # square, using the 16:9 height as boundary
        dx = (x2 - x1) * ow / 2 / 9 * 16
        dy = dx

    # Define the crop bounding box:
    dx1 = centerX - dx
    dy1 = centerY - dy
    dx2 = centerX + dx
    dy2 = centerY + dy

    # Shift crop bounding box to fit within source image:
    if dx1 < 0:
        dx2 = min(dx2 - dx1, ow)
        dx1 = 0
    if dx2 > ow:
        dx1 = max(dx1 - (dx2 - ow), 0)
        dx2 = ow
    if dy1 < 0:
        dy2 = min(dy2 - dy1, oh)
        dy1 = 0
    if dy2 > oh:
        dy1 = max(dy1 - (dy2 - oh), 0)
        dy2 = oh

    return image.crop(map(int, (dx1, dy1, dx2, dy2))).resize(size, Image.ANTIALIAS)


def resize(image, sizes, aoi=None, save_to_buffer=False):
    if not isinstance(image, Image.Image):
        image = Image.open(image)
    if image.mode not in ('RGB', 'RGBA'):
        image = image.convert('RGBA')

    if save_to_buffer and not isinstance(save_to_buffer, basestring):
        save_to_buffer = image.format

    resized = []
    for size in sizes:
        try:
            label, (w, h) = size
        except TypeError:
            w, h = label = size

        resized_img = crop_and_scale(image, (w, h), aoi)
        if save_to_buffer:
            buf = StringIO()
            resized_img.save(buf, format=save_to_buffer, quality=90)
            buf.seek(0)
            resized.append((label, buf))
        else:
            resized.append((label, resized_img))

    return resized
