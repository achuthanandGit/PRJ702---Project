# -*- coding: utf-8 -*-
"""
Created on Thu May 17 13:24:08 2018
"""


#import python libraries
import cv2
import numpy
import math
import statistics
import random


#import shared modules
from . import misc_fun as misc_fun


def contour_crosssection(contour, position, angle_cross_1):
    
    """
    DESCRIPTION
    This function locates the outer edge of a contour at a defined angle from 
    the starting position. This function is limited to finding angles within a
    45 degree range.
    
    INPUT
    contour = a contour in standard opencv format
    postion = xy coordinates of the starting position
    angle_cross_1 = the angle (degrees) at which to find the edge
    
    OUTPUT
    postion_out = xy coordinates of the outer edge
    """ 
    
    #generate the alternate angle for the cross-section
    angle_cross_2 = misc_fun.degrees_limit_range(angle_cross_1 + 180)  
    #initialize position_out
    position_out = None    
    #initialize empty data dictionary
    data = []
    #get set of points either side
    for x in range(0, len(contour)-1):
        #calculate angle to each position
        angle_1 = misc_fun.degrees(position, contour[x][0])
        angle_2 = misc_fun.degrees(position, contour[x+1][0])
        #search for target angle if 20 degree region is found
        if abs(angle_1 - angle_2) < 20:
            #create aa angle list
            angle_list = [angle_1, angle_2]
            #sort the angle list
            angle_list.sort()
            #check if either angle_cross is within the region
            if angle_list[0] <= angle_cross_1 <= angle_list[1]:
                data += [[contour[x][0], contour[x+1][0]]]
            if angle_list[0] <= angle_cross_2 <= angle_list[1]:
                data += [[contour[x][0], contour[x+1][0]]]
                
    #set empty output points
    position_out = None
    distance_max = 0
    #check if position_out is already found
    if len(data) > 1:
        #get two most distant points
        for x in data:
            for y in data:
                if misc_fun.distance(x[0], y[0]) >= distance_max:
                    #update max distance
                    distance_max = misc_fun.distance(x[0], y[0])
                    #set as output points
                    position_out = [x[0], y[0]]  
    #return 
    return position_out


def contour_mask_image(image, contour):
    
    """
    DESCRIPTION
    This function masks out the pixels in an image that are outside the input
    contours. The background is set to black.
    
    INPUT
    image = an image in standard opencv format
    contour = contours in standard opencv format
    
    OUTPUT
    image_out = an image in standard opencv format
    """
    
    #Creat a mask of the contour and remove surrounding color
    image_grey = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) 
    #draw images onto greyscale image
    cv2.drawContours(image_grey, contour, -1, 0, -1)
    #threshold to get mask
    ret, mask = cv2.threshold(image_grey, 10, 255, cv2.THRESH_BINARY)
    #invert mask
    maskInv = cv2.bitwise_not(mask)
    #subtract mask
    image_out = cv2.bitwise_and(image, image, mask = maskInv)    
    #return 
    return image_out


def contour_is_square(contour):
    
    """
    DESCRIPTION
    This function checks if the input contour is a square.
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT
    output = boolean (True/False)
    """
    
    #create a reduced approximate of the contour
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
    #check if it has four vertices
    if len(approx) == 4:
        output = True
    else:
        output = False
    #return
    return output


def contour_center(contour):
    
    """
    DESCRIPTION:
    This function finds the center of mass for an input contour. To do this it
    uses the moments() of the contour from opencv.
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT:
    output = the center of mass for the input contour
    """
    
    #if contour area is greater than zero
    if cv2.contourArea(contour) > 0:
        M = cv2.moments(contour)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
    #if contour area is equal to zero
    if cv2.contourArea(contour) == 0:
        #get minimum and maximum values
        min_x = min([x[0][0] for x in contour])
        max_x = max([x[0][0] for x in contour])
        min_y = min([x[0][1] for x in contour])
        max_y = max([x[0][1] for x in contour])
        #get x coordinate
        if min_x != max_x:
            cx = int(min_x + (max_x - min_x)/float(2))
        else:
            cx = min_x
        #get y coordinate
        if min_y != min_x:            
            cy = int(min_y + (max_y - min_y)/float(2))
        else:
            cy = min_y
    #merge into output
    output = [cx,cy]
    #return
    return output


def contour_center_line(contour):
    
    """
    DESCRIPTION
    This function finds the center line for an input contour. The center line
    is output as the coordinates at the lowest and highest x value of the 
    contour and the data generated by the opencv fitline function.
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT
    pos_lowest = xy coordinates for the line at the lowest x axis point
    pos_highest = xy coordinates for the line at the highest x axis point
    line_data = the data generated by cv2.fitline function
    """
    
    #generate xy coordinates at either end of the contour
    line_data = cv2.fitLine(contour, cv2.DIST_L2, 0, 0.01, 0.01)
    #convert line_data into variables
    [vx,vy,x,y] = line_data
    #get lowest x
    x_lowest = min([x[0][0] for x in contour])
    #get position
    pos_lowest = [x_lowest, int(((x_lowest-x)*vy/vx)+y)]
    #get highest x
    x_highest = max([x[0][0] for x in contour])
    #get position
    pos_highest = [x_highest, int(((x_highest-x)*vy/vx)+y)]    
    #return
    return pos_lowest, pos_highest, line_data


def contour_bounding_box_fitted(contour):
    
    """
    DESCRIPTION
    This function generates a contour of four points which represents the 
    fitted bounding box around the input contour
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT
    box = a contour in standard opencv format
    """
    
    #get minimum area rectangle
    rectangle = cv2.minAreaRect(contour)
    #get box points
    box = cv2.boxPoints(rectangle)
    #convert to box contour
    box = numpy.int0(box)
    #return
    return box


def contour_angle(contour):
    
    """
    DESCRIPTION:
    This function gets the primary angle of a contour using the fitLine axis of 
    the contour. The angle is returned in degrees starting from a horizontal 
    line and rotating clock-wise. The highest x coordinate is the center point
    of the rotation.
    
    INPUT:
    contour = a contour in standard opencv format.
    
    OUTPUT:
    angle = the angle of the contour
    """
    
    #calculate the fitline points
    vx,vy,x,y = cv2.fitLine(contour, cv2.DIST_L2,0,0.01,0.01)
    #use the fitline points to generate xy line_points
    lefty = int((-x*vy/vx) + y)
    righty = int(((1000-x)*vy/vx)+y)
    line_points = [1000-1, righty], [0, lefty] 
    #calculate the angle between two points
    angle = misc_fun.degrees(line_points[0], line_points[1])
    #return
    return angle


def contour_circularity_perimeter(contour):
    
    """
    DESCRIPTION
    This function measures the circularity of a contour based on the perimeter
    length and how this compares with a circle of equal volume. The circularity 
    is a ratio between 0 and 1. A value of 1 means it is a perfect circle and 
    it is less circular as it moves towards 0.
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT
    circularity = the circularity of the input contour     
    """
    
    #get the area of the input contour
    area = cv2.contourArea(contour)
    #calculate the circumference of a circle with the same area
    circumference = 2*3.14159*math.sqrt((area/3.14159))
    #get the perimeter length of the input contour
    perimeter = cv2.arcLength(contour, True)
    #if perimeter is not zero then calculate circularity
    if perimeter != 0:
        #calculate circularity as a ratio of the actual perimeter
        circularity = circumference / float(perimeter)
    else:
        circularity = 0
    #return
    return circularity


