from django.http import HttpResponseRedirect
from django.contrib.auth import SESSION_KEY

class IPAuthenticationMiddleware(object):
    def process_request(self, request):
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        print "request.path:%s \t IP: %s" % (request.path,str(ip))