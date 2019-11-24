# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 08:10:50 2018
"""

#import python libraries
import cv2
import random
import numpy
import copy
import os
import json
import time


#import shared modules
from . import opencv_fun as opencv_fun

# import json file path
from biometric_app_site.settings import JSON_ROOT


def edge_optimized(image, shapes, permutations_min, permutations_max, quality_min):
    
    """
    DESCRIPTION
    This function can be used to locate a specified target shape in an image 
    using an adaptive thresholding process. It shifts through a range of 
    different thresholding parameters to find one which locates the target 
    shape. Two memory files are used by this function. One stores successful 
    thresholding parameter sets and the other stores a dictionary of contours 
    for each shape type.
    
    To use this function:
    1. Add the shape to memory files (only needed for new shapes)
    2. Call function and define which shape you are searching for
    
    INPUT
    image = an image in standard opencv format (colour)
    shapes = a list of contour names of interest ["snapper", "ruler"]
    permutations_min = the minimum number of permutations
    permutations_max = the maximum number of permutations
    quality_min = the minimum quality required to return (suggested = 1.5) 
    
    OUTPUT
    best_contour = the best matching contour
    best_value = the match value for the returned contour
    best_overlap = the overlap value for the returned contour
    best_contrast = the contrast value for the returned contour
    """

    #define the memory location
    memory_contour_file = JSON_ROOT + '/memory_contours.json' 
    memory_shapes_file = JSON_ROOT + '/memory_shapes.json' 
    print(memory_contour_file)
    
    #load memory files
    while True:
        try:
            with open(memory_contour_file, 'r') as f:
                print(1)
                print(f)
                print(json.load(f))
                contourMemory = json.load(f) 
               
            with open(memory_shapes_file, 'r') as f:
                print(2)
                shapeMemory = json.load(f)  
                
            print(3)
            break
        except:
            print('failed to load memory1: edge_optimized')
            #wait for a few seconds
            time.sleep(random.randint(1,5))

    #determine the background color
    background_values, background_channel = opencv_fun.image_background(image)
    
    #generate a greyscale image
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

    #initialize starting return objects
    best_value = 0
    best_contour = None
    method_used = None
    best_overlap = None
    best_contrast = None
    
    #try find shape for set number of permutations
    for x in range(permutations_max):
        #select a shape type from the shape_names which it should be compared to
        shapeType = random.choice(shapes)
        #selet which version to run: existing or new parameter set
        if shapeType in contourMemory:
            version = random.uniform(0,1)
        else:
            version = 0            
        #generate contours with selected version
        if version < 0.25:            
            #generate new random parameters
            parameters = generate_edge_parameters()            
            #locate contours using relevant edge detection method colour edge detection
            if parameters['selection'] == 'simple_grey':
                contours = edge_simple_grey(image_grey, parameters) 
            if parameters['selection'] == 'simple_colour':
                contours = edge_simple_colour(image, parameters)                
            #search for a specific shape in the contours
            shape = random.choice([x for x in shapeMemory[shapeType]])           
            #get the contour for the target shape
            target_shape = shapeMemory[shapeType][shape]           
            #find matching contour
            new_contour, new_value, new_overlap, new_contrast = identify_contour(image, contours, target_shape, background_channel, quality_min)                 
        else:
            #select parameters from memory
            parameters = random.choice(contourMemory[shapeType])['contour_method']
            shape = parameters['shape']
            parameters = parameters['parameters']
            #run the selected edge detection method
            if parameters['selection'] == 'simple_grey':
                contours = edge_simple_grey(image_grey, parameters) 
            if parameters['selection'] == 'simple_colour':
                contours = edge_simple_colour(image, parameters)               
            #select the target shape
            target_shape = shapeMemory[shapeType][shape]                
            #find matching contour
            new_contour, new_value, new_overlap, new_contrast = identify_contour(image, contours, target_shape, background_channel, quality_min)            
        #check if a suitable method has been found to return
        if new_contour is not None:
            #update the method used
            method_used = {'parameters': parameters, 'shape_type':shapeType,
                          'shape':shape, 'quality1': new_overlap,
                          'quality2': new_contrast}            
            #update best_method or return
            if new_value > best_value:
                best_value = new_value
                best_contour = new_contour
                best_overlap = new_overlap
                best_contrast = new_contrast            
            #break if past quality and permutations limit
            if best_value >= quality_min:
                if x >= permutations_min:
                    break     
    #add method to memory
    if method_used is not None:
        memoryUnit = {'contour_method': method_used}
        try:
            if len(contourMemory[method_used['shape_type']]) < 1000:
               contourMemory[method_used['shape_type']] += [memoryUnit]
            else:
               del contourMemory[method_used['shape_type']][0]
               contourMemory[method_used['shape_type']] += [memoryUnit]
        except:
            contourMemory[method_used['shape_type']] = [memoryUnit]            
    #save updated memory
    while True:
        try:
            with open(memory_contour_file, 'w') as f:
                json.dump(contourMemory, f)
            break
        except:
            print('failed to save memory2: edge_optimized')
            #wait for a few seconds
            time.sleep(random.randint(1,5))
            
    #return best_match
    if best_value is not None:
        return best_contour, best_value, best_overlap, best_contrast


def generate_edge_parameters():
    
    """
    DESCRIPTION
    This function generates a new set of parameters to use in an edge 
    detection event. It generates completely random set of values for each 
    parameter between a minimum and maximum range.
    
    INPUT
    None
    
    OUTPUT
    parameters = A dictionary containing the new parameter set
    """

    #select a edge detection method from mutation guide
    selection = random.choice(['simple_grey', 'simple_colour'])
    
    #generate parameters for simple_grey method if needed
    if selection == 'simple_grey':        
        parameters = {}
        parameters['selection'] = 'simple_grey'
        parameters['clahe'] = random.choice([True, False])
        parameters['clahe_clip'] = (random.randint(1, 10))
        parameters['clahe_tile'] = random.randint(4, 50)
        parameters['blur_gaussian'] = random.choice([True, False])
        parameters['gaussian_kernel'] = random.randrange(3, 50, 2)
        parameters['blur_median'] = random.choice([True, False])
        parameters['median_kernel'] = random.randrange(3, 50, 2) 
        parameters['dil_ero'] = random.choice([True, False])
        parameters['de_steps'] = random.randint(1,1)
        parameters['de_kernel'] = random.randint(1, 30) 
        parameters['adaptive'] = random.choice([True, False])
        parameters['thresh_1'] = random.choice(range(3, 254, 2))
        parameters['thresh_2'] = random.choice(range(parameters['thresh_1']+1, 255, 2))  
           
    #generate parameters for simple_colour method if needed
    if selection == 'simple_colour':
        parameters = {}
        parameters['selection'] = 'simple_colour'
        parameters['clahe'] = random.choice([True, False])
        parameters['clahe_clip'] = random.randint(1, 10)
        parameters['clahe_tile'] = random.randint(4, 50)
        parameters['blur_gaussian'] = random.choice([True, False])
        parameters['gaussian_kernel'] = random.randrange(3, 50, 2)
        parameters['blur_median'] = random.choice([True, False])
        parameters['median_kernel'] = random.randrange(3, 50, 2) 
        parameters['dil_ero'] = random.choice([True, False])
        parameters['de_steps'] = random.randint(1, 1)
        parameters['de_kernel'] = random.randint(1, 30) 
        parameters['thresh_1'] = [random.randint(0, 254),
                                  random.randint(0, 254),
                                  random.randint(0, 254)]
        parameters['thresh_2'] = [random.randint(parameters['thresh_1'][0], 255),
                                  random.randint(parameters['thresh_1'][1], 255),
                                  random.randint(parameters['thresh_1'][2], 255)]    
    #return parameters
    return parameters
    

def edge_simple_grey(img, parameters):
    
    """
    DESCRIPTION
    This function implements threshold based edge detection to find objects in
    a greyscale image.
    
    INPUT
    img = a greyscale image
    parameters = a dictionary of parameters for this function
    
    OUTPUT
    contours = a standard OPENCV contour object    
    """
    
    #run clahe histogram equalization
    if parameters['clahe'] is True:
        clahe = cv2.createCLAHE(clipLimit=parameters['clahe_clip'], 
                                tileGridSize=(parameters['clahe_tile'], 
                                              parameters['clahe_tile']))
        img = clahe.apply(img) 
    #gaussian blur
    if parameters['blur_gaussian'] is True:
        gaussian_kernel = (parameters['gaussian_kernel'], 
                           parameters['gaussian_kernel'])
        img = cv2.GaussianBlur(img, gaussian_kernel, 0)
    #median blur   
    if parameters['blur_median'] is True:
        median_kernel = parameters['median_kernel']
        img = cv2.medianBlur(img, median_kernel)
    #threshold image
    if parameters['adaptive'] is True:
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY_INV, parameters['thresh_1'], 
                                    parameters['thresh_2'])
    else:
        ret, img = cv2.threshold(img,parameters['thresh_1'], 
                                 parameters['thresh_2'], cv2.THRESH_BINARY_INV)
    #run dilution and erosion steps
    if parameters['dil_ero'] is True:
        de_steps = parameters['de_steps']
        de_kernel = numpy.ones([parameters['de_kernel'],
                             parameters['de_kernel']], numpy.uint8)    
        img = cv2.dilate(img, de_kernel, de_steps)
        img = cv2.erode(img, de_kernel, de_steps) 
    #generate contours and return                    
    contours,hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, 2) 
    #return        
    return contours

    
def edge_simple_colour(img, parameters):
    
    """
    DESCRIPTION
    This function implements threshold based edge detection to find objects in 
    a colour image.
    
    INPUT
    img = a colour image
    parameters = a dictionary of parameters for this function
    
    OUTPUT
    contours = a standard OPENCV contour object
    """
    
    #clahe histogram equalization
    if parameters['clahe'] is True:
        clip_limit = parameters['clahe_clip']
        clahe_tile = parameters['clahe_tile']
        img = opencv_fun.colour_clahe(img, clip_limit, clahe_tile)    
    #gaussian blur
    if parameters['blur_gaussian'] is True:
        gaussian_kernel = (parameters['gaussian_kernel'], 
                           parameters['gaussian_kernel'])
        img = cv2.GaussianBlur(img, gaussian_kernel, 0)
    #median blur   
    if parameters['blur_median'] is True:
        median_kernel = parameters['median_kernel']
        img = cv2.medianBlur(img, median_kernel)
    #convert frame to hsv color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)       
    #threshold the HSV image to specified
    mask = cv2.inRange(hsv, numpy.array(parameters['thresh_1']), numpy.array(parameters['thresh_2'])) 
    #run dilution and erosion steps
    if parameters['dil_ero'] is True:
        de_steps = parameters['de_steps']
        de_kernel = numpy.ones([parameters['de_kernel'],
                             parameters['de_kernel']], numpy.uint8)    
        img = cv2.dilate(img, de_kernel, de_steps)
        img = cv2.erode(img, de_kernel, de_steps)    
    #generate contours
    contours ,hierarchy = cv2.findContours(copy.deepcopy(mask), 1,2)      
    #return contours
    return contours


def identify_contour(image, contours, target_shape, background_channel, quality_min):
    
    """
    DESCRIPTION
    This function searches through a contour list for a specific object. It 
    uses an input shape as a template to determine if any contour is a match, 
    based on the level of overlap with the template. This function also uses 
    the contrast between the object and the background of the image as a 
    measure of quality (assumes consistent background). Consequently, it is 
    only useful for objects in standardized images. The formula dictionary at 
    the start defines the weighting of the overlap and background contrast 
    measures of quality.
    
    THE WEIGHTING IN THE FORMULA DICTIONARY STILL NEED TO BE ADJUSTED
    
    INPUT
    image = an image in standard opencv format (colour or greyscale)
    contours = a standard OPENCV contour set
    shape = a shape template you are looking for
    background_channel = the channel of the background
    quality = the quality of contour match which is required
    
    OUTPUT
    best_contour = the best contour found or first contour to pass quality_min
    best_value = the quality of returned contours
    overlap = the overlap of returned contours
    contrast = the hsv contrast of returned contours
    """

    #set channel specific formulas for combined score
    formula = {0: {"overlap": 1.2, "contrast": 0.35},#Blue
               1: {"overlap": 1.1, "contrast": 0.40},#Green
               2: {"overlap": 1.1, "contrast": 0.40},#Red
               None: {"overlap": 1.3,"contrast": 0.004}}#GreyScale
    
    #initialize best_contour and best value
    best_contour = None
    best_value = 0
    overlap = 0
    contrast = 0    
    
    #loop through each contour and evaluate match...break if quality_min is reached
    for contour in contours:
        #apply a minimum area filter >>> improves performance
        if cv2.contourArea(contour) < 4000:
            continue
        #align the target shape to the contour
        aligned_ref_contour = opencv_fun.align_contours(contour, target_shape, 'two')
        #if alignment was successful check quality of match
        if aligned_ref_contour is not None:
            #calculated overlap
            overlap = opencv_fun.contours_overlap(contour, aligned_ref_contour)
            #calculated difference from background
            contrast = opencv_fun.contour_contrast_multi(image, background_channel, contour)
            #calculated adjusted overlap
            overlap_adjusted = (1-overlap)*formula[background_channel]['overlap']
            #calculated adjusted contrast
            contrast_adjusted = contrast*(formula[background_channel]['contrast'])
            #create a combined quality score
            combined = overlap_adjusted + contrast_adjusted         
            #is past the quality_min break and return
            if combined >= quality_min:
                best_contour = contour
                best_value = combined
                break
    #return   
    return best_contour, best_value, overlap, contrast 


def load_shapes(dir_main, file_out):
    
    """
    DESCRIPTION
    This function loops through all subfolders in the main directory and 
    generates a dictionary of shapes from each image folder. These shapes are
    then used by object detection functions.
    
    INPUT
    dir_main = the location of the shape training dataset
    file_out = the output file path
    
    OUTPUT
    a dictionary containing the shapes is saved to file_out in a JSON format
    """
    
    #set up main dictionary
    main_dict = {}
    #loop through each folder of shapes    
    for folder in os.listdir(dir_main):
        print('generating shapes for: %s' % (folder))
        #loop through each image in the folder
        for image in os.listdir(dir_main + '/' + folder):
            #open image
            img = cv2.imread(dir_main + '/' + folder + '/' + image)
            #convert to greyscale image
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #threshold to get black outline
            ret,thresh = cv2.threshold(img, 5, 255, cv2.THRESH_BINARY_INV)
            contour,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 2)
            #select the largest shape in the contours list
            shape = None
            largest = 0
            for x in contour:
                area = cv2.contourArea(x)
                if area > largest:
                    shape = x
                    largest = area
            try:        
                main_dict[folder][image] = shape.tolist()
            except:
                main_dict[folder] = {}
                main_dict[folder][image] = shape.tolist()
    #save main_dict to memory file in JSON format
    with open(file_out, 'w') as f:
        json.dump(main_dict, f)