def contour_circularity_radius(contour):
    
    """
    DESCRIPTION
    This function measures the circularity of a contour based on the radius at
    the maximum width and how this compares with a circle of equal radius. A
    perfect circle will have an output value of 1 with lower and higher 
    indicating more or less circular.
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT
    measure = a float value (1 = perfect circle)
    """
    
    #get minimum area rectangle
    rectangle = cv2.minAreaRect(contour) 
    #get the longest axis
    radius = max(rectangle[1])/float(2) 
    #calculate area of a circle with width
    circle_area = 3.14159 * (radius * radius)  
    #compare area of contour and generated circle
    contour_area = cv2.contourArea(contour) 
    if contour_area > 0:
        measure = contour_area / float(circle_area)
    else:
        measure = 0
    #return
    return measure


def contour_rotate(contour, degrees):
    
    """
    DESCRIPTION:
    This function rotates a contour by a set number of degrees using an affine
    transformation. The affine transformation is limited to a two point 
    reference system. This function rotates clockwise. 
    
    INPUT
    contour = a contour in standard opencv format
    degrees = number of degrees to rotate the contour
    
    OUTPUT
    new_contour = a contour in standard opencv format
    """    
    
    mid_point = contour_center(contour)
    #generate first ref point set
    point_2 = misc_fun.point_distance(mid_point, 500, 0)
    point_3 = misc_fun.point_distance(mid_point, 500, 90)
    ref_1 = [point_2, mid_point, point_3]     
    #generate second ref point set
    point_2 = misc_fun.point_distance(mid_point, 500, 0+degrees)
    point_3 = misc_fun.point_distance(mid_point, 500, 90+degrees)
    ref_2 = [point_2, mid_point, point_3]
    #convert the reference points to numpy arrays of type float32   
    old = numpy.array([(ref_1[0][0],ref_1[0][1]),
                       (ref_1[1][0],ref_1[1][1]),
                       (ref_1[2][0],ref_1[2][1])], numpy.float32)
    new = numpy.array([(ref_2[0][0],ref_2[0][1]),
                       (ref_2[1][0],ref_2[1][1]),
                       (ref_2[2][0],ref_2[2][1])], numpy.float32)
    #generate an affine matrix using the two reference point sets
    affine = cv2.getAffineTransform(new, old)
    #use affine matrix to convert contour_2 to the same space as contour_1
    new_contour = []
    for x in contour:
        #generate new x and y coordinate
        new_x = affine[0][0] * x[0][0] + affine[0][1] * x[0][1] + affine[0][2]
        new_y = affine[1][0] * x[0][0] + affine[1][1] * x[0][1] + affine[1][2]
        #add to new_contour
        new_contour.append([[int(new_x), int(new_y)]])
    #convert output contour to a numpy array
    new_contour = numpy.array(new_contour)
    #return
    return new_contour


def contour_hull_points(contour):
    
    """
    DESCRIPTION
    This function finds the points in a contour that are in direct contact with
    the convex hull of the contour and returns them as a new contour.
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT
    new_contour = a contour in standard opencv format   
    """
    
    #generate the convex hull for the contour
    hull = cv2.convexHull(contour)
    #init an empty new_contour list
    new_contour = []
    #for each point in contour test if it contacts the convex hull
    for pt in contour:
        dist = cv2.pointPolygonTest(hull,(pt[0][0],pt[0][1]),True)
        if dist == 0:
            new_contour += [pt]
    #convert contour to a numpy array
    new_contour = numpy.array(new_contour)
    #return
    return new_contour


def contour_contrast(image, contour, channel):
    
    """
    DESCRIPTION
    This function measures the contrast across the edge of a contour in an 
    image. To do this it walks around each point in the contour and measures
    the contrast on either side of the point at a 90 degree angle to the
    contour line. If the input image is greyscale it will measure the contrast
    as the difference in light/dark. If the input image is a BGR image it will
    measure the difference for a selected channel after removing the average 
    diffence observed across all three channels.
    
    INPUT
    image = an image in standard opencv format (greyscale or colour)
    contour = a contour in standard opencv format
    channel = which colour channel to look for contrast scores
    
    OUTPUT
    out = the average greyscale contrast value around the contour
    """
   
    #get width and height of img
    height, width = image.shape[:2]
    #check if greyscale or color
    dimensions = len(image.shape)
    #set up initial variable states
    total = 0
    last_pos = contour[0][0]
    count = 0
    loop = 1
    while loop < len(contour)-1:
        if misc_fun.distance(last_pos, contour[loop][0]) > 20:
            angle = misc_fun.degrees(contour[loop-1][0], contour[loop+1][0])
            #generate two points either side of contour
            point_1 = misc_fun.point_distance(contour[loop][0], 5, angle + 90)
            point_2 = misc_fun.point_distance(contour[loop][0], 5, angle - 90)
            #check that points are not outside the image
            if point_1[0] > width-1:
                point_1[0] = width-1
            if point_1[1] > height-1:
                point_1[1] = height-1
            if point_2[0] > width-1:
                point_2[0] = width-1 
            if point_2[1] > height-1:
                point_2[1] = height-1          
            #add the dif relative to other channels to the total dif
            if dimensions == 3:
                values_1 = numpy.array([int(image[point_1[1]][point_1[0]][0]),
                            int(image[point_1[1]][point_1[0]][1]),
                            int(image[point_1[1]][point_1[0]][2])])
                values_2 = numpy.array([int(image[point_2[1]][point_2[0]][0]),
                            int(image[point_2[1]][point_2[0]][1]),
                            int(image[point_2[1]][point_2[0]][2])])
                channel_dif = abs(values_1[channel] - values_2[channel])
                total_dif = abs(values_1.mean() - values_2.mean())
                total += abs(channel_dif - total_dif) 
            else:
                total += abs(int(image[point_1[1]][point_1[0]]) - int(image[point_2[1]][point_2[0]]))
            #update last position
            last_pos = contour[loop][0]
            count += 1
        loop += 1
    #if channel does not exist set value to fail
    if channel > dimensions - 1:
        out = -1
    else:
        out = total / float(count)
    #return
    return out  


def contour_contrast_multi(image, channel, contour):
    
    """
    DESCRIPTION
    This function measures the contrast across the edge of a contour in the 
    channel that is the most different from the mean in the background. This
    functionality allows it to adapt to multiple background colours.
    
    INPUT
    image = an image in standard opencv format (colour)
    channel = the background channel 
    contour = a contour in standard opencv format
    
    OUTPUT
    difference = the average difference between interior and exterior HSV pixels
    """

    #get width and height of img
    height, width = image.shape[:2]
    #set up initial variable states
    total = 0
    last_pos = contour[0][0]
    count = 0
    loop = 1
    while loop < len(contour)-1:
        if misc_fun.distance(last_pos, contour[loop][0]) > 5:
            #get angle between two points in contour
            angle = misc_fun.degrees(contour[loop-1][0], contour[loop+1][0])
            #generate angles either side
            angle_1 = misc_fun.degrees_limit_range(angle + 90)
            angle_2 = misc_fun.degrees_limit_range(angle - 90)
            #generate two points either side of contour at 90 degree angles
            point_1 = misc_fun.point_distance(contour[loop][0], 10, angle_1)
            point_2 = misc_fun.point_distance(contour[loop][0], 10, angle_2)          
            #check that points are not outside the image
            if point_1[0] > width-1:
                point_1[0] = width-1
            if point_1[1] > height-1:
                point_1[1] = height-1
            if point_2[0] > width-1:
                point_2[0] = width-1 
            if point_2[1] > height-1:
                point_2[1] = height-1          
            #calculate difference for target channel or for greyscale image
            if channel is not None:
                values_1 = numpy.array([int(image[point_1[1]][point_1[0]][0]),
                            int(image[point_1[1]][point_1[0]][1]),
                            int(image[point_1[1]][point_1[0]][2])])
                values_2 = numpy.array([int(image[point_2[1]][point_2[0]][0]),
                            int(image[point_2[1]][point_2[0]][1]),
                            int(image[point_2[1]][point_2[0]][2])])
                #calculate difference between inside and out adjusting for mean
                dif_1 = values_1[channel]/float(values_1.mean())
                dif_2 = values_2[channel]/float(values_2.mean())
                #dif_1 = background
                dif_ratio = dif_2/float(dif_1)
                #add to total
                total += dif_ratio                
            else:
                #this is the contrast for a black and white background
                grey_dif = abs(int(image[point_1[1]][point_1[0]][0]) - int(image[point_2[1]][point_2[0]][0]))
                #add ratio to total
                total += grey_dif              
            #update last position
            last_pos = contour[loop][0]
            count += 1
        loop += 1
    #adjust total by count
    out = total / float(count)    
    #return
    return out  


