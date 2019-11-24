from django.test import TestCase
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

import json
import cv2
import copy
import datetime
import time
import calendar

from . import functions
from .modules import misc_fun
from .modules import untidy_fun
from .modules import fish_fun
from .modules import opencv_fun

from identify.models import FishData, Identify

import os

dirList = [ 'J:\\IMAGES\\snapper\\2016\\2016-09-22_snapper-externals-D2toD5-2013B9\\images',
            'J:\\IMAGES\\snapper\\2016\\2016-09-23_snapper-externals-D3toD2-2013B10\\images',
            'J:\\IMAGES\\snapper\\2016\\2016-12-02_snapper-external-D2toD3-2013B10\\images',
            'J:\\IMAGES\\snapper\\2016\\2016-12-09_snapper-externals-D1toD2-2013B11\\images',
            'J:\\IMAGES\\snapper\\2016\\2016-12-12_snapper-externals-D5toD1-2013B9\\images',
            'J:\\IMAGES\\snapper\\2016\\2016-12-15_snapper-externals-D6toD5-2013B12\\images']

#tankList = ['D1', 'D6', 'D5', 'D2', 'D3', 'D2', 'D1', 'D5']
tankList = ['D5', 'D2', 'D3', 'D2', 'D1', 'D5']
#population = ['2013B11', '2012B12', '2013B9', '2013B10', '2013B10', '2013B11','2013B9','2013B12']
population = ['2013B9', '2013B10', '2013B10', '2013B11','2013B9','2013B12']
index = 0
imgCount = 1
for dirPath in dirList:
    fileList = os.listdir(dirPath)
    for image in fileList:
        print('starting fish analysis')
        if len(image.split('_')) != 2:
            continue
        else:
            startTime = datetime.datetime.now()
            fullImage = dirPath+ '\\' + image
            try:
                img = cv2.imread(fullImage)
                if img is None:
                    print('image not found')
                    break
            except:
                    print('image found')
                
            ratio = 1000 / float(len(img))
            img_resized = cv2.resize(img, (0,0), fx=ratio, fy=ratio)  
            img_spot = copy.deepcopy(img_resized)      
            img_ref = cv2.cvtColor(img_spot,cv2.COLOR_BGR2GRAY) 
            img_out = copy.deepcopy(img_resized)
            #fish, best_value, best_overlap, best_contrast = untidy_fun.edge_optimized(img_out, ['snapper'], 50, 1000, 1.5)

            print('extracting fish')
            fish = fish_fun.extract_fish_smart(img_out)
            if fish is None:
                continue

            print('extracting spots')
            spots = fish_fun.extract_snapper_spots(copy.deepcopy(img_spot), fish)

            if spots is None:
                continue

            spot_centers = [opencv_fun.contour_center(x) for x in spots]

            nose_upper, nose_lower = fish_fun.ref_fish_lips(fish)
            tail_upper, tail_lower = fish_fun.ref_tail_across(fish)
            head_upper = fish_fun.ref_fish_head(fish, nose_upper, tail_upper)

            print('saving data')
            fisObj = FishData()
            fisObj.imageId = calendar.timegm(time.gmtime())
            fisObj.name = image.split('.')[0]
            fisObj.imageUrl = SimpleUploadedFile(name=image, content=open(fullImage, 'rb').read(), content_type='image/jpeg')
            fisObj.spots = json.dumps(spot_centers)
            fisObj.refNose = json.dumps(nose_upper)
            fisObj.refHead = json.dumps(head_upper)
            fisObj.refTail = json.dumps(tail_upper)
            fisObj.population = population[index]
            fisObj.tank = tankList[index]
            fisObj.date = image.split('_')[0]
            fisObj.time = datetime.datetime.now() - startTime
            fisObj.baseTag = image.split('_')[1].split('.')[0]
            fisObj.pitTag = image.split('_')[1].split('.')[0]
            fisObj.report = image.split('_')[1].split('.')[0]
            fisObj.save()
            print(imgCount)
            imgCount = imgCount + 1
    index = index + 1
    print(index)
print(imgCount)