import numpy as np
import nibabel as nib
from tqdm import tqdm   
import utils as utils
import cv2

def resize_image(image, target_shape):
    """Resize image to the target shape using OpenCV."""
    return cv2.resize(image, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_LINEAR)

def to_channels ( arr : np.ndarray, dtype = np.uint8) -> np.ndarray :
    channels = np . unique ( arr )
    res = np.zeros(arr.shape + (len(channels),), dtype = dtype)
    for c in channels :
        c = int(c)
        res [... , c : c + 1][arr == c] = 1

    return res

# load medical image functions
def load_data_2D(imageNames, normImage=False, categorical=False, dtype=np.float32, getAffines=False, early_stop=False):
    '''
    Load medical image data from names , cases list provided into a list for each.

    This function pre - allocates 4D arrays for conv2d to avoid excessive memory &usage.

    normImage : bool ( normalise the image 0.0 -1.0)
    early_stop : Stop loading pre - maturely , leaves arrays mostly empty , for quick &
        loading and testing scripts.
    '''
    
    affines = []
    num = len(imageNames)
    first_case = nib.load(imageNames[0]).get_fdata(caching='unchanged')
    if len(first_case.shape) == 3:
        first_case = first_case[:, :, 0]  # remove extra dims if necessary
    if categorical:
        first_case = to_channels(first_case, dtype=dtype)
        rows, cols, channels = first_case.shape
        images = np.zeros((num, rows, cols, channels), dtype=dtype)
    else:
        rows, cols = first_case.shape
        images = np.zeros((num, rows, cols), dtype=dtype)

    for i, inName in enumerate(tqdm(imageNames)):
        niftiImage = nib.load(inName)
        inImage = niftiImage.get_fdata(caching='unchanged')
        affine = niftiImage.affine
        if len(inImage.shape) == 3:
            inImage = inImage[:, :, 0]  # remove extra dims if necessary
        inImage = inImage.astype(dtype)
        
        # Resize the image if necessary
        if inImage.shape != (rows, cols):
            inImage = resize_image(inImage, (rows, cols))
        
        if normImage:
            inImage = (inImage - inImage.mean()) / inImage.std()
        
        if categorical:
            inImage = utils.to_channels(inImage, dtype=dtype)
            images[i, :, :, :] = inImage
        else:
            images[i, :, :] = inImage
        
        affines.append(affine)
        if i > 20 and early_stop:
            break

    if getAffines:
        return images, affines
    else:
        return images