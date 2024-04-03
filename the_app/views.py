import time
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from chatbot.settings import API_KEY, a_id
import os
from supabase import create_client, Client


def init_supabase():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    return supabase


def get_projects(supabase):
    response = supabase.table('projects').select(
        "name", count='exact').execute()
    return response


def get_routes(supabase, project_name):
    response = supabase.table('projects').select(
        "routes").eq('name', project_name).execute()
    return response


def continue_run_request(client, msg, t_id):
    thread_message = client.beta.threads.messages.create(
        t_id,
        role="user",
        content=msg,
    )
    run = client.beta.threads.runs.create(
        thread_id=t_id,
        assistant_id=a_id
    )
    return run


def new_run_request(client, msg, project_name):
    supabase = init_supabase()
    routes = get_routes(supabase, project_name)
    
    # convert json data
    routes_json = json.dumps(routes.data[0].get('routes'))
    
    # Write the JSON string to a file
    with open('routes.json', 'w') as json_file:
        json_file.write(routes_json)
    
    # create file in openai
    file_object = client.files.create(
        file=open("routes.json", "rb"),
        purpose="assistants"
    )
    print(file_object)
    # create run 
    run = client.beta.threads.create_and_run(
        assistant_id= a_id,
        thread={
            "messages": [
                {"role": "user", "content": "for the attached json file to this message, do the following" + "\n" + msg, "file_ids": [file_object.id]}
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
    client = init_supabase()
    project_list = get_projects(client)
    return render(request, "chatbot.html", context={"dropdown": project_list.data})


@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        project = data.get("project")
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
            run = new_run_request(client, message, project)
            request.session['thread_id'] = run.thread_id
            print("assigned")

        response_message = get_request(client, run)
        return JsonResponse({"message": response_message})
