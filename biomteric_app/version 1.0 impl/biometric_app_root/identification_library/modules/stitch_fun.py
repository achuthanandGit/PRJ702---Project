# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 13:55:09 2019
"""

import numpy
import cv2


def stitch_generate_matrix(image_1, image_2, ratio=0.75, thresh=4.0):
    
    """
    DESCRIPTION
    This function compares two images to get the homography matrix to overlap
    them. This is based on key points
    
    INPUT
    image_1 = the first image in the series
    image_2 = the second image in the series
    ratio = the matching key points ratio
    thresh = the matching key points threshold    
    
    OUTPUT
    matrix = the matrix to match image_1 to image_2 space
    """

    #detect features for each image
    kpsA, featuresA = detect_describe(image_1)
    kpsB, featuresB = detect_describe(image_2)
    # compute the raw matches and initialize the list of actual matches
    matcher = cv2.DescriptorMatcher_create("BruteForce")
    rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
    matches = []
    # loop over the raw matches
    for m in rawMatches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            matches.append((m[0].trainIdx, m[0].queryIdx))

    # computing a homography requires at least 4 matches
    if len(matches) > 4:
        # construct the two sets of points
        ptsA = numpy.float32([kpsA[i] for (_, i) in matches])
        ptsB = numpy.float32([kpsB[i] for (i, _) in matches])
        # compute the homography between the two sets of points
        matrix, status = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, thresh)
        #return
        return matrix 
    #return
    return None    
 
    
def stitch_merge_images(image_1, image_2, matrix):
    
    """
    DESCRIPTION
    This function stitches image_1 in the image_2 using the given matrix. The
    image_2 can either be a starting image or the compiled image.
    
    INPUT
    image_1 = an image in standard opencv format
    image_2 = an image in standard opencv format
    matrix = the homography matrix to merge the two images
    
    OUTPUT
    image_out = an image in standard opencv format
    """
    
    #convert image_1 to image_2 space
    image_new = cv2.warpPerspective(image_1, matrix, 
                                    (image_1.shape[1] + image_1.shape[1], 
                                     image_1.shape[0] + image_1.shape[0]), 
                                     borderMode=cv2.BORDER_TRANSPARENT)
    
#    image_new = cv2.warpPerspective(image_1, matrix, (image_1.shape[1], image_1.shape[0]), borderMode=cv2.BORDER_TRANSPARENT)
    
    cv2.imshow('image_1', image_2)
    cv2.imshow('image_2', image_new)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    #need to add area around
#    image_new[0:image_2.shape[0], 0:image_2.shape[1]] = image_2
    
    #limit new image to same size as other image
    image_new = image_new[0:image_2.shape[0], 0:image_2.shape[1]]
    
    #generate a mask for background
    test = cv2.bitwise_or(image_2, image_2, mask=image_new)
    
    
    
    #draw image_2 onto the converted image_1
    image_2[0:image_new.shape[0], 0:image_new.shape[1]] = image_new#image_2 remained unchanged
    
    cv2.imshow('image_1', image_2)
    cv2.imshow('image_2', image_new)
    cv2.imshow('image_2', test)
    cv2.waitKey(0)
    cv2.destroyAllWindows()    
    
    #return 
    return image_2


def stitch_combine_matrix(matrix_1, matrix_2):
    
    """
    DESCRIPTION
    This function merges two perspective transform matrixes using 
    multiplication.
    
    INPUT
    matrix_1 = a perspective transform matrix
    matrix_2 = a perspective transform matrix
    
    OUTPUT
    matrix_out = a perspective transform matrix
    """
 
    #use the cv2.gemm function to merge both matrices
    matrix_out = cv2.gemm(matrix_1, matrix_2, 1, None, 0)
    #return
    return matrix_out


def stitch(image_1, image_2, ratio=0.75, thresh =4.0):
    
    """
    DESCRIPTION
    This function stitches together two images. To do this it generates a set
    of key points for each image, determines which key points are matching, 
    generate a matrix to convert to same space, converts the first image to the
    same space as the second image, and then draws the second image over the
    first image (excluding overlap regions).
    
    INPUT
    image_1 = the first image in the series
    image_2 = the second image in the series
    ratio = the matching key points ratio
    thresh = the matching key points threshold
    
    OUTPUT
    image_out = the combined image
    matrix_out = the affine transformation matrix for merging
    """
   
    #detect features for each image
    kpsA, featuresA = detect_describe(image_1)
    kpsB, featuresB = detect_describe(image_2)  
    
    #match keypoints
    matching_keys, h_matrix, status = match_keys(kpsA, kpsB, featuresA, 
                                                 featuresB,ratio, thresh)
    
    #return
    if matching_keys is None:
        return None, None
    else:
        #convert image_1 to image_2 space
        result = cv2.warpPerspective(image_1, h_matrix, (image_1.shape[1] + image_1.shape[1], image_1.shape[0] + image_1.shape[0]))
        #draw image_2 onto the converted image_1
        result[0:image_2.shape[0], 0:image_2.shape[1]] = image_2
        #create an image to demonstrate key points
        vis = draw_matches(image_1, image_2, kpsA, kpsB, matching_keys, status)
        #return
        return result, vis


def detect_describe(image):
    
    """
    DESCRIPTION
    This function does blah blah
    
    INPUT
    image = an image in standard opencv format (BGR)
    
    OUTPUT
    
    """
       
    # detect and extract features from the image
    descriptor = cv2.xfeatures2d.SIFT_create()
    kps, features = descriptor.detectAndCompute(image, None)
    # convert the keypoints from KeyPoint objects to NumPy arrays
    kps = numpy.float32([kp.pt for kp in kps]) 
    # return a tuple of keypoints and features
    return kps, features      


def match_keys(kpsA, kpsB, featuresA, featuresB, ratio, thresh):
    
    """
    DESCRIPTION
    This function compares the features for the two images and creates a 
    matching keys set.
    
    INPUT
    kpsA = 
    kpsB =
    featuresA = 
    featuresB = 
    ratio = 
    threshold =
    
    OUTPUT
    matches = the matching key points between images
    h_matrix = the homography matrix to merge both images
    status = the status of each key point??? check this
    """
    
    # compute the raw matches and initialize the list of actual matches
    matcher = cv2.DescriptorMatcher_create("BruteForce")
    rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
    matches = []
 
    # loop over the raw matches
    for m in rawMatches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            matches.append((m[0].trainIdx, m[0].queryIdx))

    # computing a homography requires at least 4 matches
    if len(matches) > 4:
        # construct the two sets of points
        ptsA = numpy.float32([kpsA[i] for (_, i) in matches])
        ptsB = numpy.float32([kpsB[i] for (i, _) in matches])
        # compute the homography between the two sets of points
        h_matrix, status = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, thresh)
        #return
        return matches, h_matrix, status 
    # otherwise, no homograpy could be computed
    return None, None, None                

              
def draw_matches(imageA, imageB, kpsA, kpsB, matches, status):
    
    """
    DESCRIPTION
    This function does blah blah
    
    INPUT
    imageA = 
    imageB = 
    kpsA =
    kpsB =
    matches =
    status =
    
    OUTPUT
    vis = 
    """
    
    # initialize the output visualization image
    (hA, wA) = imageA.shape[:2]
    (hB, wB) = imageB.shape[:2]
    vis = numpy.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
    vis[0:hA, 0:wA] = imageA
    vis[0:hB, wA:] = imageB
 
    # loop over the matches
    for ((trainIdx, queryIdx), s) in zip(matches, status):
        # only process the match if the keypoint was successfully
        # matched
        if s == 1:
            # draw the match
            ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
            ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
            cv2.line(vis, ptA, ptB, (0, 255, 0), 1)
 
    # return the visualization
    return vis
