from django.shortcuts import render
from django.http import Http404
from .models import Post



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

# post_list = []

# Create your views here.
def home(request):

    all_posts = Post.objects.all()
    print(all_posts)
    return render(request, 'posts/index.html', {'posts': all_posts, 'name': 'sachin'})


def post_detail(request, id):

    post_dict = {}
    for post in post_list:
        if post["id"] == id:
            post_dict = post
            break

    if not post_dict:
        raise Http404()
    

    return render(request, 'posts/post.html', {"post_dict": post_dict})

