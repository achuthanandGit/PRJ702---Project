from django.urls import path
from django.conf.urls import url

from . import views
from .views import IdentifyList

urlpatterns = [
    path('', views.identify, name='identify'),
    path('identify_list/', IdentifyList.as_view(), name='identify-list'),
    url(r'^identify-fish/$', views.identifyFish),
    url(r'^identify_list/get-match-data/$', views.getMatchData),
    url(r'^identify_list/try-again/$', views.tryAgain),
]