import cv2
import numpy as np
import os.path

def PreProcessImage(in_path:str, out_path:str):

    #Read the image
    img = cv2.imread(in_path)

    ### for the cameras on the edge of the membrane we want to keep only the membrane, so crop anything outside of it
    # Detect edges using Canny method
    blurred = cv2.blur(img, (3,3))
    edges = cv2.Canny(blurred, 150, 300)

    pts = np.argwhere(edges>0)
    y1,x1 = pts.min(axis=0)
    y2,x2 = pts.max(axis=0)


    ### Increase the contrast of the image to highlight features ###
    lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)

    # Applying CLAHE to L-channel
    # feel free to try different values for the limit and grid size:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)

    # merge the CLAHE enhanced L-channel with the a and b channel
    limg = cv2.merge((cl,a,b))
    cropped = limg[y1:y2, x1:x2]

    # Converting image from LAB Color model to BGR color spcae
    enhanced_img = cv2.cvtColor(cropped, cv2.COLOR_LAB2BGR)


    ### Pass the images through a sobel filter for feature extraction ###
    ksize = 0
    gX = cv2.Sobel(enhanced_img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=ksize)
    gY = cv2.Sobel(enhanced_img, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=ksize)

    # the gradient magnitude images are now of the floating point data
    # type, so we need to take care to convert them back a to unsigned
    # 8-bit integer representation so other OpenCV functions can operate
    # on them and visualize them
    gX = cv2.convertScaleAbs(gX)
    gY = cv2.convertScaleAbs(gY)

    # combine the gradient representations into a single image
    combined = cv2.addWeighted(gX, 0.5, gY, 0.5, 0)


    cv2.imwrite(out_path, combined)

    file_exists = os.path.exists("readme.txt")

    if file_exists:
        return 1
    return 0