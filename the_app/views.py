import time
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from chatbot.settings import API_KEY, a_id
import os
from supabase import create_client, Client
import sys
import tiktoken

def count_tokens(filename: str, model_name="gpt-4") -> int:
    """Count the number of tokens in a file using TikToken."""
    try:
        with open(filename, 'r') as file:
            content = file.read()
            # Get the tokenizer encoding for the specified model
            encoding = tiktoken.encoding_for_model(model_name)
            tokens = encoding.encode(content)
            return len(tokens)
    except FileNotFoundError:
        print("File not found.")
        return 0

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python script.py <filename>")
#     else:
#         filename = sys.argv[1]
#         print("Number of tokens:", count_tokens(filename))


def create_chunks(file_path, model_name="gpt-4", max_tokens_per_chunk=1500000):
    # Get the tokenizer encoding for the specified model
    encoding = tiktoken.encoding_for_model(model_name)

    # Read the file
    with open(file_path, 'r') as file:
        text = file.read()

    # Divide the text into chunks based on tokens
    chunks = []
    current_chunk = ""
    current_token_count = 0

    for line in text.split('\n'):
        line_tokens = encoding.encode(line)
        line_token_count = len(line_tokens)

        if current_token_count + line_token_count > max_tokens_per_chunk:
            chunks.append(current_chunk)
            current_chunk = line + '\n'
            current_token_count = line_token_count
        else:
            current_chunk += line + '\n'
            current_token_count += line_token_count

    if current_chunk:
        chunks.append(current_chunk)

    # Save each chunk to a separate text file
    for i, chunk in enumerate(chunks):
        chunk_file_path = f'chunk{i+1}.txt'
        with open(chunk_file_path, 'w') as chunk_file:
            chunk_file.write(chunk)

# Example usage
# create_chunks('songs_original.txt', model_name="gpt-4")

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
