from django.shortcuts import render
from django.http import HttpResponse

post_list = [
    {
        "title": "My first post",
        "content": "This is my first post content",
        "id": 1
    },
    {
        "title": "My second post",
        "content": "This is my second post content",
        "id": 2
    },
    {
        "title": "My third post",
        "content": "This is my third post content",
        "id": 3
    }
]

# Create your views here.
def home(request):
    html = ""
    for post in post_list:
        html += f'''
            <div>
                <h2>{post["id"]}-{post["title"]}</h2>
                <p>{post["content"]}</p>
            </div>
        '''
    return HttpResponse(html)


def post_detail(request, id):
    print(type(id))
    return HttpResponse(f"<h1>Post detail page for post {id}</h1>")


    