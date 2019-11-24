# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 10:44:52 2019
"""

#import python libraries
import numpy
import cv2
import math
import datetime
import copy

#import shared libraries
from . import opencv_fun as opencv_fun
from . import misc_fun as misc_fun


def extract_fish_smart(image):
    
    """
    DESCRIPTION
    This function performs a basic thresholding operation to extract the 
    contour of a fish from an image.
    
    THIS FUNCTION IS CURRENTLY UNDER DEVELOPMENT: DAVID ASHTON
    
    INPUT
    image = an image in standard opencv format (bgr)
    
    OUTPUT
    fish = a contour in standard opencv format
    """
    
    #find the image background
    data, channel = opencv_fun.image_background(image)

    #split the image into separate channels    
    blue, green, red = cv2.split(image)
    
    #select the channel
    if channel == 0:
        image_grey = blue
    elif channel == 1:
        image_grey = green
    elif channel == 2:
        image_grey = red
    else:
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    #use blur subtraction to get objects
    image_subtract = opencv_fun.image_blur_subtraction(image_grey, 75, 350)
    
    #blur image and extract contours
    image_blur = cv2.GaussianBlur(image_subtract, (15, 15), 0) 
    
    #get mean and std_value for image
    mean_value = numpy.mean(image_blur)
    std_value = numpy.std(image_blur)
    #set threshold as proportion of pixel range
    thresh_value = int(mean_value + std_value*0.5)
    #threshold image using mean value
    ret, thresh_2 = cv2.threshold(image_blur, thresh_value, 255, cv2.THRESH_BINARY_INV)       
    
    #get contours
    contours, hierarchy = cv2.findContours(thresh_2, 1, 2)    
    
    #filter contours to specific size range
    contours = opencv_fun.filter_contours_size(contours, 1000, 500000)
    
    #filter to only include largest
    fish = opencv_fun.filter_contours_largest(contours, 1)
    
    #select the fish
    fish = fish[0]

    #return
    return fish


def extract_snapper_spots(image, fish):
    
    """
    DESCRIPTION
    This function locates the the blue external spots from snapper for
    biometric identification. This function requires the snapper to be located
    first as this is used to set several relative parameters within the 
    function. While this function is primarily designed to detect blue spots
    it currently also detects other spots on red backgrounds which have a 
    relatively high blue chanel (e.g. white).
    
    INPUT
    image = an image in standard opencv format (bgr)
    fish = a contour in standard opencv format
    
    OUTPUT
    blue_spots = a list of xy coordinates
    """

    #shrink fish by 10% so thate edge of the fish is not searched for spots
    fish = opencv_fun.contour_resize(fish, 0.90)
    #mask out the background colouration    
    image = opencv_fun.contour_mask_image(image, numpy.array([fish]))
    #split the channels
    image_blue, image_green, image_red = cv2.split(image)     
    #recast arrays to dat type that supports negative numbers
    image_blue = image_blue.astype(numpy.float32)
    image_red = image_red.astype(numpy.float32)    
    #divide blue channel by red channel
    image_dif =  image_blue - image_red    
    #normalize image to 0 - 255 range
    image_dif = misc_fun.array_normalize(image_dif, 0, 255)    
    #convert back got data type supported by opencv
    image_dif = image_dif.astype(numpy.uint8)   
    #invert image
    image_invert = (255 - image_dif)    
    #set blur subtraction parameters based on fish area
    blur_size = int(cv2.contourArea(fish)*0.0005)
    clahe_size = int(cv2.contourArea(fish)*0.00005)
    spot_size_min = int(cv2.contourArea(fish)*0.00004)
    spot_size_max = int(cv2.contourArea(fish)*0.0013)   
    #check that blur size is an uneven number
    if blur_size % 2 == 0:
        blur_size += 1 
    #check that clahe is not equal to zero >>> crashes kernel without error report
    if clahe_size == 0:
        clahe_size = 1
    #run blue subtraction to locate spots    
    image_subtract = opencv_fun.image_blur_subtraction(image_invert, blur_size, clahe_size)
    #get ROI around fish
    fish_ROI = opencv_fun.contour_ROI(image_subtract, fish)
    #get mean and standard deviation of pixels within the fish ROI
    mean_value = numpy.mean(fish_ROI)
    std_value = numpy.std(fish_ROI)       
    #set threshold as proportion of pixel range
    thresh_value = int(mean_value + std_value*3.2)#2.7  #3.2 
    #threshold image using the relative threshold value        
    ret, thresh_2 = cv2.threshold(image_subtract, thresh_value, 255, cv2.THRESH_BINARY)
    #get contours
    spots, hierarchy = cv2.findContours(thresh_2, 1, 2)
    #filter out contours not inside fish
    spots = opencv_fun.filter_contours_region(spots, fish)
    #filter contours based on circularity
    spots = opencv_fun.filter_contours_circularity(spots, 0.2, 1.5) 
    #filter spots for size
    spots = opencv_fun.filter_contours_size(spots, spot_size_min, spot_size_max)    
    #return
    return spots


def extract_salmon_spots(image, fish):
    
    """
    DESCRIPTION
    This function extracts the external spot patterns from an image of a 
    salmon. It requires that the salmon contour has been located.
    
    INPUT
    image = an image in standard opencv format (BGR)
    fish = a contour in standard opencv format
    
    OUTPUT
    output = a list of xy coordinates
    """

    #set parameters based on fish area
    blur_size = int(cv2.contourArea(fish)*0.00035)
    clahe_size = int(cv2.contourArea(fish)*0.00004)
    spot_size_min = int(cv2.contourArea(fish)*0.00004)
    spot_size_max = int(cv2.contourArea(fish)*0.005) 
#    print(blur_size, clahe_size, spot_size_min, spot_size_max)
    #check that blur size is an uneven number
    if blur_size % 2 == 0:
        blur_size += 1  
    #mask out the background colouration    
    image = opencv_fun.contour_mask_image(image, numpy.array([fish]))
    #create a greyscale image
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #generate blur subtraction image
    image_subtract = opencv_fun.image_blur_subtraction(image_grey, blur_size, clahe_size)
    #select ROI for contour
    fish_ROI = opencv_fun.contour_ROI(image_subtract, fish)
    #get mean and standard deviation of pixels within the fish ROI
    mean_value = numpy.mean(fish_ROI)
    std_value = numpy.std(fish_ROI)
    #set threshold as proportion of pixel range
    thresh_value = int(mean_value + std_value*2)
    #threshold image using mean value
    ret, thresh_2 = cv2.threshold(image_subtract, thresh_value, 255, cv2.THRESH_BINARY)
    #get spot contours
    spots, hierarchy = cv2.findContours(thresh_2, 1, 2)
    #filter spots for size
    spots = opencv_fun.filter_contours_size(spots, spot_size_min, spot_size_max)
    #filter spots that are not within the fish region
    spots = opencv_fun.filter_contours_region(spots, fish)
    #return
    return spots


def extract_fish_eye(image, fish):

    """
    DESCRIPTION
    This function will locate the black pupil of a fish eye from an image of a
    fish. The pupil is returned as a standard opencv contour so that additional
    operations can be carried out on it by downstream functions.
        
    INPUT
    image = the image containing the fish (colour)
    fish = a contour in standard opencv format
    
    OUTPUT
    fish_eye = a contour in standard opencv format
    """
    
    #set image blur based on fish 
    blur_size = int(cv2.contourArea(fish)*0.0005)
    clahe_size = int(cv2.contourArea(fish)*0.00005)
    minimum_size = int(cv2.contourArea(fish)*0.0008)
    maximum_size = int(cv2.contourArea(fish)*0.025)
    #check that blur size is an uneven number
    if blur_size % 2 == 0:
        blur_size += 1
    #reduce fish to just the fish head
    fish_head = opencv_fun.contour_extreme_pts(fish, 0, 0, 0.15)
    #convert to greyscale
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #blur mask the image
    image_subtract = opencv_fun.image_blur_subtraction(image_grey, blur_size, clahe_size)
    #select ROI for contour
    fish_ROI = opencv_fun.contour_ROI(image_subtract, fish)
    #get mean and standard deviation of pixels within the fish ROI
    mean_value = numpy.mean(fish_ROI)
    std_value = numpy.std(fish_ROI)
    #set threshold as proportion of pixel range
    thresh_value = int(mean_value + std_value*2.5)
    #threshold image using mean value
    ret, thresh_2 = cv2.threshold(image_subtract, thresh_value, 255, cv2.THRESH_BINARY_INV)
    #erosion and dilation steps
    de_kernel = numpy.ones([3, 3], numpy.uint8)
    thresh_2 = cv2.dilate(thresh_2, de_kernel, 1)
    thresh_2 = cv2.erode(thresh_2, de_kernel, 1)    
    #generate contours
    contours, hierarchy = cv2.findContours(thresh_2, 1, 2)
    #filter to contours within fish head region
    contours = opencv_fun.filter_contours_region(contours, fish_head)
    #check that it is within the expected size
    contours = opencv_fun.filter_contours_size(contours, minimum_size, maximum_size)
    #filter contours for circularity
    contours = opencv_fun.filter_contours_circularity(contours, 0.5, 2.5)
    #filter contours to keep most circular
    contours = opencv_fun.filter_contours_most_circular(contours, 1)
    #set output to None if contours is empty
    if len(contours) == 0:
        eye = None 
    else:
        eye = contours[0]
    #return
    return eye


def extract_fish_morphometrics(fish, points, angle): 
    
    """
    DESCRIPTION
    This function selects a list of points (xy coordinates) from a contour 
    which can be used to measure the shape of the contour. This function starts 
    by selecting two reference points around the contour. it then moves along 
    at set intervals between the two reference points(e.g. 0.5 would be half 
    way between the nose and tail of a fish) and selects an xy point from the 
    contour which is at a specified angle from this interval (e.g. 0.5 at 90 
    degrees would be the top of the fish half way between the nose and the 
    tail).
    
    INPUT
    fish = a contour in standard opencv format
    points = a list of intervals at which to select points = [0.1, 0.5, 1]
    angle = the angle at which to take samples
    
    OUTPUT
    new_contour = xy coordinates of each morphometric point
    new_stats = distance to center line for each of the morphometric points
    """
    
    #generate the two reference points
    ref_1, lip_l = ref_fish_lips(fish) 
    ref_2, tail_across_l = ref_tail_across(fish)
    #get the angle between the two references
    ref_angle = misc_fun.degrees(ref_1, ref_2)
    #correct the target angle for the angle of the references
    angle_corrected = angle + ref_angle
    #set up new contour and stats lists
    new_stats = []
    new_contour = [] 
    #loop through points and find required xy coordinates
    loop = 0
    while loop < len(points):
        #generate line point
        dist = points[loop]
        mid_pt = misc_fun.point_mid(ref_1, ref_2, dist)
        #find point at specified angle
        out_pt = opencv_fun.contour_pt_angle(fish, mid_pt, angle_corrected)
        new_contour += [[out_pt]]
        new_stats += [misc_fun.distance(mid_pt, out_pt)]
        loop += 1
    #return
    return numpy.array(new_contour), new_stats 


def ref_tail_across(fish):
    
    """
    DESCRIPTION
    This function extracts the reference points on either side of the tail at
    the narrowest cross-section. This function locates the cross-section by 
    first finding the center line, walking from front to end of fish, and 
    locating the narrowest cross-section section within a target region.
    
    INPUT
    fish = a contour in standard opencv format
    
    OUTPUT
    ref_upper = a list containing xy coordinates
    ref_lower = a list containing xy coordinates
    """

    #get the center line of the fish
    pos_low, pos_high, line = opencv_fun.contour_center_line(fish)
    #get angle between two xy coordinates
    fish_angle = misc_fun.degrees(pos_low, pos_high)
    #select the top and bottom angles
    angle_top = misc_fun.degrees_limit_range(fish_angle + 90)
    #initialize width data
    data_width = []    
    #walk length of fish and generate dictionary of widths
    for x in range(pos_low[0], pos_high[0]):
        #calculate proportion
        proportion = (x-pos_low[0])/float(pos_high[0]-pos_low[0])
        #get points if within target proportion
        if 0.7 < proportion < 0.9:
            #calculate center point
            center_pos = misc_fun.point_mid(pos_low, pos_high, proportion)
            #walk out until edge is retched
            cross_section_points = opencv_fun.contour_crosssection(fish, center_pos, angle_top)          
            #check if cross-section was found
            if cross_section_points is not None:
                #get most distant points from the cross-section
                points_out = misc_fun.distant_points(cross_section_points)
                #calculate width
                width = misc_fun.distance(points_out[0], points_out[1])
                #add to data
                data_width += [[proportion, width, center_pos, points_out[0], 
                                points_out[1]]]   
    #find narrowest width
    width_min = min([x[1] for x in data_width])  
    #filter to target position
    data_width = [x for x in data_width if x[1] == width_min]
    #create sorted list of the two points
    data_points = [data_width[0][3], data_width[0][4]]
    data_points.sort(key=lambda x: x[1])
    #get upper and lower ref points
    ref_upper = data_points[0].tolist()
    ref_lower = data_points[1].tolist()
    #return
    return ref_upper, ref_lower
    
    
def ref_tail_fork(fish):
    
    """
    DESCRIPTION
    This function uses the outline of a snapper or trevally to find the 
    position of the tail fork. This function may work for other similar fish 
    shapes.
    
    INPUT
    fish = a contour in standard opencv format
    
    OUTPUT
    tail_fork = the xy coordinates of the tail fork    
    """

    #find center of contour
    center = opencv_fun.contour_center(fish)    
    #check or convert fish to a list
    fish = fish.tolist() 
    #get minimum and maximum x coordinates for fish
    pos_1 = min(x[0][0] for x in fish)
    pos_2 = max(x[0][0] for x in fish)
    #set tail to last 20% of fish
    limit = int(pos_1 + ((pos_2 - pos_1)*0.80))
    #get points from contour which are past the 80% limit
    fish_tail = []
    for x in fish:
        if x[0][0] >= limit:
            fish_tail += [x]         
    #get the highest point in the profile as the first tail tip
    min_x = 1000000
    for x in range(len(fish_tail)):
        if fish_tail[x][0][0] < min_x:
            min_x = fish_tail[x][0][0]
            min_x_pos = x         
    #rotate contour so that the min_x_pos is at the start and the end
    fish_tail = fish_tail[min_x_pos:] + fish_tail[:min_x_pos]
    #convert contour to profile
    profile_1 = opencv_fun.contour_to_profile(numpy.array(fish_tail), center)
    #calculate a reduced density front_fish contour
    epsilon = 0.065*cv2.arcLength(numpy.array(fish_tail), False)
    approx = cv2.approxPolyDP(numpy.array(fish_tail), epsilon, False) 
    #generate contour of reduced density
    profile_2 = opencv_fun.contour_to_profile(approx, center) 
    #stretch profile_2 x axis to match the profile_1 range 
    max_1 = max([x[0] for x in profile_1])
    max_2 = max([x[0] for x in profile_2])
    ratio = max_1 / float(max_2)
    profile_2 = [[x[0] * ratio, x[1]] for x in profile_2] 
    #save contours et al..
    fish_tail = [x[0] for x in fish_tail]
    #find biggest triangle as tail fork
    triangle = opencv_fun.profile_largest_triangle(profile_1, 10000)
    #get middle point of triangle as fork_out
    if triangle is not None:
        fork_out = fish_tail[triangle[1]]
    else:
        fork_out = None
    #return
    return fork_out


def ref_tail_upper(fish): 
    
    """
    DESCRIPTION
    This function uses a snapper contour to find the upper tip of the tail.
    
    INPUT
    fish = a snapper contour in standard opencv format
    
    OUTPUT
    ref = the xy coordinates for the upper tip of the snapper tail
    
    """    
    
    #convert the contour to a list
    fish = fish.tolist()
    #    
    pos_1 = min(x[0][0] for x in fish)
    pos_2 = max(x[0][0] for x in fish)
    limit = int(pos_1 + ((pos_2 - pos_1)*0.80))    
    new_fish = []
    for x in fish:
        if x[0][0] >= limit:
            new_fish += [x]
    value_1 = min(x[0][1] for x in new_fish)
    for x in new_fish:
        if x[0][1] == value_1:
            ref = x[0]
            break
    return ref


def ref_fish_lips(fish):
    
    """
    DESCRIPTION
    This function finds the upper and lower lip from a fish contour. The output
    is two xy coordinates representing the upper and lower lip position. If it 
    cannot find two distinct lips then the same xy coordinate is returned for
    both lips
    
    INPUT
    fish = a contour in standard opencv format
    
    OUTPUT
    nose_1 = an XY coordinate for the fishes top lip
    nose_2 = an XY coordinate for the fishes bottom lip
    """
    
    #find center of contour
    center = opencv_fun.contour_center(fish)    
    #select the front 5% of the fish  
    pos_1 = min(x[0][0] for x in fish)
    pos_2 = max(x[0][0] for x in fish)
    limit = int(pos_1 + ((pos_2 - pos_1)*0.05))    
    front_fish = []
    for x in fish:
        if x[0][0] <= limit:
            front_fish += [x]  
    #convert contour to profile
    profile_1 = opencv_fun.contour_to_profile(numpy.array(front_fish), center)
    #calculate a reduced density front_fish contour
    epsilon = 0.065*cv2.arcLength(numpy.array(front_fish), False)
    approx = cv2.approxPolyDP(numpy.array(front_fish), epsilon, False)
    #generate contour of reduced density
    profile_2 = opencv_fun.contour_to_profile(approx, center)    
    #stretch profile_2 x axis to match the profile_1 range 
    max_1 = max([x[0] for x in profile_1])
    max_2 = max([x[0] for x in profile_2])
    ratio = max_1 / float(max_2)
    profile_2 = [[x[0] * ratio, x[1]] for x in profile_2]   
    #select nose points from reduced profile
    if len(profile_2) == 6:
        nose_1 = profile_2[1]
        nose_2 = profile_2[4]
    elif len(profile_2) == 5:
        nose_1 = profile_2[1]
        nose_2 = profile_2[3]
    elif len(profile_2) == 4:
        nose_1 = profile_2[1]
        nose_2 = profile_2[2]        
    elif len(profile_2) == 3:
        nose_1 = profile_2[1]
        nose_2 = profile_2[1]
    else:
        print('problem fish_fun.ref_fish_lips: %s' % (len(profile_2)))
        nose_1 = profile_2[1]
        nose_2 = profile_2[1]
    #find the related points in the front_fish contour
    nose_dist_1 = 10000000
    nose_dist_2 = 10000000
    loop = 0
    while loop < len(profile_1):
        if abs(nose_1[0] - profile_1[loop][0]) < nose_dist_1:
            nose_dist_1 = abs(nose_1[0] - profile_1[loop][0])
            nose_out_1 = front_fish[loop][0]
        if abs(nose_2[0] - profile_1[loop][0]) < nose_dist_2:
            nose_dist_2 = abs(nose_2[0] - profile_1[loop][0])
            nose_out_2 = front_fish[loop][0]                  
        loop += 1
    #select which nose point is the upper lip
    if nose_out_1[1] < nose_out_2[1]:
        nose_1 = nose_out_1.tolist()
        nose_2 = nose_out_2.tolist()
    else:
        nose_1 = nose_out_2.tolist()
        nose_2 = nose_out_1.tolist()
    #return
    return nose_1, nose_2


def ref_fish_head(fish, ref_nose, ref_tail):
    
    """
    DESCRIPTION
    This function uses a fish contour and reference points for the upper lip 
    and narrowest cross-section of the tail to generate a third head reference 
    point. 
    
    INPUT
    fish = a contour in standard opencv format
    ref_1 = an XY coordinate for upper lip
    ref_3 = an XY coordinate for the fishes tail
    
    OUTPUT
    ref = an xy coordinate for the ref point on the top of the fishes head
    """
    
    #initialize output variable
    ref_head = None
    #get angle between ref_1 and ref_3
    deltaX = ref_tail[0] - ref_nose[0]
    deltaY = ref_tail[1] - ref_nose[1]
    angle = math.atan2(deltaY, deltaX)*(180/math.pi)
    #get starting pos 30% along from ref_1 towards ref_3
    pos_start = [int(ref_nose[0] + ((ref_tail[0] - ref_nose[0])*0.3)),
                 int(ref_nose[1] + ((ref_tail[1] - ref_nose[1])*0.3))]
    #calculate point on fish outline at set angle from pos_start
    closest = 1000
    for x in fish:
        deltaX = pos_start[0] - x[0][0]
        deltaY = pos_start[1] - x[0][1]
        test_angle = math.atan2(deltaY, deltaX)*(180/math.pi)
        if abs(test_angle - (90 + angle)) < closest:
            closest = abs(test_angle - (90 + angle))
            ref_head = numpy.ndarray.tolist(x[0])
    #return
    return ref_head

 
def search_for_pattern(dataset, new_individual, limit, perm, method):
    
    """
    DESCRIPTION
    This function searchs through an existing dataset of spot patterns for a 
    target spot pattern. To do this it first aligns the spot patterns using an 
    affine transformation. it then counts the number of spots that are matching 
    between the different patterns to find a positive match.
    
    INPUT
    dataset = the dataset in which to search for the new pattern
    new_individual = the data from the new individual (spots + ref points)   
    limit = the minimum number of matching spots for a match
    perm = maximum permutations to search for a match
    method = the affine reference points to use for matching
    
    OUTPUT
    match_name = the name from the matching individual (if found)
    match_value = the number of spots shared between the matching patterns
    perm_out = the number of permutations it took to find a match
    time_out = the time it took to find a match
    """
    
    #set an initial start time
    start_time = datetime.datetime.now()
    #loop through dataset for a total number of permutations
    loop = 0
    while loop < len(range(perm)):
        #initialize None for return values
        match_name = None
        match_value = None
        perm_out = None
        #loop through each individual in the pattern_data
        for prior_individual in dataset:
            #update the output permutation
            perm_out = loop
            #get the probability of match
            if len(new_individual['spots']) > 3 and len(prior_individual['spots']) > 3:
                #align both spot patterns (prior aligned to new) 
                aligned_pattern = align_patterns(copy.deepcopy(new_individual), 
                                                 copy.deepcopy(prior_individual), 
                                                 method)
                #calculate distances between spots
                match_list = compare_patterns(new_individual['spots'], 
                                              aligned_pattern)
                #count the number of matching spots
                match = len([x for x in match_list if x[1] < 0.15])
                #break if sufficient number of matching spots is found
                if match > limit:
                    match_name = prior_individual['name']
                    match_value = match                    
                    loop =  len(range(perm))
                    break
        #increment loop
        loop += 1
    #calculate time it took to match
    end_time = datetime.datetime.now()
    time_out = end_time - start_time
    time_out = time_out.total_seconds()
    #return            
    return match_name, match_value, perm_out, time_out


def align_patterns(ind_1, ind_2, method):
    
    """
    DESCRIPTION
    This function takes the data from two individuals (spots + ref points) and
    aligns the second individual to the same space as the first individual. A
    range of different reference point methods can be used for this alignment
    including, random, radius, triangle, and fish_ref.
    
    THOUGHT: The initial bounding box positioning in this function should be 
    moved to a separate step in the same way that common_space is used in 
    older versions of the biometric id. Individuals should be stored as 
    common_space objects.
    
    INPUT
    ind_1 = data from the first individual (spots + ref points)
    ind_2 = data from the second individual (spots + ref points)
    method = a string defining which method to use
    
    OUTPUT
    pattern_aligned = the spots from the second individual aligned to the first
    """
       
    if method == 'radius':
        #get ref points based on bounding box
        ref_1 = opencv_fun.ref_bounding(numpy.array(ind_1['spots']))
        ref_2 = opencv_fun.ref_bounding(numpy.array(ind_2['spots']))
        #replace middle ref point
        ref_1[1] = opencv_fun.ref_affine_third(ref_1[0], ref_1[2]) 
        ref_2[1] = opencv_fun.ref_affine_third(ref_2[0], ref_2[2])    
        
        #generate affine matrix
        matrix = opencv_fun.affine_matrix(ref_1, ref_2)
        #convert pattern_2 to same position as pattern_1
        pattern_aligned = []
        for point in ind_2['spots']:
            #convert to new position
            point_new  = opencv_fun.affine_apply(matrix, point)
            #convert points to integers
            point_new = [int(x) for x in point_new]
            #add to pattern_new
            pattern_aligned += [point_new] 
        #set ind_2 spots to pattern_new position
        ind_2['spots'] = pattern_aligned            
        #generate radius based ref points
        ref_1, ref_2 = opencv_fun.ref_affine_radius(ind_1['spots'], 
                                                    pattern_aligned, 
                                                    100, 0.1, 100)
        #generate the third ref point
        ref_1 += [opencv_fun.ref_affine_third(ref_1[0], ref_1[1])] 
        ref_2 += [opencv_fun.ref_affine_third(ref_2[0], ref_2[1])] 
    elif method == 'random':
        ref_1, ref_2 = opencv_fun.ref_affine_random(ind_1['spots'], 
                                                    ind_2['spots'])
        ref_1 += [opencv_fun.ref_affine_third(ref_1[0], ref_1[1])]
        ref_2 += [opencv_fun.ref_affine_third(ref_2[0], ref_2[1])]
    elif method == 'triangle':
        ref_1, ref_2 = opencv_fun.ref_affine_triangle(ind_1['spots'], 
                                                      ind_2['spots'], 
                                                      5000, 0.03)
        ref_1[1] = opencv_fun.ref_affine_third(ref_1[0], ref_1[2]) 
        ref_2[1] = opencv_fun.ref_affine_third(ref_2[0], ref_2[2]) 
    elif method == 'fish_ref':
        #reference points for primary alignment using nose and tail of fish
        ref_1 = [ind_1['ref_nose'], None, ind_1['ref_tail']]
        ref_2 = [ind_2['ref_nose'], None, ind_2['ref_tail']]
        #check for missing reference points
        if (ref_1 + ref_2).count(None) > 2:            
            #get ref points based on bounding box
            ref_1 = opencv_fun.ref_bounding(numpy.array(ind_1['spots']))
            ref_2 = opencv_fun.ref_bounding(numpy.array(ind_2['spots']))
        #generate generic third reference point
        ref_1[1] = opencv_fun.ref_affine_third(ref_1[0], ref_1[2]) 
        ref_2[1] = opencv_fun.ref_affine_third(ref_2[0], ref_2[2])         
        #generate affine matrix
        matrix = opencv_fun.affine_matrix(ref_1, ref_2)       
        #convert pattern_2 to same position as pattern_1
        pattern_aligned = []
        for point in ind_2['spots']:
            #convert to new position
            point_new  = opencv_fun.affine_apply(matrix, point)
            #convert points to integers
            point_new = [int(x) for x in point_new]
            #add to pattern_new
            pattern_aligned += [point_new]            
        #set ind_2 spots to pattern_new position
        ind_2['spots'] = pattern_aligned       
        #ref points for secondary alignment using radius method
        ref_1, ref_2 = opencv_fun.ref_affine_radius(ind_1['spots'], 
                                                    ind_2['spots'], 
                                                    100, 0.1, 100)       
        #generate the third ref point
        ref_1 += [opencv_fun.ref_affine_third(ref_1[0], ref_1[1])] 
        ref_2 += [opencv_fun.ref_affine_third(ref_2[0], ref_2[1])]

    #generate the final transformation matrix
    matrix = opencv_fun.affine_matrix(ref_1, ref_2)  
    #generate final aligned pattern
    pattern_aligned = []
    for point in ind_2['spots']:
        #convert to new position
        point_new  = opencv_fun.affine_apply(matrix, point)
        #convert points to integers
        point_new = [int(x) for x in point_new]
        #add point to pattern
        pattern_aligned += [point_new]                
    #return
    return pattern_aligned


def standardize_pattern(pattern_1):
    
    """
    DESCRIPTION
    This function converts an input pattern to the predefined standardized 
    space using a 2D affine transformation. It uses the nose and tail of the
    input individual to align the spot pattern to the ref_2 points.
    
    INPUT
    pattern_1 = data from the first individual (spots + ref points)
    
    OUTPUT
    pattern_standardized = a spot pattern in standard space
    """
    
    #reference points for primary alignment using nose and tail of fish
    ref_1 = [pattern_1['ref_nose'], None, pattern_1['ref_tail']]
    ref_2 = [[100, 400], None, [600, 400]]
    #generate generic third reference point
    ref_1[1] = opencv_fun.ref_affine_third(ref_1[0], ref_1[2]) 
    ref_2[1] = opencv_fun.ref_affine_third(ref_2[0], ref_2[2])         
    #generate affine matrix
    matrix = opencv_fun.affine_matrix(ref_2, ref_1)       
    #convert pattern_2 to same position as pattern_1
    pattern_standardized = []
    for point in pattern_1['spots']:
        #convert to new position
        point_new  = opencv_fun.affine_apply(matrix, point)
        #convert points to integers
        point_new = [int(x) for x in point_new]
        #add to pattern_new
        pattern_standardized += [point_new]     
    #return
    return pattern_standardized


def compare_patterns(pattern_1, pattern_2): 

    """
    DESCRIPTION
    This function finds the matching spots between two patterns and returns a
    list containing the distance for each match + the relative distance to 
    the next closest match.
    
    INPUT
    pattern_1 = a list of xy coordinates
    pattern_2 = a list of xy coordinates
    
    OUTPUT
    dist_list = a list containing distances for each spot in pattern_1
    """ 
    
    #init an empty dist_list
    dist_list = []
    #loop through each spot in pattern_1
    for spot in pattern_1:
        #calculate distances to spots in pattern_2
        dist = [misc_fun.distance(spot, x) for x in pattern_2]
        #get minimum dist
        dist_min = min(dist)
        #get position of closest spot
        closest = dist.index(min(dist))
        #calculate distances from closest spot to pattern_1
        dist_2 = [misc_fun.distance(pattern_2[closest], x) for x in pattern_1]
        #get minimum dist_2
        dist_min_2 = min(dist_2)
        if dist_min == dist_min_2:
            #sort distance
            dist.sort()
            #add to count if passed limit
            if dist[0] == 0:
                dist_list += [[dist_min, 0]]
            else:
                dist_list += [[dist_min, dist[0]/float(dist[1])]]
    #return
    return dist_list    
 