def contour_pt_angle(contour, pos, angle): 
    
    """
    DESCRIPTION
    This function finds the edge of a contour at a specified angle from a 
    specified starting point. If it fails to find the edge of the contour then
    it returns None.
    
    INPUT
    contour = a contour in standard opencv format
    pos = the starting xy coordinate
    angle = the angle at which to search for the edge of the contour
    
    OUTPUT
    out = the target xy coordinate  
    """
    
    #init an empty output variable
    out = None
    #generate a black image with the contour drawn in white
    img = numpy.zeros((5000,5000,3), numpy.uint8)
    cv2.drawContours(img, [contour], -1, (255,255,255), -1)
    #loop through distances until edge of contour is found
    for x in range(5, 1000):
        #generate the xy coordinate
        new_pt = misc_fun.point_distance(pos, x, angle + 180)
        #check if it has moved outside the contour
        if img[new_pt[1]][new_pt[0]][0] == 0:
            out = new_pt
            break
    #return
    return out



#"""
#This is another version of the even spaces function but starts at the start of
#the contour and ends at the end.
#"""
#    
#def contour_even_spaces_open(contour, number):
#    #create double contour
#    double_cnt = numpy.concatenate((contour, contour), axis=0)
#    #calculate distance spacing
#    length = cv2.arcLength(contour,False)
#    dist = length/float(number)    
#    #generate new_contour
#    new_contour = [[contour[0][0]]]
#    closest = 0
#    #add each of the new required points
#    loop_2 = 1
#    while loop_2 < number+1:
#        #calculate distance for next point
#        distance_1 = dist*loop_2#distance forward for point to be placed
#        #find two points either side of location
#        point_a, point_b, min_dist = distance_spacers(double_cnt, distance_1, closest)        
#        #generate new position
#        distance_2 = distance_1-min_dist
#        angle = angleTwo(point_a, point_b)
#        new_pt = pointPos(point_a, distance_2, angle+180)
#        #add new_pt to new_contour
#        new_contour += [[new_pt]]
#        loop_2 += 1
#    #convert new_contour to numpy.array
#    new_contour = numpy.array(new_contour) 
#    return new_contour       


def contour_even_spacing(contour, number):
    
    """
    DESCRIPTION
    This function restructures an input contour so that has the specified 
    number of points and that they are evenly spaced around the contour.
    
    INPUT
    contour = a contour in standard opencv format
    number = the number of points to include in the contour
    
    OUTPUT
    contour_new = a contour in standard opencv format
    """

    #create a couble length contour to loop around
    contour_double = numpy.concatenate((contour, contour), axis=0)
    #calculate the perimeter of the contour
    perimeter = cv2.arcLength(contour, True)
    #calculate the step distance
    step_distance = perimeter/float(number + 1)
    #initialize a new contour
    contour_new = []
    #add the starting point
    contour_new += [contour[0]]
    #add each of the new points
    for x in range(number):
        #generate the point
        point_new = point_perimeter(contour_double, x*step_distance)
        #add to the new contour
        contour_new += [point_new]
    #convert contour_new to a numpy array
    contour_new = numpy.array(contour_new)
    #return
    return contour_new


def contour_width(contour):
    
    """
    DESCRIPTION
    This function measures the width of the contour on the x axis.
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT
    contour_width = the width of the contour in pixels
    """
    
    #get contour bounding box
    x,y,w,h = cv2.boundingRect(contour)    
    #return
    return w        


def contour_smooth(contour, ratio):
    
    """
    DESCRIPTION
    This function smooths a contour. To do this it looks for regions where the 
    distance around is greater than the distance acrose a gap. A threshold can 
    be set to define a maximum distance around relative to distance across.
    This threshold ranges from 0 to 1. 0 = less smooth 1 = more smooth.
    
    INPUT
    contour = a contour in standard opencv format
    ratio = a ratio from 0 to 1 defining how far across should be accepted
    
    OUTPUT
    output = a contour in standard opencv format
    """
    
    contour = contour.tolist()    
    #set distance to check in backwards direction
    dist = int(len(contour)*0.02)
    #run through and smooth the contour
    loop_1 = 2
    while loop_1 < dist:
        loop_2 = dist
        while loop_2 < len(contour):
            section = contour[loop_2-loop_1:loop_2]
            total_dist = cv2.arcLength(numpy.array(section),False)
            across_dist = misc_fun.distance(section[0][0], section[-1][0])
            if across_dist / float(total_dist) < ratio:
                del contour[loop_2-(loop_1+1):loop_2]
            loop_2 += 1
        loop_1 += 1 
    #output 
    output = numpy.array(contour)
    #return the smoothed contour           
    return output


def contour_ROI(image, contour):
    
    """
    DESCRIPTION
    This function selects the region of interested for a contour.
    
    INPUT
    image = an image in standard opencv format
    contour = a contour in standard opencv format
    
    OUTPUT
    image_ROI = an image in standard opencv format
    """
    
    #calculate the bounding box for the contour
    x,y,w,h = cv2.boundingRect(contour)
    #place bounding box values into a list
    r = [x,y,w,h]
    #slice the ROI from the image
    image_ROI = image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]     
    #return
    return image_ROI
  

def contours_overlap(contour_1, contour_2):
    
    """
    DESCRIPTION
    This function calculates proportion of two contours that are not overlaping
    relative to the area of each contour. It returns the average of the two 
    values. The closer this number is to zero the better the overlapp between
    the two contours. If it fails it returns None.
    
    INPUT
    contour1 = a contour in standard opencv format
    contour2 = a contour in standard opencv format
    
    OUTPUT
    output = the proportion of the contours not overlapping
    """
    
    #generate picture of overlap for each version
    blank1 = numpy.zeros((5000,5000,1), numpy.uint8)
    cv2.drawContours(blank1, [contour_1], 0, (255), -1)
    cv2.drawContours(blank1, [contour_2], 0, (0), -1)
    beyond_1 = cv2.countNonZero(blank1)
    blank2 = numpy.zeros((5000,5000,1), numpy.uint8)
    cv2.drawContours(blank2, [contour_2], 0, (255), -1)
    cv2.drawContours(blank2, [contour_1], 0, (0), -1)
    beyond_2 = cv2.countNonZero(blank2)

    #calculate area of the contours
    area_1 = cv2.contourArea(contour_1)
    area_2 = cv2.contourArea(contour_2)
    
    #proportion overlap
    overlap_1 = beyond_1 / float(area_1)
    overlap_2 = beyond_2 / float(area_2)
    overlap_avg = (overlap_1 + overlap_2) / float(2)
    #return
    return overlap_avg   


