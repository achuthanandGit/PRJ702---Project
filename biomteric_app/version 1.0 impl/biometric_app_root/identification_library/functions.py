# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 10:02:06 2019
"""

#import libraries
import copy
import datetime


#import shared modules
from .modules import misc_fun
from .modules import fish_fun


def contour_edge_angle(contour, position, angle):
    
    """
    DESCRIPTION
    This function locates the outer edge of a contour at a defined angle from 
    the starting position. This function is limited to finding angles within a
    45 degree range.
    
    INPUT
    contour = a contour in standard opencv format
    postion = xy coordinates of the starting position
    angle = the angle (degrees) at which to find the edge
    
    OUTPUT
    postion_out = xy coordinates of the outer edge
    """ 

    #initialize position_out
    position_out = None    
    #initialize empty data dictionary
    data = []
    #get set of points either side
    for x in range(0, len(contour)-1):
        #calculate angle to each position
        angle_1 = misc_fun.degrees_360(misc_fun.degrees(contour[x][0], position))
        angle_2 = misc_fun.degrees_360(misc_fun.degrees(contour[x+1][0], position))
        #search for target angle if 10 degree region is found
        if abs(angle_1 - angle_2) < 45:
            #add two data if either side
            if angle_1 < angle < angle_2:
                data += [[contour[x][0], contour[x+1][0]]]
            elif angle_2 < angle < angle_1:
                data += [[contour[x][0], contour[x+1][0]]]
            elif angle_1 == angle:
                position_out = contour[x][0]
                break
            elif angle_2 == angle:
                position_out = contour[x+1][0]
                break 
    #check if position_out is already found
    if position_out is None:
        if len(data) > 0:
            #get most distant set
            if len(data) > 1:
                #measure distance to max position
                most_distant = max([misc_fun.distance(x[0], position) for x in data])
                #filter to only include position
                data = [x for x in data if misc_fun.distance(x[0], position) == most_distant]
            #get position
            position_out = misc_fun.point_mid(data[0][0], data[0][1], 0.5)            
    #return 
    return position_out


def search_for_pattern(dataset, new_individual, limit, perm, method):
    
    """
    DESCRIPTION
    This is a new version of the search_for_pattern function located in the 
    untidy_fun module. This function was built to return the name of the image
    which it was matched to rather than a id number. Otherwise it still uses
    the same base pattern matching functions. To improve performance this 
    function only compares individuals from the same population.
    
    INPUT
    dataset = the spot pattern dataset in which to search for the new pattern
    new_individual = the data from the new individual (spots + ref points)   
    limit = the minimum number of matching spots for a match
    perm = maximum permutations to search for a match
    method = the affine reference points to use for matching
    
    OUTPUT
    matching_image["population"] = the population the image belongs to
    matching_image["date"] = the date the image belongs to
    matching_image["number"] = the image number for the matching image
    match_data["value"] = the number of matching spots
    match_data["time"] = the search time
    match_data["permutations"] = the search permutations
    """
    
    #set an initial start time
    start_time = datetime.datetime.now()
    #create output variables as None
    matching_image = None
    match_data = {"value": None,
                  "time": None,
                  "permutations": None} 
    #loop through dataset for a total number of permutations
    loop = 0
    while loop < len(range(perm)):
        #initialize None for return values
        match_value = None
        #loop through each population
        for population in dataset:
            #skip if not the same population as the input image
            if population != new_individual["population"]:
               continue
            #loop through dates
            for date in dataset[population]:
                #loop through individual in date
                for number in dataset[population][date]:
                    #select the data_individual
                    data_individual = dataset[population][date][number]
                    #skip if fewer than four spots
                    if len(data_individual['spots']) < 4:
                        continue
                    if len(new_individual['spots']) < 4:
                        continue
                    #check that it is not the same photo
                    image_1 = str(population) + str(date) + str(number)
                    image_2 = str(new_individual["population"]) + str(new_individual["date"]) + str(new_individual["number"])
                    if image_1 == image_2:
                        continue                    
                    #align the data_individual to the new individual
                    aligned_pattern = fish_fun.align_patterns(copy.deepcopy(new_individual), 
                                                                copy.deepcopy(data_individual), 
                                                                method)
                    #compare to new_individual
                    match_list = fish_fun.compare_patterns(new_individual['spots'], 
                                                             aligned_pattern)
                    #count the number of matching spots
                    match_value = len([x for x in match_list if x[1] < 0.15])
                    #break if sufficient number of matching spots is found
                    if match_value > limit:
                        #add info to a dictionary
                        matching_image = {"population": population,
                                          "date": date,
                                          "number": number}
                        #calculate the search time
                        end_time = datetime.datetime.now()
                        time_out = end_time - start_time
                        match_data["value"] = match_value
                        match_data["time"] = time_out.total_seconds()  
                        match_data["permutations"] = loop
                        #return
                        return matching_image, match_data 
        loop += 1                       
    #calculate time it took to match
    end_time = datetime.datetime.now()
    time_out = end_time - start_time
    match_data["time"] = time_out.total_seconds() 
    match_data["permutations"] = loop
    #return
    return matching_image, match_data


def add_match_data(match_data, population, date, number, new_data):
    
    """
    DESCRIPTION
    This function checks that the required population and date fields exist 
    within the match_data dictionary and then adds the new data to the 
    relevant position.
    
    INPUT
    match_data = a dictionary of matches
    population = the current population
    date = the current date 
    number = the image number
    new_data = the match data from the biometric search
    
    OUTPUT
    match_data = the updated match data
    """
    
    #check that population is in match
    if population not in match_data:
        match_data[population] = {}
    #check that date is within population
    if date not in match_data[population]:
        match_data[population][date] = {}
    #add new data to the specified number
    match_data[population][date][number] = new_data
    #return
    return match_data
  