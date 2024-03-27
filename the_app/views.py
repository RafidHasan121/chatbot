from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
# Create your views here.


def index(request):
    return render(request, "chatbot.html")

@ensure_csrf_cookie
def chatbot(request):
    if request.method == "POST":
        message = request.data.get("message")
    return JsonResponse({"message": message})