def contour_extreme_pts(contour, axis, min_limit, max_limit):
    
    """
    DESCRIPTION
    This function returns the xy coordinate point that is the most extreme for
    a given axis.
    
    INPUT
    contour = a contour in standard opencv format
    axis = 0 or 1 (x or y)
    min_limit = the minimum cutoff point (proportion of axis)
    max_limit = the maximum cutoff point (proportion of axis)
    
    OUTPUT
    out = the xy coordinate at the designated axis
    """

    #initialize an empty out
    out = None
    #get min value
    min_value = min([x[0][axis] for x in contour])
    #get max value
    max_value = max([x[0][axis] for x in contour])
    #set below and above limits
    above = min_value + (max_value-min_value)*min_limit
    below = min_value + (max_value-min_value)*max_limit
    #filter using list comprehension
    out = [x for x in contour if above <= x[0][axis] <= below]
    #return
    return numpy.array(out)


def contour_resize(contour, ratio):
    
    """
    DESCRIPTION
    This function resizes a contour by a defined ratio. The contour is resized
    with the center point of the contour remaining the same.
    
    INPUT
    contour = a contour in standard opencv format
    ratio = the resize ratio of the contour
    
    OUTPUT
    contour_out = a contour in standard opencv format
    """

    #get contour center
    center = contour_center(contour)
    #initialize new contour
    contour_out = []
    #loop through points
    for point in contour:
        #calculate new z
        x = int(((point[0][0] - center[0])*ratio) + center[0])
        #calculate new y
        y = int(((point[0][1] - center[1])*ratio) + center[1])
        #add to contour_out
        contour_out += [[[x, y]]]    
    #return
    return numpy.array(contour_out)   


def ref_common_two(contour_1, contour_2):
    
    """
    DESCRIPTION
    This function finds two points to use as references when aligning two 
    contours. The current version finds center of mass and left hand extreme 
    point of ellipse around the contour.
    
    INPUT
    contour_1 = a contour in standard opencv format
    contour_2 = a contour in standard opencv format
    
    OUTPUT
    ref_1 = the first xy reference point coordinates
    ref_2 = the second xy reference point coordinates
    """
      
    #check if contours are numpy arrays
    contour_1 = numpy.array(contour_1)    
    contour_2 = numpy.array(contour_2)      
    #find angle of contour_1
    angle_1 = contour_angle(contour_1)
    #calculate distance based on size
    dist = max(cv2.minAreaRect(contour_1)[1])/float(2)
    #get center of contour_1
    center_1 = contour_center(contour_1)
    #generate first two points
    point_1a = misc_fun.point_distance(center_1, dist, angle_1)
    point_1b = misc_fun.point_distance(center_1, dist, angle_1+180)
    
    #find angle of contour_1
    angle_2 = contour_angle(contour_2)
    #calculate distance based on size
    dist = max(cv2.minAreaRect(contour_2)[1])/float(2)
    #get center of contour_1
    center_2 = contour_center(contour_2)
    #generate first two points
    point_2a = misc_fun.point_distance(center_2, dist, angle_2)
    point_2b = misc_fun.point_distance(center_2, dist, angle_2+180) 
    #define to output ref lists
    ref_1 = [point_1a, point_1b]
    ref_2 = [point_2a, point_2b]
    #return
    return ref_1, ref_2


def ref_common_three(contour_1, contour_2):
    
    """
    DESCRIPTION
    This function finds three points to use as a references when aligning two 
    contours. The current version finds center of mass, left hand extreme 
    point of ellipse around the contour. The third point is then at a standard
    distance 90 degrees from the previous two points.
    
    INPUT
    contour_1 = a contour in standard opencv format
    contour_2 = a contour in standard opencv format
    
    OUTPUT
    points_1 = a list of three xy coordinates for the first contour
    points_2 = a list of three xy coordinates for the second contour
    """
    
    contour_1 = numpy.array(contour_1)    
    contour_2 = numpy.array(contour_2)      
    #find angle of contour_1
    angle_1 = contour_angle(contour_1)
    #get size of contour_1
    size_1 = cv2.contourArea(contour_1)
    #calculate distance based on size
    dist = math.sqrt(size_1/3.1416)
    #get center of contour_1
    center_1 = contour_center(contour_1)
    #generate first two points
    point_1a = misc_fun.point_distance(center_1, dist, angle_1)
    point_1b = misc_fun.point_distance(center_1, dist, angle_1+180)
    #generate third point
    angle = misc_fun.degrees(point_1a, point_1b)
    center = misc_fun.point_mid(point_1a,point_1b, 0.5)
    point_1c = contour_pt_angle(contour_1, center, angle-90)    
    #find angle of contour_1
    angle_2 = contour_angle(contour_2)
    #get size of contour_1
    size_2 = cv2.contourArea(contour_2)
    #calculate distance based on size
    dist = math.sqrt(size_2/3.1416)
    #get center of contour_1
    center_2 = contour_center(contour_2)
    #generate first two points
    point_2a = misc_fun.point_distance(center_2, dist, angle_2)
    point_2b = misc_fun.point_distance(center_2, dist, angle_2+180)
    #generate third point
    angle = misc_fun.degrees(point_2a, point_2b)
    center = misc_fun.point_mid(point_2a, point_2b, 0.5)
    point_2c = contour_pt_angle(contour_2, center, angle-90)
    #combine three points
    points_1 = [point_1a, point_1c, point_1b]     
    points_2 = [point_2a, point_2c, point_2b]
    return points_1, points_2


def ref_bounding(contour):
    
    """
    DESCRIPTION
    This function generates three reference points based on a fitted bounding 
    box around an input contour. Consequently it can be used as a universal 
    referencing system for a variety of shapes. It gives similar but slightly
    different results to ref_common_three()
    
    INPUT
    contour = a contour in standard opencv format
    
    OUTPUT
    ref_1 = the first xy coordinate
    ref_2 = the second xy coordinate
    ref_3 = the third xy coordinate
    """
    
    #get fitted bounding box and convert to box
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    #convert to nested list
    box_list = []
    for x in box:
        box_list += [[x[0],x[1]]]
    #
    box_list.sort(key=lambda x: int(x[0]))
    first_list = box_list[:2]
    first_list.sort(key=lambda x: int(x[1]))
    second_list = box_list[2:]
    second_list.sort(key=lambda x: int(x[1]))
    #select the three reference points
    ref_1 = first_list[1]
    ref_2 = first_list[0]
    ref_3 = second_list[0]
    #orientate for longest axis
    #check which is the longest axis
    if misc_fun.distance(ref_1, ref_2) > misc_fun.distance(ref_2, ref_3):
        out = [ref_1, ref_2, ref_3]
    else:
        out = [ref_3, ref_2, ref_1] 
    #return
    return out   


def morph_bounding_dist(contour, points, angle): 
    
    """
    DESCRIPTION
    This function finds the xy coordinates for a list of morphometric points. 
    It uses two ref points to orientate and then finds points along the the 
    edge of an input contour which are at a defined angle. 
    
    INPUT
    contour = a contour in standard opencv format
    points = a list of proportions at which to take measurements = [0.1, 0.5, 1]
    angle = the angle at which to take samples
    
    OUTPUT
    new_contour = a standard opencv contour which contains the xy morphometric points
    new_stats = distance to center line for each of the morphometric points
    """

    #get the contour center
    center = contour_center(contour)    
    #generate the two reference points
    ref_1B, ref_2B, ref_3B = ref_bounding(contour)
    #get the angle
    ref_angle = misc_fun.degrees(ref_1B, ref_2B)
    #get the two ref points
    ref_1 = contour_pt_angle(contour, center, ref_angle)
    ref_2 = contour_pt_angle(contour, center, ref_angle-180)   
    #correct the target angle using the reference angle
    angle_corrected = angle + ref_angle
    #set up new contour and stats lists
    new_contour = [] 
    #loop through points and find required xy coordinates
    loop = 0
    while loop < len(points):
        #generate line point
        dist = points[loop]
        mid_pt = misc_fun.point_mid(ref_1, ref_2, dist)
        #find point at specified angle
        out_pt = contour_pt_angle(contour, mid_pt, angle_corrected)
        new_contour += [[out_pt]]
        loop += 1
    #return
    return numpy.array(new_contour)


