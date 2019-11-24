#import python libraries
import json
import cv2
import copy
import datetime



# import json file path
from biometric_app_site.settings import JSON_ROOT

# import shared modules
from . import functions
from .modules import misc_fun
from .modules import untidy_fun
from .modules import fish_fun
from .modules import opencv_fun

# import model
from identify.models import FishData

"""
Accepts request from web page and return the result

INPUT
image = path of uploaded image
imageName = name of uploaded image
pitTag = physical tag of uploaded image

OUTPUT
Identfication results
"""
def analyzeData(image, imageName, pitTag):
    print('starting identification')
    
    # load the merged raw spot data
    spot_data_file = JSON_ROOT + '/snapper-spot-data.json'
    with open(spot_data_file, 'r') as file:
        spot_data = json.load(file)
    
    # to analyze how much time taken for the identification process
    startTime = datetime.datetime.now()
    
    # load image to deal the identification process
    try:
        img = cv2.imread(image)
        if img is None:
            return {'type': 'error', 'message': 'Failed to open image. Please try again'}
    except:
        return {'type': 'error', 'message': 'Failed to open image. Please try again'}
        
    standard_height = 1000
    population = '2013B10'
    date = '2019-03-22'
    methods = ['fish_ref']
    matchPerm = 100
    matchQuality = 12

    # Resize input image and create three copies for different parts of the analysis
    ratio = standard_height / float(len(img))
    img_resized = cv2.resize(img, (0,0), fx=ratio, fy=ratio)  
    img_spot = copy.deepcopy(img_resized)      
    img_ref = cv2.cvtColor(img_spot,cv2.COLOR_BGR2GRAY) 
    img_out = copy.deepcopy(img_resized)
    
    print('finding fish')
     # Find fish in image
    fish = fish_fun.extract_fish_smart(img_out)
    #fish, best_value, best_overlap, best_contrast = untidy_fun.edge_optimized(img_out, ['snapper'], 50, 1000, 1.5)
    
    # If fish is not identified skip rest of the process
    if fish is None:
        return {'type': 'error', 'message': 'No Fish detected. Please try again.'}
    
    print('finding spots')
    # Run spot detection function
    spots = fish_fun.extract_snapper_spots(copy.deepcopy(img_spot), fish)

    if spots is None:
        return {'type': 'error', 'message': 'No spots for identification detected. Please try again.'}
    
    # generate list of spot centers
    spot_centers = [opencv_fun.contour_center(x) for x in spots]
      
    # find three ref points
    nose_upper, nose_lower = fish_fun.ref_fish_lips(fish)
    tail_upper, tail_lower = fish_fun.ref_tail_across(fish)
    head_upper = fish_fun.ref_fish_head(fish, nose_upper, tail_upper)
        
    # init a new individual dictionary
    new_ind = {"population": population, "date": date, "number": 0,
                    "image": image, 'spots': spot_centers, 'ref_nose': nose_upper, 
                   'ref_head': head_upper, 'ref_tail': tail_upper,
                   'name': imageName}

    # initiating search for match
    return search_for_match(new_ind, methods, matchQuality, matchPerm, startTime, pitTag)



def search_for_match(new_individual, methods, matchquality, matchPerm, startTime, pitTag):
    #loop through dataset for a total number of permutations
    dataList = FishData.objects.order_by('-date')
    matchData = {}
    print('Start checking for match')
    if pitTag is '-':
        print('Bio match starts')
        matchData = getBioMatchData(dataList, new_individual, methods, matchquality, matchPerm)
    else:
        print('Tag match starts')
        matchData = getTagMatchData(new_individual, dataList, pitTag)
    print('got results')
    if pitTag is not '-' and len(matchData['matching_image_list']) == 0:
        return {'type': 'success',
                'message': 'Match Not Found',
                'new_individual': new_individual,
                'matchPitTag': pitTag,
                'matching_image_list': matchData['matching_image_list'],
                'matching_image_id_list': matchData['matching_image_id_list'],
                'timeTook': str(datetime.datetime.now() - startTime)}
    elif len(matchData['matching_image_list']) == 0:
        return {'type': 'info', 'message': 'Sorry, unable to identify the fish.'}
    else:
        return {'type': 'success',
            'message': 'Match Found',
            'new_individual': new_individual,
            'matchPitTag': matchData['matchPitTag'],
            'matching_image_list': matchData['matching_image_list'],
            'matching_image_id_list': matchData['matching_image_id_list'],
            'timeTook': str(datetime.datetime.now() - startTime)}


