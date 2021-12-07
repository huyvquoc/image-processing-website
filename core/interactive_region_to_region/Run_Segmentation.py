# Run segmentation for full image  (In Run_Segmentation.py)
# 1) Train the net or download pre-trained model from:
# 2) Set the path to the pre-trained model in the Trained_model_path parameter
# 3) Set path for test image in the InputImagePath parameter (or leave as is)
# 4) Set path where the output overlay annotation map  in the OutputFile parameter
# 5) Run script

import argparse
import os

import cv2
import torch
import numpy as np
import FCN_NetModel as NET_FCN# The net Class
from PIL import Image
from matplotlib import pyplot as plt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-inp', '--input_path', type=str, required=True, help='path to the input image')
    parser.add_argument('-mp', '--model_path', type=str, required=True, help='path to the trained model')
    parser.add_argument('-oup', '--output_path', type=str, required=True, help='path to the output image')
    args = parser.parse_args()
    
    input_path = args.input_path
    category_paths = []
    for root, dirs, files in os.walk(input_path):
        category_paths.append(root)
    category_paths = category_paths[1:]

    #---------------------Create and Initiate net and create optimizer------------------------------------------------------------------------------------
    Trained_model_path = args.model_path
    print("Loadin model")
    Net=NET_FCN.Net(NumClasses=2) # Create net and load pretrained encoder path
    Net.AddAttententionLayer() # Load attention layer
    Net=Net.cuda()
    Net.load_state_dict(torch.load(Trained_model_path)) # load traine model
    Net.eval()
    print("Model Loaded")

    fig = plt.figure()
    for category_path in category_paths:
        img_names = os.listdir(category_path)
        print(img_names)
        for img_name in img_names:
            #.....................................Input parametrs..................................................................................................................
            InputImagePath = os.path.join(category_path, img_name)
            OutputFile = args.output_path
            os.makedirs(OutputFile.split('/')[1], exist_ok=True)
 
            #----------------------------------------Read image and generate initial ROI mask--------------------------------------------------------------------------------------------------------------
            Im=Image.open(InputImagePath)
            inp = cv2.imread(InputImagePath)
            # Im.show()
            I=np.array(Im)[:,:,0:3]
            H,W,d=I.shape
            I=np.expand_dims(I,0)
            ROIMask=np.ones(I.shape[:3]) # Generate ROI mask that cover the full image
    
            #-------------------------------Start sequential segmentation--------------------------------------------------------------
            for ii in range(100):
                #--------------pick random point in ROI mask----------------------------------------------------
                print("picking next point point")
                while (True):
                    X = np.random.randint(W)
                    Y = np.random.randint(H)
                    if ROIMask[0,Y,X]==1: break
    
                #==============Generate Pointer mask==================================================================================
                PointerMask=np.zeros(ROIMask.shape)
                PointerMask[0, Y, X] = 1
    
                #==============run inference predict segment==================================================================================
                with torch.autograd.no_grad():
                       Prob, PredLb = Net.forward(Images=I, Pointer=PointerMask,ROI=ROIMask)  # Run net inference and get prediction
                PredLb=PredLb.data.cpu().numpy()
                ROIMask[PredLb == 1] = 0 # Remove predicted segment from the ROI mask
    
                #=========== Stiched the predicted segment to full segmentation mask ======================================
                if ii==0:
                    SegViz=np.zeros(I[0].shape,dtype=np.uint8)
                SegViz[:,:, 0] += np.uint8(PredLb[0]*(ii+1)*21%255)
                SegViz[:,:, 1] += np.uint8(PredLb[0]*((ii+1)*67) % 255)
                SegViz[:,:, 2] += np.uint8(PredLb[0]*((ii+1) * 111) % 255)
    
                #============ break when 95% of the image have been segmented =================
                if (ROIMask.sum() / W / H) < 0.05: break
                print(str(ii)+") ROI as fraction of image"+str(ROIMask.sum() / W / H))
    
            #=============== Display and save result =============
            OverLay = (I[0]*0.2+SegViz*0.8).astype(np.uint8)
            disp1 = Image.fromarray(OverLay, 'RGB')
            # disp1.show()
            disp1.save(OutputFile)

            ax1 = fig.add_subplot(2,1,1)
            ax1.title.set_text('Input')
            ax1.imshow(inp)
            ax1.axis('off')

            ax2 = fig.add_subplot(2,1,2)
            ax2.title.set_text('Output')
            ax2.imshow(OverLay)
            ax2.axis('off')

            plt.waitforbuttonpress()
            fig.clf()
            plt.draw()