def morph_bounding_radial(contour, angles): 
    
    """
    DESCRIPTION
    This function finds the xy coordinates for a list of morphometric points. 
    It uses two ref points to orientate and then finds the morphometric points
    for a set of defined angles. 
    
    INPUT
    contour = a contour in standard opencv format
    angles = a list of angles at which to get morphometric points
    
    OUTPUT
    new_contour = a standard opencv contour which contains the xy morphometric points
    """

    #initiate empty output list
    new_contour = []
    #get the contour center
    center = contour_center(contour)    
    #generate the two reference points
    ref_1B, ref_2B, ref_3B = ref_bounding(contour)
    #get the angle
    ref_angle = misc_fun.degrees(ref_1B, ref_2B)
    #loop through all angles and generate points
    for pos in angles:
        #generate corrected angles
        angle_corrected = pos + ref_angle
        #get point
        point = contour_pt_angle(contour, center, angle_corrected)
        #add to output data
        new_contour += [[point]]
    #return
    return numpy.array(new_contour)


def affine_matrix(points_A, points_B):
    
    """
    DESCRIPTION
    This function generates an affine matrix that can convert the points in 
    points_B to the same postion as points in points_A.
    
    INPUT
    points_A = a list of three xy reference point coordinates
    points_B = a list of three xy reference point coordinates
    
    OUTPUT
    matrix = an opencv affine transformation matrix
    """    

    old = numpy.array([(points_B[0][0], points_B[0][1]),
                       (points_B[1][0], points_B[1][1]),
                       (points_B[2][0], points_B[2][1])],
                       numpy.float32)
    new = numpy.array([(points_A[0][0], points_A[0][1]),
                       (points_A[1][0], points_A[1][1]),
                       (points_A[2][0], points_A[2][1])],
                       numpy.float32)
    #get matrix
    matrix = cv2.getAffineTransform(old, new)
    #return
    return matrix 


def affine_apply(matrix, point):
    
    """
    DESCRIPTION
    This function uses the matrix generated by affine_matrix to transform an
    input xy coordinate point to a new position.
    
    INPUT
    matrix = an affine transformation matrix
    point = the input xy coordinate
    
    OUTPUT
    point_new = the transformed xy coordinate
    """
    
    #generate x and y coordinate
    new_x = matrix[0][0] * point[0] + matrix[0][1] * point[1] + matrix[0][2]
    new_y = matrix[1][0] * point[0] + matrix[1][1] * point[1] + matrix[1][2]  
    #combine into single point
    point_new = [new_x, new_y]
    #return
    return point_new


def ref_affine_random(pattern_1, pattern_2):
    
    """
    DESCRIPTION
    This function finds two points to use as affine transformation references
    randomly from two patterns.
    
    INPUT
    pattern_1 = the first set of xy coordinates
    pattern_2 = the second set of xy coordinates
    
    OUTPUT
    points_1 = the reference points for pattern_1
    points_2 = the reference points for pattern_2     
    """

    #select two random points without replacement
    pos_1 = numpy.random.choice(range(len(pattern_1)), size = 2, replace = False)
    pos_2 = numpy.random.choice(range(len(pattern_2)), size = 2, replace = False)  
    #get the xy coordinates
    points_1 = [pattern_1[pos_1[0]], pattern_1[pos_1[1]]]
    points_2 = [pattern_2[pos_2[0]], pattern_2[pos_2[1]]]
    #return points_1, points_2
    return points_1, points_2


def ref_affine_radius(pattern_1, pattern_2, perm, radius_drop_off, match_attempts):
    
    """
    DESCRIPTION
    This function finds two points to use as affine transformation references
    within a given radius for two patterns. Currently, it selects two random
    points in the first pattern and then uses a combination of parameters to 
    try and select the matching points in the second pattern.
    
    THOUGHTS FOR FURTHER DEVELOPMENT
    > If these points should be a similar distance apart in both 
    patterns...so they do not create different sized patterns
    > This function should not just select the closest dist match, but 
    have random chance within a target range.
    > Should try and select refs at each end of the pattern as these 
    would have a lower error rate.
    > Should use points which are larger and more isolated as these are
    less likely to overlap incorrectly.
    
    INPUT
    pattern_1 = the first set of xy coordinates
    pattern_2 = the second set of xy coordinates
    radius = the maximum distance to look for matching reference points
    
    OUTPUT
    points_1 = the reference points for pattern_1
    points_2 = the reference points for pattern_2 
    """
    
    #get length of pattern_1 along longest axis
    ref = ref_bounding(numpy.array(pattern_1))
    dist_max = misc_fun.distance(ref[0], ref[2])
    
    #run for a set number of permutations
    for x in range(perm):
        #select two random points in pattern_1
        pos_1 = numpy.random.choice(range(len(pattern_1)), size = 2, replace = False)
        #generate list of distances from these points to those in pattern_2
        dist_1 = [misc_fun.distance(pattern_1[pos_1[0]], x) for x in pattern_2]
        dist_2 = [misc_fun.distance(pattern_1[pos_1[1]], x) for x in pattern_2]
        #convert distances to probabilities based on radius_drop_off
        prob_1 = [x/float(dist_max) for x in dist_1] 
        prob_2 = [x/float(dist_max) for x in dist_2]
        
        #try find match within radius
        pos_2 = None
        for x in range(match_attempts):
            #select random position
            test_pos_2 = numpy.random.choice(range(len(pattern_2)), size = 2, replace = False)
            #calculate combined probability for both ref points
            total_prob = prob_1[test_pos_2[0]] + prob_2[test_pos_2[1]]
            #generat random value between 0 and 2
            value = random.uniform(0, 2)
            #if it passes probability limit break 
            if total_prob < value*radius_drop_off:
                pos_2 = test_pos_2
                break           
        #if failed to find points within radius get closest points instead
        if pos_2 is None:
            pos_2 = [prob_1.index(min(prob_1)), prob_2.index(min(prob_2))]
        #get xy coordinates for both sets of points
        points_1 = [pattern_1[pos_1[0]], pattern_1[pos_1[1]]]
        points_2 = [pattern_2[pos_2[0]], pattern_2[pos_2[1]]]
        
        #check that a ref point has not been selected twice
        dist_1 = misc_fun.distance(points_1[0], points_1[1])
        dist_2 = misc_fun.distance(points_2[0], points_2[1])
        #if sufficient quality break loop and return points
        if dist_1 > 0 and dist_2 > 0:
            break
        
    #return
    return points_1, points_2


