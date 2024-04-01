import time
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from chatbot.settings import API_KEY, a_id

# writing functions

def continue_run_request(client, msg, t_id):
    thread_message = client.beta.threads.messages.create(
        t_id,
        role="user",
        content=msg,
    )
    run = client.beta.threads.runs.create(
        thread_id=t_id,
        assistant_id= a_id
    )
    return run


def new_run_request(client, msg):
    run = client.beta.threads.create_and_run(
        assistant_id= a_id,
        thread={
            "messages": [
                {"role": "user", "content": msg}
            ]
        }
    )
    return run


def get_request(client, run):

    # checking run status until completed
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id,
            run_id=run.id
        )
        if run.status == 'completed':
            break
        time.sleep(5)  # Wait for five second before checking again

    # getting the thread messages list
    thread_messages = client.beta.threads.messages.list(run.thread_id)
    result = thread_messages.data[0].content[0].text.value
    return result

# writing views


def index(request):
    request.session.flush()
    return render(request, "chatbot.html")


@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")

        try:
            t_id = request.session['thread_id']
        except:
            t_id = None
        
        client = OpenAI(api_key=API_KEY)
        
        # previous thread
        if t_id:
            run = continue_run_request(client, message, t_id)
            print(t_id)
        
        # new thread
        else:
            run = new_run_request(client, message)
            request.session['thread_id'] = run.thread_id
            print("assigned")

        response_message = get_request(client, run)
        return JsonResponse({"message": response_message})
