# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
def index(request):
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))