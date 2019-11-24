from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic.list import ListView


import calendar
import time
import datetime
import json
import asyncio

from biometric_app_site.settings import MEDIA_ROOT
from identification_library import identifyImage

from .models import Identify, FishData
from .form import IdentifyForm

"""
identify(request)
to load the upload form view when the page is loaded
"""
def identify(request):
    #Identify.objects.all().delete()
    #FishData.objects.all().delete()
    return render(request, 'identify/identify.html', {'form':IdentifyForm(),})

"""
error_404(request, exception, template_name='404.html'):
to load the 404 error page view when wrong URL is loaded
"""
def error_404(request, exception, template_name='404.html'):
    return render(request, 'error-pages/404.html', status=404)

"""
error_500(request, template_name='500.html'):
to load the 500 error page view when unexpected error happens in the server side
"""
def error_500(request, template_name='500.html'):
    return render(request, 'error-pages/500.html', status=500)

"""
identifyFish(request)
to initiate the process to find the matching data when the user submitted the form

input : request
        contains data from the client side to manage in the server side
        important contains the form data and request type
"""
def identifyFish(request):
    # creating asynchrnous process for finding the match data
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(getDataAndRun(request))
    return JsonResponse({})

"""
getDataAndRun(request)
to initiate the mathcing process. Will triggered from identifyFish method

Input : request
        contains data from the client side to process input
        contains the form data and request type
"""    
def getDataAndRun(request):
    analyzeDataResult = {}
    # checking whether the request of POST or not
    if request.method == 'POST':
        # getting form data
        form = IdentifyForm(request.POST, request.FILES)
        # validating form data
        if form.is_valid():
            # auto generating the id for upload image. Id is created using the current date and time
            imageId = calendar.timegm(time.gmtime())
            identifyObj = Identify()
            # putting basic data to model object identifyObj
            identifyObj.imageId = imageId
            identifyObj.username = form.cleaned_data['username']
            identifyObj.email = 'NA'
            identifyObj.image = form.cleaned_data['image']
            identifyObj.tank = form.cleaned_data['tank']
            # updating the process state
            identifyObj.status = 'Running process'
            # analysing the pitTag provided by user
            if form.cleaned_data['pitTag']:
                identifyObj.pitTag = form.cleaned_data['pitTag']
            else:
                identifyObj.pitTag = '-'
            # saving the input data 
            identifyObj.save()
            # setting the uploaded image url for further process
            image_url = MEDIA_ROOT + '/images/' + str(form['image'].value())
            # getting image name from uploaded image file
            image_name = str(form['image'].value()).split('.')[0]
            # Calling the process of matching the uploaded data with database data
            analyzeDataResult = identifyImage.analyzeData(image_url, image_name, identifyObj.pitTag)
            # checking whether the analyzes was successull or not
            if analyzeDataResult['type'] == 'success':
                spotObj = FishData()
                # getting the analyzis result of uploaded image
                new_individual = analyzeDataResult['new_individual']
                # getting the match datalist
                matching_image_list = analyzeDataResult['matching_image_list']
                # getting the match imageId list
                match_image_id_list = analyzeDataResult['matching_image_id_list']
                # updating spotObj object with result
                spotObj.imageId = imageId
                spotObj.name = image_name
                spotObj.imageUrl = form.cleaned_data['image']
                spotObj.spots = json.dumps(new_individual['spots'])
                spotObj.refNose = json.dumps(new_individual['ref_nose'])
                spotObj.refHead = json.dumps(new_individual['ref_head'])
                spotObj.refTail = json.dumps(new_individual['ref_tail'])
                if analyzeDataResult['type'] is 'Match Not Found' or len(matching_image_list) == 0:
                    spotObj.population = '-'
                else:
                    spotObj.population = matching_image_list[0]['population']
                spotObj.tank = form.cleaned_data['tank']
                spotObj.date = datetime.date.today().strftime("%y-%m-%d")
                spotObj.time = analyzeDataResult['timeTook']
                spotObj.report = analyzeDataResult['matchPitTag']
                if identifyObj.pitTag is '-':
                    spotObj.pitTag = '-'
                else:
                    spotObj.pitTag = analyzeDataResult['matchPitTag']
                if analyzeDataResult['matchPitTag'] is not '-':
                    spotObj.baseTag = analyzeDataResult['matchPitTag']
                else:
                    spotObj.baseTag = imageId
                # saving the match result
                spotObj.save()
                if len(matching_image_list) == 0:
                    identifyObj.population = '-'
                    identifyObj.status = "Match not Found"
                else:
                    identifyObj.population = matching_image_list[0]['population']
                    identifyObj.matchingImageId = json.dumps(match_image_id_list)
                    identifyObj.status = 'Match Found'
                # saving the match details
                identifyObj.save()
                #responseData = analyzeDataResult                
            else:
                identifyObj.status = 'Match not Found'
                identifyObj.save()
                #responseData = {'type': 'info', 'message': 'Sorry, unable to identify the fish. Please try again with another.'}

"""
IdentifyList(ListView):
to load the uploaded list in the table as listview

Input : ListView
        to provide list view in the django template
Output : context
         contains list of uploaded data
"""
class IdentifyList(ListView):
    model = Identify
    context_object_name = 'all_identifys'
    # getting the upload data using django native method for ListView
    def get_context_data(self, **kwargs):
        context = super(IdentifyList, self).get_context_data(**kwargs)
        context['identify_list'] = Identify.objects.all()
        return context

