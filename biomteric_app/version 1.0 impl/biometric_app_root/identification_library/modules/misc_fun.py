# -*- coding: utf-8 -*-
"""
Created on Thu May 17 13:28:08 2018
"""

#import python libraries
import math
import re
import random
import numpy


def random_int_string(length):
    
    """
    DESCRIPTION
    This function generates a string of a designated length which consists of 
    random integers. This is used for generating random identification numbers
    
    INPUT
    length = the length of string required
    
    OUTPUT
    output = a string of integers of a defined length
    """

    #initialize an empty string
    output = ''
    #add a specified numer of integers to the string
    for x in range(length):
        output += random.choice(['0', '1', '2', '3', '4', 
                                 '5', '6', '7', '8', '9'])
    #return
    return output


def natural_key(string_):
    
    """
    DESCRIPTION
    This function can be used for natural sorting of a list. The call to this 
    function is included as the key item in pythons standard sort function.    
    See http://www.codinghorror.com/blog/archives/001018.html
    
    INPUT
    string_ = can be skipped when calling
    
    OUTPUT
    used within
    """
    
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def distance(point_a, point_b):
    
    """
    DESCRIPTION
    This function measures the distance between two pixel locations (x,y 
    coordinates).
    
    INPUT
    point_a = the first xy coordinate
    point_b = the second xy coordinate
    
    OUTPUT
    d = the distance between the two xy coordinates
    """
    
    #calculate distance between two points
    distance = math.sqrt(((float(point_a[0])-float(point_b[0]))**2) + 
                         ((float(point_a[1])-float(point_b[1]))**2))
    #return distance
    return distance


def degrees(point_a, point_b):
    
    """
    DESCRIPTION
    This function calculates the angle in degrees between two points starting 
    at a horizontal angle and rotating clockwise. Values range from 0 
    degrees to 360 degrees.

    INPUT
    point_a = the first xy coordinate
    point_b = the second xy coordinate
    
    OUTPUT
    degrees = the angle between the two points    
    """
    
    #calculate difference between dimensions of two points
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    #use math library to calculate radians
    radians = math.atan2(dy,dx)
    #convert radians to degrees
    degrees = math.degrees(radians)
    #convert from -180:180 to 0:360 degree range
    degrees += 180
    #return
    return degrees


def degrees_limit_range(degrees):
    
    """
    DESCRIPTION
    This function limits degrees to a range of 0:360
    
    INPUT
    degrees = angle in degrees
    
    OUTPUT
    degrees = angle in degrees
    """
    
    while degrees > 360:
        degrees -= 360
    while degrees < 0:
        degrees += 360
    #return
    return degrees


def point_distance(coordinate, distance, degrees):
    
    """
    DESCRIPTION
    This function generates a point at a set angle and distance from a starting 
    x,y coordinate. The angle starts at a horizontal point to the left of the
    coordinate and rotates clockwise.
    
    INPUT
    coordinate = the starting xy coordinate point
    distance = the distance at which to generate a new point
    degrees = the angle in degrees at which to generate a new point
    
    OUTPUT
    output = a new xy coordinate point    
    """
    
    #convert degrees to radians
    radians = math.radians(degrees)
    #generate the output coordinate
    output = [int(coordinate[0] + distance*math.cos(radians)), 
              int(coordinate[1] + distance*math.sin(radians))]
    #return   
    return output


def point_mid(point_a, point_b, proportion):
    
    """
    DESCRIPTION
    This function generates an xy coordinate at a defined proportion of the 
    distance between two starting points.
    
    INPUT
    point_a = the first xy coordinate point
    point_b = the second xy coordinate point
    proportion = the distance between the two points to generate a new point
    
    OUTPUT
    output = the target xy coordinate point
    """
    
    #generate the x and y point
    x = point_a[0] + (point_b[0] - point_a[0]) * proportion
    y = point_a[1] + (point_b[1] - point_a[1]) * proportion
    #output
    output = [x,y]
    #return the new xy coordinate
    return output


def circle_area_to_radius(area):
    
    """
    DESCRIPTION
    This function calculates the radius of a circle given its area
    
    INPUT
    area = the area of the target circle
    
    OUTPUT
    radius = the radius based on the input area
    """
    
    #calculate the radius of the circle
    radius = math.sqrt(area/float(3.15159))
    #return
    return radius


def array_normalize(array_in, min_limit, max_limit):
    
    """
    DESCRIPTION
    This function normalizes an input numpy array to the defined range.
    
    INPUT
    array_in = an array in standard numpy format
    min_limit = the minimum value to normalize to
    max_limit = the maximum value to normailze to
    
    OUTPUT
    array_out = an array in standard numpy format
    """

    #get minimum and maximum values in array    
    min_value = numpy.amin(array_in)
    max_value = numpy.amax(array_in)
    #normalize array to range
    array_out = (array_in - min_value)/(max_value-min_value)*max_limit     
    #return
    return array_out


def distant_points(data_in):
    
    """
    DESCRIPTION
    This function filters a list of xy coordinates and returns the two most
    distant points.
    
    INPUT
    data_in = a list of xy coordinates
    
    OUTPUT
    points_out = a list of two xy coordinates
    """
    
    #set width max to 0
    width_max = -1
    points_out = None
    #compare all items in cross_section
    for x in data_in:
        for y in data_in:
            #measure width
            width = distance(x,y)
            #if greater than previous width update outputs
            if width_max < width:
                #set as output points
                points_out = [x, y]  
                width_max = width
    #return
    return points_out