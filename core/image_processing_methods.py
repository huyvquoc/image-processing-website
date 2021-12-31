'''https://stackoverflow.com/questions/33077804/losslessly-compressing-images-on-django/33989023'''

# standard library
import os
from io import BytesIO

# third-party
import cv2
import numpy as np
from PIL import Image, ImageOps
from matplotlib import pyplot as plt

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

def crop_polygons(img_obj_url, list_of_polygons, height, width):
    img = cv2.imread(img_obj_url)
    img = cv2.resize(img, (width, height))
    # pts = np.array([[10,150],[150,100],[300,150],[350,100],[310,20],[35,10]])
    contours = []
    for idx, polygon in enumerate(list_of_polygons):
        contour = []
        for point in polygon:
            coordinate = [point["y"], point["x"]]
            contour.append(coordinate)
        # pts = np.array(pts)
        contours.append(contour)
        # print('pts ' + str(idx) + ': ', pts)
    
        ## (1) Crop the bounding rect
        # rect = cv2.boundingRect(pts)
        # x,y,w,h = rect
        # croped = img[y:y+h, x:x+w].copy()
        
        ## (2) make mask
        # pts = pts - pts.min(axis=0)
        
    contours = np.array(contours)
    print(contours)
    mask = np.zeros(img.shape[:2], np.uint8)
    cv2.drawContours(mask, [contours], -1, (255, 255, 255), -1, cv2.LINE_AA)
    
    ## (3) do bit-op
    dst = cv2.bitwise_and(img, img, mask=mask)
    
    ## (4) add the white background
    # bg = np.ones_like(croped, np.uint8)*255
    # cv2.bitwise_not(bg,bg, mask=mask)
    # dst2 = bg+ dst
    
    
    cv2.imwrite("input.png", img)
    cv2.imwrite("mask.png", mask)
    cv2.imwrite("dst.png", dst)
    # cv2.imwrite("dst2.png", dst2)
    dst = dst[:, :, ::-1].copy()
    pil_dst = Image.fromarray(dst)
    im_io = BytesIO()
    pil_dst.save(
        im_io, 
        'JPEG')
    new_image = File(
        im_io, 
        name="output_img.jpg")

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

def watershed_segmentation(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    # noise removal
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 2)
    # sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0

    markers = cv2.watershed(image, markers)
    image[markers == -1] = [255,0,0]

    return gray, thresh, opening, sure_bg, dist_transform, sure_fg, unknown, markers, image

if __name__ == "__main__":
    input_path = "/media/data-huy/Segmentation/images"

    category_paths = []
    for root, dirs, files in os.walk(input_path):
        category_paths.append(root)
    category_paths = category_paths[1:]

    fig = plt.figure()
    for category_path in category_paths:
        img_names = os.listdir(category_path)
        print(img_names)
        for img_name in img_names:
            img_path = os.path.join(category_path, img_name)
            print('[*] img_path', img_path)
            # inp = Image.open(img_path)
            inp = cv2.imread(img_path)
            gray, thresh, opening, sure_bg, dist_transform, sure_fg, unknown, markers, image = watershed_segmentation(inp)

            ax1 = fig.add_subplot(3,3,1)
            ax1.title.set_text('Gray input')
            ax1.imshow(gray)
            ax1.axis('off')

            ax2 = fig.add_subplot(3,3,2)
            ax2.title.set_text('Threshold')
            ax2.imshow(thresh)
            ax2.axis('off')

            ax3 = fig.add_subplot(3,3,3)
            ax3.title.set_text('Opening')
            ax3.imshow(opening)
            ax3.axis('off')

            ax4 = fig.add_subplot(3,3,4)
            ax4.title.set_text('Sure background')
            ax4.imshow(sure_bg)
            ax4.axis('off')

            ax5 = fig.add_subplot(3,3,5)
            ax5.title.set_text('Distance transform')
            ax5.imshow(dist_transform)
            ax5.axis('off')

            ax2 = fig.add_subplot(3,3,6)
            ax2.title.set_text('Sure foreground')
            ax2.imshow(sure_fg)
            ax2.axis('off')

            ax3 = fig.add_subplot(3,3,7)
            ax3.title.set_text('Unknown regions')
            ax3.imshow(unknown)
            ax3.axis('off')

            ax4 = fig.add_subplot(3,3,8)
            ax4.title.set_text('Markers')
            ax4.imshow(markers)
            ax4.axis('off')

            ax5 = fig.add_subplot(3,3,9)
            ax5.title.set_text('Output image')
            ax5.imshow(image)
            ax5.axis('off')

            plt.waitforbuttonpress()
            fig.clf()
            plt.draw()
