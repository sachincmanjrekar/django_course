from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse



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
    # print(reverse('home'))
    html = ""
    for post in post_list:
        html += f'''
            <div>
            <a href="/post/{post["id"]}/">
                <h2>{post["id"]}-{post["title"]}</h2></a>
                <p>{post["content"]}</p>
            </div>
        '''
    return render(request, 'home.html')


def post_detail(request, id):

    post_dict = {}
    for post in post_list:
        if post["id"] == id:
            post_dict = post
            break

    if not post_dict:
        return HttpResponseNotFound("Post not found") 
    
    html = f'''
        <div>
            <h2>{post_dict["id"]}-{post_dict["title"]}</h2>
            <p>{post_dict["content"]}</p>
        </div>
    '''

    return HttpResponse(html)


def google(request, id):
    print(reverse('post_detail', args=[id]))
    url = reverse('post_detail', args=[id])
    return HttpResponseRedirect(url)

    