from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Post





# post_list = []

# Create your views here.
def home(request):

    all_posts = Post.objects.all()
    print(all_posts)
    return render(request, 'posts/index.html', {'posts': all_posts, 'name': 'sachin'})


def post_detail(request, id):

    post_dict = get_object_or_404(Post, id=id)   
    return render(request, 'posts/post.html', {"post_dict": post_dict})

