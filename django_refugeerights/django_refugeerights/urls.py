from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^admin/',  include(admin.site.urls)),
                       url(r'^locationfinder/',
                           include('locationfinder.urls')),
                       url(r'^admin/locationfinder/upload/',
                           'locationfinder.views.locations_uploader',
                           {'page_name': 'locations_uploader'},
                           name="locations_uploader"),
                       url(r'^contentstore/',
                           include('contentstore.urls')),
                       )
