from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View


class OverviewPage(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'overview/overview.html')

    @method_decorator(login_required)
    def post(self, request):
        return render(request, 'overview/overview.html')
