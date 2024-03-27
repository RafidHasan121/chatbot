from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

def index(request):
    return render(request, "chatbot.html")

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        print(message)
        response_message = "test"
        return JsonResponse({"message": response_message})
