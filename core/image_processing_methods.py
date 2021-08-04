'''https://stackoverflow.com/questions/33077804/losslessly-compressing-images-on-django/33989023'''

# standard library
from io import BytesIO

# third-party
import cv2
import numpy as np
from PIL import Image, ImageOps

# Django
from django.core.files import File


def compress(
        image):
    im = Image.open(image)
    im_io = BytesIO()
    im.save(
        im_io, 
        'JPEG', 
        quality=70)
    new_image = File(
        im_io, 
        name=image.name)
    return new_image

def trim(
        image, 
        left, top, 
        right, bottom):
    im = Image.open(image)
    im = im.crop((
        left, top, 
        right, bottom))
    im_io = BytesIO()
    im.save(
        im_io, 
        'JPEG', 
        quality=100)
    new_image = File(
        im_io, 
        name=image.name)
    return new_image

def frame(
        image, 
        padding, 
        color):
    im = Image.open(image)
    im_with_border = ImageOps.expand(
        im, 
        border=padding, 
        fill=color)
    im_io = BytesIO()
    im_with_border.save(
        im_io, 
        'JPEG', 
        quality=100)
    new_image = File(
        im_io, 
        name=image.name)
    return new_image

def convert_jpg_to_png(
        image):
    im = Image.open(image)
    im_io = BytesIO()
    im.save(
        im_io, 
        'PNG')
    new_image = File(
        im_io, 
        name=image.name)
    return new_image

def remove_background(
        image, blur, 
        canny_thresh_1, canny_thresh_2, 
        mask_dilate_iter, mask_erode_iter, 
        mask_color):
    #-- Read image -----------------------------------------------------------------------
    pil_img = Image.open(image).convert('RGB')
    img = np.array(pil_img)
    img = img[:, :, ::-1].copy()
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #-- Edge detection -------------------------------------------------------------------
    edges = cv2.Canny(
        gray_img, 
        canny_thresh_1, 
        canny_thresh_2)
    edges = cv2.dilate(edges, None)
    edges = cv2.erode(edges, None)

    #-- Find contours in edges, sort by area ---------------------------------------------
    contour_info = []
    contours, _ = cv2.findContours(
        edges, 
        cv2.RETR_LIST, 
        cv2.CHAIN_APPROX_NONE)
    for c in contours:
        contour_info.append((
            c,
            cv2.isContourConvex(c),
            cv2.contourArea(c),))
    contour_info = sorted(
        contour_info, 
        key=lambda c: c[2], 
        reverse=True)
    max_contour = contour_info[0]

    #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
    # Mask is black, polygon is white
    mask = np.zeros(edges.shape)
    cv2.fillConvexPoly(
        mask, 
        max_contour[0], 
        (255))

    #-- Smooth mask, then blur it --------------------------------------------------------
    mask = cv2.dilate(
        mask, 
        None, 
        iterations=mask_dilate_iter)
    mask = cv2.erode(
        mask, 
        None, 
        iterations=mask_erode_iter)
    mask = cv2.GaussianBlur(
        mask, 
        (blur, blur), 
        0)
    mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask

    #-- Blend masked img into MASK_COLOR background --------------------------------------
    mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
    img         = img.astype('float32') / 255.0                 #  for easy blending

    masked = (mask_stack * img) + ((1-mask_stack) * mask_color) # Blend
    masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit 

    masked = masked[:, :, ::-1].copy()
    pil_masked = Image.fromarray(masked)
    im_io = BytesIO()
    pil_masked.save(
        im_io, 
        'JPEG')
    new_image = File(
        im_io, 
        name=image.name)

    return new_image
