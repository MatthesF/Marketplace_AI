# for a given folder, get all image files
# for each, try opening it with PIL
# if fail, print or delete the file
# the error:
#     UnidentifiedImageError: cannot identify image file [path/to/file]

import os
from PIL import Image
import pathlib
import numpy as np
import matplotlib.pyplot as plt

def try_open(path, delete=False):
    try:
        im = Image.open(path)
        im.close()
    except:
        if delete:
            os.remove(path)
            print(f"Deleted {path}")
        else:
            print(f"Failed to open {path}")
        return False
    return True


def identify_duplicates(im_path, plot=False, verbose=False):
    im_files = [f for f in os.listdir(path=im_path)]
    im_files

    # lets try this!
    ims = {im : {'image' : Image.open(pathlib.Path(im_path,im))} for im in im_files}

    # sort images by aspect ratio
    ims_by_aspect_ratio = {}
    for im in ims:
        size = ims[im]['image'].size
        aspect_ratio = round(size[0] / size[1], 2)
        ims[im]['size'] = size
        ims[im]['aspect_ratio'] = aspect_ratio
        if aspect_ratio not in ims_by_aspect_ratio:
            ims_by_aspect_ratio[aspect_ratio] = [
                {'im_fname' : im,
                'image' : ims[im]['image'],
                'size' : size}
            ]
        else:
            ims_by_aspect_ratio[aspect_ratio] += [
                {'im_fname' : im,
                'image' : ims[im]['image'],
                'size' : size}
            ]


    
    to_delete = []
    try:
        for ar in ims_by_aspect_ratio:
            if verbose:
                print(f'Aspect ratio {ar} has {len(ims_by_aspect_ratio[ar])} images')
            if len(ims_by_aspect_ratio[ar]) > 1:
                min_size = min([ims_by_aspect_ratio[ar][i]['size'][1] for i in range(len(ims_by_aspect_ratio[ar]))])
                if verbose:
                    print(f'Min size is {min_size}')
                    print(ims_by_aspect_ratio[ar])

                # downsample all images to the smallest size
                im_arrays = {im['im_fname'] : np.array(im['image'].resize((int(min_size*ar), min_size)))/255 for im in ims_by_aspect_ratio[ar]}

                if plot:
                    fig, ax = plt.subplots(1, len(im_arrays), figsize=(20, 3))
                    for i, im in enumerate(im_arrays):
                        ax[i].imshow(im_arrays[im])
                        ax[i].axis('off')
                        ax[i].set_title(im)
                    plt.show()


                sim_matrix = np.zeros((len(im_arrays), len(im_arrays)))
                for i, im_i in enumerate(im_arrays):
                    for j, im_j in enumerate(im_arrays):
                        sim_matrix[i, j] = np.mean((im_arrays[im_i] - im_arrays[im_j])**2)
                    
                if verbose:
                    print(np.round(sim_matrix, 4))
            
                same = np.argwhere(sim_matrix < 0.01)
                same_cleaned = []
                for s in same:
                    if s[0] == s[1]:
                        continue
                    if (s[1], s[0]) in same_cleaned:
                        continue
                    if (s[0], s[1]) in same_cleaned:
                        continue
                    same_cleaned.append((s[0], s[1]))
                if verbose:
                    print(same_cleaned)

                for s in same_cleaned:
                    im1_fname = ims_by_aspect_ratio[ar][s[0]]['im_fname']
                    im2_fname = ims_by_aspect_ratio[ar][s[1]]['im_fname']
                    # check which is bigger
                    im1_size = ims[im1_fname]['size']
                    im2_size = ims[im2_fname]['size']
                    if verbose:
                        print(f'image {im1_fname} has size', im1_size, f'image {im2_fname} has size', im2_size)
                    if im1_size[0] > im2_size[0]:
                        to_delete.append(ims_by_aspect_ratio[ar][s[1]]['im_fname'])
                    else:
                        to_delete.append(ims_by_aspect_ratio[ar][s[0]]['im_fname'])
                # print(to_delete)

    except Exception as e:
        print(f'Error: {e}')
        return set(to_delete)
    
    return set(to_delete)
            

def broken_images(base_path = 'content', delete=False, verbose=False):  # TODO: the for folder in folder stuff and above should be common, the rest can be a separate function
    sources = os.listdir(base_path)
    print('Broken files and duplicates will be ' + ('deleted' if delete else 'printed only'))
    total_number_of_duplicates = 0
    total_number_of_images = 0
    for source in sources:
        if '.' in source:
            continue
        folders = os.listdir(pathlib.Path(base_path,source))
        print(f'For source {source}, found {len(folders)} folders: {folders}')

        for folder in folders:
            path = pathlib.Path(base_path,source,folder)
            im_path  = pathlib.Path(path,'images')

            im_files = [f for f in os.listdir(im_path) ]  #if f.endswith('.jpg')
            total_number_of_images += len(im_files)

            for f in im_files:
                try_open(pathlib.Path(im_path,f), delete=delete)


            to_del = identify_duplicates(im_path)
            if len(to_del) > 0:
                if verbose:
                    print(f'Found {len(to_del)} duplicates in {im_path}')
                total_number_of_duplicates += len(to_del)
                print(f'Duplicates in {im_path}: {to_del}')
                if delete:
                    for f in to_del:
                        os.remove(pathlib.Path(im_path,f))
                        if verbose:
                            print(f"Deleted {total_number_of_duplicates} so far", end='\r')

            # break
        # break

    print(f'Total number of duplicates: {total_number_of_duplicates}')
    print(f'Total number of images: {total_number_of_images}')

        