def getTagMatchData(new_individual, dataList, pitTag):
    imageName = new_individual['name']
    matching_image_list = []
    mathcing_image_id_list = []
    jsonDec = json.decoder.JSONDecoder()
    for data_individual in dataList:
        if imageName == data_individual.name:
            continue
        if data_individual.pitTag is not '-':
            checkPitTag = data_individual.pitTag
        elif data_individual.report is not '-':
            checkPitTag = data_individual.report
        else:
            continue
        imageId = data_individual.imageId
        if checkPitTag == pitTag and (len(mathcing_image_id_list) == 0 or imageId not in mathcing_image_id_list):
            mathcing_image_id_list.append(imageId)
            matching_image_list.append({'population' : data_individual.population,
                                            'name' : data_individual.name, 
                                            'imageId' : imageId,
                                            'tank': data_individual.tank, 
                                            'date': data_individual.date})
    return {'matching_image_list': matching_image_list,
            'matching_image_id_list': mathcing_image_id_list,
            'matchPitTag' : pitTag}   


def getBioMatchData(dataList, new_individual, methods, matchquality, matchPerm):
    loop = 0
    matching_image_list = []
    mathcing_image_id_list = []
    matchPitTag = '-'
    jsonDec = json.decoder.JSONDecoder()
    imageName = new_individual['name']
    while loop < len(range(matchPerm)):
        for data_individual in dataList:
            if imageName == data_individual.name:
                continue

            # select the spots to allign
            dataSpots = data_individual.spots

            # setting check_data
            check_data = {'spots': jsonDec.decode(data_individual.spots),
                        'ref_nose': jsonDec.decode(data_individual.refNose),
                        'ref_tail': jsonDec.decode(data_individual.refTail),
                        'ref_head': jsonDec.decode(data_individual.refHead)}

            # align the data_individual to the new individual        
            aligned_pattern = fish_fun.align_patterns(copy.deepcopy(new_individual),
                copy.deepcopy(check_data), methods[0])

            #compare to new_individual
            match_list = fish_fun.compare_patterns(new_individual['spots'], aligned_pattern)

            # count the number of matching spots
            match_value = len([x for x in match_list if x[1] < 0.15])

            population = data_individual.population
            name = data_individual.name
            imageId = data_individual.imageId
            tank = data_individual.tank
            date = data_individual.date
            temp = {}
            if match_value > matchquality and (len(mathcing_image_id_list) == 0 or imageId not in mathcing_image_id_list):
                    mathcing_image_id_list.append(imageId)
                    if data_individual.pitTag is not '-':
                        matchPitTag = data_individual.pitTag
                    elif data_individual.report is not '-':
                        matchPitTag = data_individual.report
                    matching_image_list.append({'population' : population,
                                            'name' : name, 'imageId' : imageId,
                                            'tank': tank, 'date': date})
                    break
        loop += 1
    return {'matching_image_list': matching_image_list,
            'matching_image_id_list': mathcing_image_id_list,
            'matchPitTag': matchPitTag}



    """

    # draw reference points to image
    cv2.drawContours(img_out, [fish], -1, (0,255,0), 3)
    cv2.drawContours(img_out, spots, -1, (0,0,255), 1) 
    cv2.circle(img_out, (int(nose_upper[0]),int(nose_upper[1])),5,(255,0,255),-1)
    cv2.circle(img_out, (int(head_upper[0]),int(head_upper[1])),5,(255,0,255),-1)
    cv2.circle(img_out, (int(tail_upper[0]),int(tail_upper[1])),5,(255,0,255),-1)
    
    # show image with extracted data points
    cv2.imshow('image', img_out)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()
    
    # save image to file
    #cv2.imwrite(img_name_out, img_out)

    #set name for image if exploring specific matches within the search function
    name = None#'015544444'#'884108669'
    
    #set the match_name to None
    match_name = None
    match_prob = None

    print('finding match')
    for method in methods:
        #set method_out
        method_out = method
        
        #use new spot pattern data to search database
        matching_image, match_info = functions.search_for_pattern(spot_data, new_ind, matchQuality, matchPerm, method)
        #break if individual is found
        if matching_image is not None:
            break

    if matching_image is None:
        return {'type': 'info', 'message': 'Sorry, unable to identify the fish.'}
    

    return {'type':'success', 'message':'Match Found.',
            'population': matching_image["population"],
            'date': matching_image["date"],
            'number': matching_image["number"],
            'value': match_info["value"],
            'time': match_info["time"],
            'permutations': match_info["permutations"],
            'spots': spot_centers,
            'ref_nose': nose_upper,
            'ref_head': head_upper,
            'ref_tail': tail_upper}
    """
    