def ref_affine_triangle(pattern_1, pattern_2, perm, dist_dif):
    
    """
    DESCRIPTION
    This function locates three ref points to use when aligning two lists of xy 
    points. It finds the best ref points by locating three points in each list
    by comparing the triangle created by the three points. Length of the sides
    relative to the total circumference is used as the primary measure because
    it is size independant. This function requires that the lists are 
    orientated roughly in the same direction.
    
    THOUGHT: should try an angle based version of this to see if it is faster
    
    INPUT
    pattern_1 = the first set of xy coordinates
    pattern_2 = the second set of xy coordinates
    perm = the number of attempts to make when finding reference points
    
    OUTPUT
    triangle_1 = the first set of reference points
    triangle_2 = the second set of reference points
    """
    
    #for required permutations try and find a set of matching points
    for x in range(perm):
        #get three points from pattern_1 without replacement
        pos_1 = numpy.random.choice(range(len(pattern_1)), size = 3, replace = False)
        #select three matching points from pattern_2 
        pos_2 = numpy.random.choice(range(len(pattern_2)), size = 3, replace = False)
        #select triangle points
        triangle_1 = [pattern_1[pos_1[0]], pattern_1[pos_1[1]], pattern_1[pos_1[2]]]
        triangle_2 = [pattern_2[pos_2[0]], pattern_2[pos_2[1]], pattern_2[pos_2[2]]]                    
        #sort triangles based on x axis
        triangle_1.sort()
        triangle_2.sort()
        #get circumference of triangle
        circ_1 = cv2.arcLength(numpy.array(triangle_1), True)
        circ_2 = cv2.arcLength(numpy.array(triangle_2), True)
        #check triangle shape by comparing distances of each point
        dist_1a = misc_fun.distance(triangle_1[0], triangle_1[1])/float(circ_1)
        dist_2a = misc_fun.distance(triangle_2[0], triangle_2[1])/float(circ_2)
        if dist_2a*(1-dist_dif) < dist_1a < dist_2a*(1+dist_dif):
            dist_1b = misc_fun.distance(triangle_1[1], triangle_1[2])/float(circ_1)
            dist_2b = misc_fun.distance(triangle_2[1], triangle_2[2])/float(circ_2)
            if dist_2b*(1-dist_dif) < dist_1b < dist_2b*(1+dist_dif):
                dist_1c = misc_fun.distance(triangle_1[2], triangle_1[0])/float(circ_1)
                dist_2c = misc_fun.distance(triangle_2[2], triangle_2[0])/float(circ_2)
                if dist_2c*(1-dist_dif) < dist_1c < dist_2c*(1+dist_dif):
                    break
    #return
    return triangle_1, triangle_2


def ref_affine_third(ref_1, ref_2):
    
    """
    DESCRIPTION
    This function generates a third position for a given set of two refs. This 
    third position is needed for affine transformation calculations, but does
    not contain any new information.
    
    INPUT
    ref_1 = an xy coordinate for the first ref point
    ref_2 = an xy coordinate for the second ref point
    
    OUTPUT
    out = an xy coordinate for the new third ref point
    """
    
    #calculate the angle between two reference points
    angle = misc_fun.degrees(ref_1, ref_2)
    #calculate the distance between two reference points
    dist = misc_fun.distance(ref_1, ref_2)/float(3)
    #generate the third reference point
    pointA = [(ref_1[0]+ref_2[0])/float(2),(ref_1[1]+ref_2[1])/float(2)]
    out = misc_fun.point_distance(pointA, dist, 360+angle-90)
    out[0] = int(out[0])
    out[1] = int(out[1])
    #return
    return out  


def align_contours(contour_1, contour_2, method):
    
    """
    DESCRIPTION
    This function aligns contour_2 to contour_1 using an affine transformation
    and either 2 or 3 common_ref_points. One limitation of this method is that
    the contour must be 5 points or more in length.
    
    INPUT
    contour_1 = a contour in standard opencv format
    contour_2 = a contour in standard opencv format
    method = either 'two' or 'three' to indicate the reference type to use.
    
    OUTPUT
    new_contour = a contour in standard opencv format
    """    
    
    #break if either contour is less than 5 points in length
    if len(contour_1) < 5:
        return None
    if len(contour_2) < 5:
        return None
    #check if the ref contour has double nested lists or not...it should
    if len(contour_2[0]) > 1:
        contour_2 = [[x] for x in contour_2]
    #generate the ref_sets for the two contours
    if method == 'two':
        ref_set_1, ref_set_2 = ref_common_two(contour_1, contour_2)
        ref_set_1 += [ref_affine_third(ref_set_1[0], ref_set_1[1])]
        ref_set_2 += [ref_affine_third(ref_set_2[0], ref_set_2[1])]
    elif method == 'three':
        ref_set_1, ref_set_2 = ref_common_three(contour_1, contour_2)
    #use a two point affine transformation to transform contour_2 to contour_1    
    old = numpy.array([(ref_set_1[0][0],ref_set_1[0][1]),
                       (ref_set_1[1][0],ref_set_1[1][1]),
                       (ref_set_1[2][0],ref_set_1[2][1])], numpy.float32)
        
    new = numpy.array([(ref_set_2[0][0],ref_set_2[0][1]),
                       (ref_set_2[1][0],ref_set_2[1][1]),
                       (ref_set_2[2][0],ref_set_2[2][1])], numpy.float32)
        
    affine = cv2.getAffineTransform(new, old)
    #convert contour_2 to cotnour_1 space using affine
    new_contour = []
    for x in contour_2:
        new_x = affine[0][0] * x[0][0] + affine[0][1] * x[0][1] + affine[0][2]
        new_y = affine[1][0] * x[0][0] + affine[1][1] * x[0][1] + affine[1][2]
        new_contour.append([[int(new_x), int(new_y)]])
    #convert new contour to numpy array
    new_contour = numpy.array(new_contour)
    #return
    return new_contour


def align_contour_common(contour, ref_points):

    """
    DESCRIPTION
    This function aligns a contour to a common-space position based on two 
    reference points for the input contour and predefined ref point positions 
    for common space (e.g. [[50,500],[1050,500]]). Common-space can be used if
    you want to overlap many images to compare their shape and so that stored
    shapes can be prepositioned to overlap.
    
    INPUT
    contour = a contour in standard opencv format
    ref_points = list containing the nose and peduncle tail xy coordinates
    
    OUTPUT
    new_contour = a contour in standard opencv format
    """
    
    #check if the ref contour has double nested lists or not...it should
    if len(contour[0]) > 1:
        contour = [[x] for x in contour]
    #generate the ref_sets for the two contours
    ref_common = [[50,500],[1050,500]]      
    ref_common += [ref_affine_third(ref_common[0], ref_common[1])]
    ref_points += [ref_affine_third(ref_points[0], ref_points[1])] 
    #use a two point affine transformation to transform contour_2 to contour_1    
    old = numpy.array([(ref_common[0][0],ref_common[0][1]),
                       (ref_common[1][0],ref_common[1][1]),
                       (ref_common[2][0],ref_common[2][1])], numpy.float32)
    new = numpy.array([(ref_points[0][0],ref_points[0][1]),
                       (ref_points[1][0],ref_points[1][1]),
                       (ref_points[2][0],ref_points[2][1])], numpy.float32)
    affine = cv2.getAffineTransform(new, old)
    #convert contour_2 to cotnour_1 space using affine
    new_contour = []
    for x in contour:
        new_x = affine[0][0] * x[0][0] + affine[0][1] * x[0][1] + affine[0][2]
        new_y = affine[1][0] * x[0][0] + affine[1][1] * x[0][1] + affine[1][2]
        new_contour.append([[int(new_x), int(new_y)]])
    new_contour = numpy.array(new_contour)
    #return transformed contour
    return new_contour


def colour_clahe(image, clip_limit, grid_size):
    
    """
    DESCRIPTION
    This function carries out a clahe histogram equalization for colour images.
    To do this it converts to LAB space and then back to BGR space
    
    INPUT
    image = a standard opencv bgr scale image
    clip_limit = clahe clip limit (often set to 2)
    grid_size = clahe grid size (often set to 9)
    
    OUTPUT
    image_out = a standard opencv bgr scale image
    """

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)    
    lab_planes = cv2.split(lab)    
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size,grid_size))    
    lab_planes[0] = clahe.apply(lab_planes[0])    
    lab = cv2.merge(lab_planes)    
    image_out = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    #return 
    return image_out  