"""
getMatchData(request)
trigger to get the matches when the user clicks a row in the uploaded list view

Input : request
        contains the client side data
        contains the imageId of the image clicked
Output : responseData
         contains the match data detils for the clicked image
         will be empty if no match found
"""
def getMatchData(request):
    responseData = []
    if request.method == 'POST' and request.is_ajax():
        imageId = request.POST.get('imageId', None)
        return getMatchDataFromDB(imageId)
    else:
        return JsonResponse({})

"""
getMatchDataFromDB(request)
to get the clicked image details from the database and will return to the client side to display

Input : imageId
        imageId of the image clicked
Output : responseData
         contains the match data detils for the clicked image
         will be empty if no match found
"""
def getMatchDataFromDB(imageId):
    responseData = []
    # getting clicked image data from database
    matchDataId = Identify.objects.get(pk=imageId)
    # condition to check whether the clicked image has match found
    if(matchDataId.status == 'Match Found'):
        # decoding the matching imageId list
        matchImageIdList = jsonDec.decode(matchDataId.matchingImageId)
        # getting the match data using matchImageIdList
        matchDataList = FishData.objects.filter(pk__in=matchImageIdList)
        # organizing the data for display
        for data in matchDataList:
            print(data.imageUrl.url)
            if data.pitTag:
                tag = data.pitTag
            elif data.report:
                tag = data.report
            else:
                tag = '-'
            responseData.append({'name' : data.name,
                'imagePath': str(data.imageUrl.url),
                'population': data.population,
                'tank': data.tank,
                'date': data.date,
                'tag' : tag,
                })
    return JsonResponse(responseData, safe=False)


"""
tryAgain(request)
will recheck for the match details when re-check button is clicked by user

Input : request
        contains client side data for the process
        contains imageId
Output: responseData
        contains the match data detils for the clicked image
        will be empty if no match found
"""
def tryAgain(request):
    print('try again')
    responseData = []
    analyzeDataResult = {}
    # getting imageId of clicked row
    imageId = request.POST.get('imageId', None)
    # checking whether the request is POST and ajax
    if request.method == 'POST' and request.is_ajax():
        jsonDec = json.decoder.JSONDecoder()
        # getting clicked dataset
        dataToCheck = Identify.objects.get(pk=imageId)
        # Confirming the clicked image has no matches found previously
        if(dataToCheck.status == 'Match not Found'):
            # setting the image url of clicked image for further process
            image_url = MEDIA_ROOT + '/images/' + dataToCheck.image.url.split('/')[3]
            # setting the image name for further process
            image_name = str(dataToCheck.image.url.split('/')[3].split('.')[0])
            # Initiating the analysis for finding the matches
            analyzeDataResult = identifyImage.analyzeData(image_url, image_name, dataToCheck.pitTag)
            # checks whether the process is success or not
            if analyzeDataResult['type'] == 'success':
                spotObj = FishData()
                # getting details of image clicked
                new_individual = analyzeDataResult['new_individual']
                # getting details of matched data
                matching_image_list = analyzeDataResult['matching_image_list']
                # getting imageId list of matched data
                match_image_id_list = analyzeDataResult['matching_image_id_list']
                # setting the match data to save 
                spotObj.imageId = dataToCheck.imageId
                spotObj.name = image_name
                spotObj.imageUrl = dataToCheck.image.url
                spotObj.spots = json.dumps(new_individual['spots'])
                spotObj.refNose = json.dumps(new_individual['ref_nose'])
                spotObj.refHead = json.dumps(new_individual['ref_head'])
                spotObj.refTail = json.dumps(new_individual['ref_tail'])
                if analyzeDataResult['type'] is 'Match Not Found' or len(matching_image_list) == 0:
                    spotObj.population = '-'
                else:
                    spotObj.population = matching_image_list[0]['population']
                spotObj.tank = dataToCheck.tank
                spotObj.date = datetime.date.today().strftime("%y-%m-%d")
                spotObj.time = analyzeDataResult['timeTook']
                spotObj.report = analyzeDataResult['matchPitTag']
                if dataToCheck.pitTag is '-':
                    spotObj.pitTag = '-'
                else:
                    spotObj.pitTag = analyzeDataResult['matchPitTag']
                if analyzeDataResult['matchPitTag'] is not '-':
                    spotObj.baseTag = analyzeDataResult['matchPitTag']
                else:
                    spotObj.baseTag = dataToCheck.imageId
                # saving matchdata
                spotObj.save()
                if len(matching_image_list) == 0:
                    dataToCheck.population = '-'
                    dataToCheck.status = "Match not Found"
                else:
                    dataToCheck.population = matching_image_list[0]['population']
                    dataToCheck.matchingImageId = json.dumps(match_image_id_list)
                    dataToCheck.status = 'Match Found'
                # saving clicked image data
                dataToCheck.save()             
            else:
                dataToCheck.status = 'Match not Found'
                # saving clicked image data
                dataToCheck.save()
    # returning the match details for showing for the user
    return getMatchDataFromDB(imageId)


    