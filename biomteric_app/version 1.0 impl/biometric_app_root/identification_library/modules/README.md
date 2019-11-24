[TOC]

# Overview

This folder contains the shared python modules which are being developed as an overlapping component of the other image analysis projects within this repository. These modules contain functions which are being used to reduce the work required when coding opencv or similar solutions for image analysis projects.



# Module descriptions



## misc_fun.py

This module contains miscellaneous functions which do not specifically relate to OpenCV or PFR image analysis problems (e.g. basic python mathematical problems). Some of this functionality might be present in libraries which 



## opencv_fun.py

This module contains functions which are specific to OpenCV formatted data types (e.g. OpenCV formatted contour array or images). These functions could be usable outside PFRs immediate image analysis problems.



## untidy_fun.py

This module contains functions which are being used by multiple projects but could benefit from further refactoring. Many of these functions are specific a PFR centric problem which may or may not be reusable outside these applications. This module will probably be subdivided at some point into modules related more specific applications (e.g. a pattern matching module which implements PFR's biometric identification).



## fish_fun.py

This module contains functions which are specific to analysis of fish images. This includes the functions for measuring fish shape, extracting spot pattern and reference point coordinates.



## stitch_fun.py

This module contains the functions needed to carry out image stitching with opencv. This could potentially be migrated into the opencv_fun module at a later date.