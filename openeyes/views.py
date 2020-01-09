from django.shortcuts import redirect, render
from django.views import View

# Create your views here.
class index(View):
    def get(self, request):
        return redirect('/authen/login/')

#   404
class _404(View):
    def get(self, request, **kwargs):
        from django.shortcuts import render_to_response
        response = render_to_response('404.html', {})
        response.status_code = 404
        return response

#   500
# class _500(View):
#     def get(self, request, **kwargs):
#         from django.shortcuts import render_to_response
#         response = render_to_response('404.html', {})
#         response.status_code = 500
#         return response