def filter_contours_cluster(contours, size, number):
    
    """
    DESCRIPTION
    This function filters the contours in a contour list based on the distance
    to the largest cluster within the contours list. A two part procedure is 
    used to do this. First the largest cluster within the contours is 
    identified and then each point is filtered based on distance to the 
    cluster.
    
    contours which haver a lower average distance to other clusters will be 
    closer to the main cluster.
    
    INPUT
    contours = a contour list in standard opencv format
    size = the kernal size to use for dilation
    number = the iterations to use for dilation
    
    OUTPUT
    contours_out = a contour list in standard opencv format
    """
    
    #initialize a background image
    blank1 = numpy.zeros((2000,2000,1), numpy.uint8)  
    #draw contours onto image in white
    cv2.drawContours(blank1, contours, -1, 255, -1)
    #dilate contours to a target level which overlaps the cluster
    kernel = numpy.ones((size,size), numpy.uint8)
    dilation = cv2.dilate(blank1, kernel, iterations = number)
    #select the largest contour from the dilation image
    ret, img_mask = cv2.threshold(dilation, 100, 255, cv2.THRESH_BINARY) 
    clusters ,hierarchy = cv2.findContours(img_mask, 1,2)   
    #select the largest contour as the largest cluster
    if len(clusters) > 0:
        cluster_max = max([cv2.contourArea(x) for x in clusters])
    else:
        cluster_max = 0
    #filter contours to get the largest cluster
    cluster = [x for x in clusters if cv2.contourArea(x) == cluster_max]
    #filter out any contours which are not found inside the cluster
    contours_out = []
    for contour in contours:
        #find center point
        center = contour_center(contour)
        #test contour is within cluster
        dist = cv2.pointPolygonTest(cluster[0],(center[0],center[1]), True)
        #keep if it is within cluster
        if dist > 0:
            contours_out += [contour] 

#    #remove contours which have centers outside the             
#    cv2.drawContours(dilation, cluster, -1, 125, -1)
#    cv2.drawContours(dilation, contours_out, -1, 0, -1)
#    resized = cv2.resize(dilation, (500, 500))
#    cv2.imshow('final_image', resized)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()             
                        
    #return
    return contours_out


def filter_contours_largest(contours, number):
    
    """
    DESCRIPTION
    This function filters a list of contours to only retain the largetst x 
    number of contours
    
    INPUT
    contours = contours in a standard opencv format
    number = the number of contours to keep
    
    OUTPUT
    contours_out = contours in a standard opencv format
    """
    
    #an empty list to add contours two
    contours_out = []    
    #an empty list for area information
    area_info = []    
    #loop through each contour
    for key, item in enumerate(contours):
        #calculate area
        area = cv2.contourArea(item)
        #area_info
        area_info += [[area, key]]
    #sort the area info
    area_info.sort()
    #get the two largest x contours
    for item in area_info[-number:]:
        contours_out += [contours[item[1]]]
    #return
    return numpy.array(contours_out)    


def filter_contours_most_circular(contours, number):
    
    """
    DESCRIPTION
    This function filters a list of contours to keep a designated number of the
    most circular contours.
    
    INPUT
    contours = contours in a standard opencv format
    number = the number of contours to return
    
    OUTPUT
    contours_out = contours in a standard opencv format
    """
    
    #an empty list to add contours two
    contours_out = []    
    #an empty list for area information
    area_info = []    
    #loop through each contour
    for key, item in enumerate(contours):
        #calculate area
        area = contour_circularity_radius(item)
        #area_info
        area_info += [[area, key]]
    #sort the area info
    area_info.sort()
    #get the two largest x contours
    for item in area_info[-number:]:
        contours_out += [contours[item[1]]]
    #return
    return numpy.array(contours_out)


def filter_contours_size(contours, limit_min, limit_max):
      
    """
    DESCRIPTION
    This function filters a list of contours to remove any that are not within
    a designated size range
    
    INPUT
    contours = contours in a standard opencv format
    limit_min = the minimum size
    limit_max = the maximum size
    
    OUTPUT
    contours_out = contours in a standard opencv format
    """
    
    #filter using list comprehension
    contours_out = [x for x in contours if limit_min <= cv2.contourArea(x) <= limit_max]
    #return
    return numpy.array(contours_out)


def filter_contours_circularity(contours, limit_min, limit_max):
    
    """
    DESCRIPTION
    This function filters a list of contours to remove any that are not within
    a designated circularity range
    
    INPUT
    contours = contours in a standard opencv format
    limit_min = the minimum circularity
    limit_max = the maximum circularity
    
    OUTPUT
    contours_out = contours in a standard opencv format
    """
    
    #filter using list comprehension
    contours_out = [x for x in contours if limit_min <= contour_circularity_radius(x) <= limit_max]
    #return
    return numpy.array(contours_out)
 

def filter_contours_region(contours, region):

    """
    DESCRIPTION
    This function filters a list of contours to remove any that are not located
    within a defined region. To be considered within the region the center of
    each contour must be located within the region. The region is defined using
    a standard opencv contour
    
    INPUT
    contours = contours in a standard opencv format
    region = a contour in standard opencv format
    
    OUTPUT
    contours_out = contours in a standard opencv format
    """    
    
    #define new contours list
    contours_out = []
    #loop through contours
    for item in contours:
        #get center
        center = contour_center(item)
        #run test
        dist = cv2.pointPolygonTest(region, (center[0], center[1]), True)
        #add to out
        if dist >= 0:
            contours_out += [item]
    #return
    return numpy.array(contours_out)


def contour_to_profile(contour, ref_point):
    
    """
    DESCRIPTION
    This function converts a contour to a linear profile similar to a line 
    graph. The x coordinate is distance around the contour from the starting 
    point. The y coordiante is the distance from the point to the ref_point. 
    Typically the ref_point would be the center of the contour being converted.
    
    INPUT
    contour = a contour in standard opencv format
    ref_point = the position to use as the center of the profile 
    
    OUTPUT
    profile = a linear profile of the contour [[x,y],[x,y],[x,y]]    
    """
    
    #init empty list for profile
    profile = []
    #init distance around variable
    around = 0
    #convert xy points of the contour to a linear profile
    loop = 0
    while loop  < len(contour):
        #calculate distance to center
        value = misc_fun.distance(ref_point, contour[loop][0])
        #update distance around
        around = cv2.arcLength(contour[:loop+1], False)
        #update profile
        profile += [[around, value]]
        loop += 1     
    #return
    return profile


def circle_radius(contour, radius, points):
    
    """
    DESCRIPTION
    This function generates a circle with a defined radius and number of 
    points.
    
    INPUT
    center = the center point to build the circle around
    radius = the radius of the circle to build 
    points = the number of points 
    
    OUTPUT
    circle = a contour in standard opencv format
    """
    
    #initiate and empty circle list
    circle = [] 
    #get center
    center = contour_center(contour)
    #create a list of points to generate
    angles = numpy.linspace(0, 360, points)
    angles = [int(x) for x in angles]
    #look through each point and generate point
    for item in angles:
        #generate point
        pos = misc_fun.point_distance(center, radius, item)
        #add to circle
        circle += [[pos]]
    #check that circle is a numpy array
    circle = numpy.array(circle)
    #return
    return circle


def profile_largest_triangle(profile, permutations):
    
    """
    DESCRIPTION
    This function finds the largest inverted triangle in a profile.
    
    INPUT
    profile = the profile generated based on a contour
    permutations = the number of iterations to search for
    
    OUTPUT
    best_triangle = a contour in standard opencv format
    """

    #set up empty best_tri
    best_triangle = None
    best_size = 0
    #run for a set number of permutations
    for x in range(permutations):
        #select three points
        pos = numpy.random.choice(len(profile), 3, replace = False)
        #sort positions based on x axis
        pos = numpy.sort(pos)
        #skip triangles with center point at top
        if profile[pos[0]][1] > profile[pos[1]][1]:
            if profile[pos[2]][1] > profile[pos[1]][1]:   
                #get triangle
                triangle = numpy.array([[profile[pos[0]]], [profile[pos[1]]], [profile[pos[2]]]]).astype(int)                
                #get area
                area = cv2.contourArea(numpy.array(triangle))
                if area > best_size:
                    best_triangle = pos
                    best_size = area
    #return
    return best_triangle


