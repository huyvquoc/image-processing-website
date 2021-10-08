import os
import time

import cv2
import numpy as np

from torchvision import models
import torchvision.transforms as T
from PIL import Image
import matplotlib.pyplot as plt
import torch


def decode_seg_map(image, nc=21):
    label_colors = np.array([(0, 0, 0), # 0=background
                            # 1=aeroplane, 2=bicycle, 3=bird, 4=boat, 5=bottle
                            (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
                            # 6=bus, 7=car, 8=cat, 9=chair, 10=cow
                            (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0), (64, 128, 0),
                            # 11=dining table, 12=dog, 13=horse, 14=motorbike, 15=person
                            (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128), (192, 128, 128),
                            # 16=potted plant, 17=sheep, 18=sofa, 19=train, 20=tv/monitor
                            (0, 64, 0), (128, 64, 0), (0, 192, 0), (128, 192, 0), (0, 64, 128)])

    r = np.zeros_like(image).astype(np.uint8)
    g = np.zeros_like(image).astype(np.uint8)
    b = np.zeros_like(image).astype(np.uint8)

    for cls_label in range(0, nc):
        idxs = image == cls_label
        r[idxs] = label_colors[cls_label, 0]
        g[idxs] = label_colors[cls_label, 1]
        b[idxs] = label_colors[cls_label, 2]

    # stack 3 channels
    rgb = np.stack([r, g, b], axis=2)
    return rgb

def foreground_background_preprocess(color_seg_map, src_img, bg_img, type_of_process='remove-background'):
    foreground = cv2.imread(src_img)
    foreground = cv2.cvtColor(foreground, cv2.COLOR_BGR2RGB)
    foreground = cv2.resize(foreground, (color_seg_map.shape[1], color_seg_map.shape[0]))

    if type_of_process == 'blur-background':
        background = cv2.GaussianBlur(foreground, (7, 7), 0)
    elif type_of_process == 'remove-background':
        background = 255 * np.ones_like(color_seg_map).astype(np.uint8)
    elif type_of_process == 'change-background':
        background = cv2.imread(bg_img)
        background = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
        background = cv2.resize(background, (color_seg_map.shape[1], color_seg_map.shape[0]))
    elif type_of_process == 'grayscale-background':
        background = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)
        background = cv2.cvtColor(background, cv2.COLOR_GRAY2RGB)

    foreground = foreground.astype(float)
    background = background.astype(float)

    th, alpha = cv2.threshold(np.array(color_seg_map), 0, 255, cv2.THRESH_BINARY)

    alpha = cv2.GaussianBlur(alpha, (7, 7), 0)

    alpha = alpha.astype(float)/255

    foreground = cv2.multiply(alpha, foreground)
    background = cv2.multiply(1.0 - alpha, background)

    outImage = cv2.add(foreground, background)

    return outImage/255



def segmentation_then_process(network, input_path, background_path=None, type_of_process='remove-background', show_orig=True, dev='cuda'):
    img = Image.open(input_path)

    if show_orig:
        plt.imshow(img)
        plt.axis('off');
        plt.show()

    transformations = T.Compose([T.Resize(640),
                     # T.CenterCrop(224),
                     T.ToTensor(),
                     T.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])])

    transformed_img = transformations(img).unsqueeze(0).to(dev)
    output_segmentation = network.to(dev)(transformed_img)['out']
    print('[**] output_segmentation: ', output_segmentation.shape)
    output_seg_map = torch.argmax(output_segmentation.squeeze(), dim=0).detach().cpu().numpy()
    print('[**] output_seg_map.shape: ', output_seg_map.shape)
    print('[**] np.unique(output_seg_map): ', np.unique(output_seg_map))
    color_seg_map = decode_seg_map(output_seg_map)
    output_img = foreground_background_preprocess(color_seg_map, input_path, background_path, type_of_process)

    return output_img

if __name__ == "__main__":
    fcn = models.segmentation.fcn_resnet101(pretrained=True).eval()
    dlab = models.segmentation.deeplabv3_resnet101(pretrained=1).eval()

    input_path = "/media/data-huy/Segmentation/images"
    background_path = "/media/data-huy/Segmentation/images/sea/sea1.jpg"
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
            inp = Image.open(img_path)
            out1 = segmentation_then_process(fcn, img_path, type_of_process='blur-background', show_orig=False)
            out2 = segmentation_then_process(fcn, img_path, type_of_process='remove-background', show_orig=False)
            out3 = segmentation_then_process(fcn, img_path, background_path, type_of_process='change-background', show_orig=False)
            out4 = segmentation_then_process(fcn, img_path, type_of_process='grayscale-background', show_orig=False)


            ax1 = fig.add_subplot(1,5,1)
            ax1.title.set_text('Input')
            ax1.imshow(inp)
            ax1.axis('off')

            ax2 = fig.add_subplot(1,5,2)
            ax2.title.set_text('Blur background')
            ax2.imshow(out1)
            ax2.axis('off')

            ax3 = fig.add_subplot(1,5,3)
            ax3.title.set_text('Remove background')
            ax3.imshow(out2)
            ax3.axis('off')

            ax4 = fig.add_subplot(1,5,4)
            ax4.title.set_text('Change background')
            ax4.imshow(out3)
            ax4.axis('off')

            ax5 = fig.add_subplot(1,5,5)
            ax5.title.set_text('Grayscale background')
            ax5.imshow(out4)
            ax5.axis('off')

            plt.waitforbuttonpress()
            fig.clf()
            plt.draw()

    # segmentation_then_process(dlab, "/media/data-huy/Segmentation/images/car/car2.jpg")

    # segmentation_then_process(fcn, "/media/data-huy/Segmentation/images/outdoor/person-segmentation.jpeg", background_path)

    # segmentation_then_process(dlab, "/media/data-huy/Segmentation/images/outdoor/person-segmentation.jpeg", background_path)