def pattern_spacing_average(pattern):
    
    """
    DESCRIPTION
    This function checks the spacing of an input pattern of xy points.
    
    INPUT
    pattern = a set of xy coordinates in a list or array
    
    OUTPUT
    spacing_abs = the average distance between each set of spots
    spacing_profile = value to represent distortions in spacing
    """
    
    #init empty data list
    dist_list = []
    #calculate pairwise distance for each set of points
    for spot_1 in pattern:
        for spot_2 in pattern:
            #measure distance
            dist = misc_fun.distance(spot_1, spot_2)
            #add to dist_list
            if dist > 0:
                dist_list += [dist]   
    #generate statistics
    if len(dist_list) > 0:
        average = sum(dist_list)/float(len(dist_list))
        stdv = numpy.std(dist_list)
    else:
        average = 0
        stdv = 0    
    #return
    return average, stdv


def pattern_spacing_closest(pattern):

    """
    DESCRIPTION
    This function calculates the average spacing within a pattern of xy points
    between the closest points
    
    INPUT
    pattern = a set of xy coordinates in a list or array
    
    OUTPUT
    spacing_closest = the average spacing between closest points
    """       
    
    #initialize empty distance list
    dist_list = []
    
    #loop through spots
    for spot_1 in pattern:
        dist_single = []
        for spot_2 in pattern:
            #calculate the distance
            dist = misc_fun.distance(spot_1, spot_2)
            #add to dist_single
            dist_single += [dist]
        #sort list
        dist_single.sort()            
        #add closest to dist_list
        if len(dist_single) > 1:
            dist_list += [dist_single[1]]  
    #generate statistic
    if len(dist_list) > 0:
        average = sum(dist_list)/float(len(dist_list))
        stdv = numpy.std(numpy.array(dist_list))
    else:
        average = 0
        stdv = 0    
    #return
    return average, stdv 


def image_blur_subtraction(image_grey, blur_size, clahe_size):
    
    """
    DESCRIPTION
    This function creates a blurred image of the input image and then subtracts
    this from the original to identify regions of difference. It requires grey
    scale images as an input. The output subtraction based image is returned to
    the standard greyscale space (0 to 255 pixel range). A clahe histogram is 
    then applied to stabilize the pixel range.
    
    INPUT
    image_grey = an image in standard opencv format (greyscale)
    blur_size = the dimensions for the blur
    clahe_size = the dimension fo the clahe filter
    
    OUTPUT
    image_out = an image in standard opencv format (greyscale)
    """

    #blur image
    image_blur = cv2.GaussianBlur(image_grey, (blur_size, blur_size), 0)   
    #subtract blurred image from original
    subtraction = numpy.int32(image_blur) - numpy.int32(image_grey)
    #remove negative numbers
    subtraction = subtraction.clip(min=0)
    #adjust to range 
    adjusted = numpy.interp(subtraction, (subtraction.min(), subtraction.max()), (0, 255))
    #set to int
    adjusted = adjusted.astype(numpy.uint8)
    #clahe histogram correction 
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(clahe_size,clahe_size))
    adjusted = clahe.apply(adjusted) 
    #return
    return adjusted


def image_rotate(image, degrees):
    
    """
    DESCRIPTION
    This function rotates the input image by the defined degrees.
    
    INPUT
    image = an image in standard opencv format
    degrees = the number of degrees to rotate the image
    
    OUTPUT
    image_out = the rotated image
    """
    
    #get the rows and columns of the image
    shape = image.shape
    #select rows and cols
    rows = shape[0]
    cols = shape[1]
    #generate the required matrix
    M = cv2.getRotationMatrix2D((cols/2,rows/2), degrees, 1)
    #apply the affine transformation
    image_out = cv2.warpAffine(image, M, (cols,rows))
    #return
    return image_out


def images_align(image_1, image_2, iterations, terminate_eps):
    
    """
    DESCRIPTION
    This function aligns two images using the the ECC algorithm. This can be
    set to multiple motions (e.g. euclidean, affine)
    
    INPUT
    image_1 = an image in standard opencv format (greyscale)
    image_2 = an image in standard opencv format (greyscale)
    iterations = the number of iterations to attempt the match
    terminate_eps = the quality of overlap before terminating
    
    OUTPUT
    image_out = the aligned image
    """

    #set warp mode
    warp_mode = cv2.MOTION_EUCLIDEAN#cv2.MOTION_AFFINE
    warp_matrix = numpy.eye(2, 3, dtype = numpy.float32)
    
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                iterations, terminate_eps)    
    #run the ecc algorithm
    (cc, warp_matrix) = cv2.findTransformECC(image_1, image_2, warp_matrix,
                                             warp_mode, criteria)    
    #get size 
    target_shape = image_1.shape
    
    #create aligned image
    image_out = cv2.warpAffine(image_2,
                               warp_matrix,
                               (target_shape[1], target_shape[0]),
                               flags = cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                               borderMode = cv2.BORDER_CONSTANT,
                               borderValue = 0)
    
    #return
    return image_out


def image_laplacian_variance(image):
    
    """
    DESCRIPTION
    This function takes an input image and calculates the variance of the 
    laplacian function. This can be used as a measure of image blur.
    
    INPUT
    image = an image in standard opencv format (grey or colour)
    
    OUTPUT
    variance = the variance of the laplacian function 
    """
    
    #calculate the variance of the laplacian function for the image
    variance = cv2.Laplacian(image, cv2.CV_64F).var()    
    #return
    return variance
    

def image_background(image):
    
    """
    DESCRIPTION
    This function generates the mean and standard deviations each channel for 
    the background of an image. It then searches through the images to find
    the channel which is most likely the background. If there is less than a 
    difference of 10 between the averages of each channel it returns None as 
    the channel (which indicates white background)
    
    INPUT
    image = an image in standard opencv format (colour BGR or HSV)
    
    OUTPUT
    output = a dictionary of mean and standard deviation for channel
    """
    
    #initialize an empty output dictionary
    output = {}
    
    #calculate the size of the image
    height, width = image.shape[:2]

    #get top channel from each edge 3% in from border
    left_column = image[:, int(width*0.03)].tolist()
    right_column = image[:, int(width*0.97)].tolist()
    upper_line = image[int(height*0.03)].tolist()
    lower_line = image[int(height*0.97)].tolist()
    
    #merge borders 
    combined = left_column + right_column + upper_line + lower_line
    
    #split into channel lists
    combined_1 = [x[0] for x in combined]
    combined_2 = [x[1] for x in combined]
    combined_3 = [x[2] for x in combined]
    
    #calculate mean and standard deviation of each channel
    output["mean_1"] = statistics.mean(combined_1)
    output["stdev_1"] = statistics.stdev(combined_1)
    output["mean_2"] = statistics.mean(combined_2)
    output["stdev_2"] = statistics.stdev(combined_2)
    output["mean_3"] = statistics.mean(combined_3)
    output["stdev_3"] = statistics.stdev(combined_3)

    #calculate average background value across all channels
    average = (output['mean_1'] + output['mean_2'] + output['mean_3'])/float(3)
    
    #create channels conversion dictionary
    channel_dict = {'mean_1':0, 'mean_2':1, 'mean_3':2}
    
    #find most distinct channel
    biggest_dif = 10
    channel = None
    for x in ['mean_1', 'mean_2', 'mean_3']:
        dif = abs(output[x] - average)
        if dif > biggest_dif:
            biggest_dif = dif
            channel = channel_dict[x]
    
    #return
    return output, channel
  