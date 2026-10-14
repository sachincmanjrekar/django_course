django-admin startproject blog
    - Creates a new Django project named "blog".
    - Makes a folder "blog" containing:
        manage.py        -> tool to run project commands (runserver, migrate, startapp, ...)
        blog/            -> project settings package
            __init__.py  -> marks the folder as a Python package
            settings.py  -> project configuration (installed apps, database, etc.)
            urls.py      -> main URL routes of the site
            asgi.py      -> entry point for async web servers
            wsgi.py      -> entry point for regular web servers

python manage.py runserver
    - Starts the development server at http://127.0.0.1:8000/

python manage.py runserver 1223
    - Starts the development server on port 1223 instead (http://127.0.0.1:1223/).

Django apps (understanding)
    - A project is like a car; apps are its parts (music player, engine, AC, ...).
    - Each app is independent and does one job.
    - An app can be copied and reused in another project,
      like moving the music player to another car.

python manage.py startapp posts
    - Creates a new app named "posts" (run inside the folder with manage.py).
    - Makes a folder "posts" containing:
        __init__.py   -> marks the folder as a Python package
        admin.py      -> register models to show in the admin site
        apps.py       -> app configuration
        migrations/   -> database change files for this app
        models.py     -> database tables (models) for this app
        tests.py      -> tests for this app
        views.py      -> functions that handle requests and return responses

URLs and Views
    - urls.py  -> maps a URL (web address) to a view.
    - views.py -> fetches data from the database, checks authentication,
                  and sends the response back to the client.

Page not found (404)
    - Removed path('post/helloworld/', views.hello_world) from blog/blog/urls.py.
    - Ran python manage.py runserver and opened http://127.0.0.1:8000/post/helloworld/
      -> "Page not found", because Django only serves URLs listed in urlpatterns.

include() - connecting app URLs to the project
    - blog/blog/urls.py (project):
        from django.urls import include, path
        path('post/', include('posts.urls'))
          -> any URL starting with "post/" is sent to posts/urls.py
    - blog/posts/urls.py (app, created by hand):
        from . import views
        path('helloworld/', views.hello_world)
    - Result: post/ + helloworld/ = http://127.0.0.1:8000/post/helloworld/ -> "Hello, World!"
    - Each app keeps its own URLs, so the app can be reused in another project.

ROOT_URLCONF - where Django starts looking for URLs
    - In blog/blog/settings.py:
        ROOT_URLCONF = 'blog.urls'
    - Tells Django the main URL file is blog/blog/urls.py.
    - Every request is matched there first; include() then passes it on to app URL files (e.g. posts/urls.py).

HTML response with h1 tag
    - In blog/posts/views.py:
        def hello_world(request):
            return HttpResponse('<h1>Hello, World!</h1>')
    - HttpResponse can return HTML; the browser shows "Hello, World!" as a big heading.
    - Open **http://127.0.0.1:8000/post/helloworld/**

Sample dynamic URL
    - In blog/posts/urls.py:
        path('<id>/', views.post_detail)
          -> <id> matches any value in that part of the URL and passes it to the view.
    - In blog/posts/views.py:
        def post_detail(request, id):
            return HttpResponse(f"<h1>Post detail page for post {id}</h1>")
    - Open **http://127.0.0.1:8000/post/sample_dynamic_url/**
        -> shows "Post detail page for post sample_dynamic_url"
    - id is received as a string (print(type(id)) -> <class 'str'>).

Dynamic URL with int converter
    - In blog/posts/urls.py:
        path('<int:id>/', views.post_detail)
          -> <int:id> only matches whole numbers; id is passed to the view as int.
    - **http://127.0.0.1:8000/post/2/** -> "Post detail page for post 2"
    - **http://127.0.0.1:8000/post/sample_dynamic_url/** -> Page not found (404), not a number.

Clickable posts on home page
    - In blog/posts/views.py, home() wraps each post title in a link:
        <a href="/post/{post["id"]}/">
            <h2>{post["id"]}-{post["title"]}</h2>
        </a>
    - **http://127.0.0.1:8000/post/home/** -> click a title to open its detail page (e.g. /post/1/).

What happens when a link is clicked (e.g. /post/1/)
    Click "/post/1/"
       |
       v
    blog/blog/urls.py   -> 'post/' matches -> include('posts.urls')
       |                   (removes "post/", passes "1/")
       v
    blog/posts/urls.py  -> '<int:id>/' matches "1/" -> id = 1
       |
       v
    views.post_detail(request, id=1) -> returns the HTML page

    - This is NOT a redirect. The browser asks for /post/1/ once; Django looks it up
      in blog/urls.py, then posts/urls.py, and sends back the page. Address bar stays /post/1/.
    - Redirect = server tells the browser to go to a different URL (address bar changes).

Sample redirect URL
    - In blog/blog/urls.py:
        path('google/', views.google)
    - In blog/posts/views.py:
        from django.http import HttpResponseRedirect

        def google(request):
            return HttpResponseRedirect("https://www.google.com")
    - Open **http://127.0.0.1:8000/google/** -> browser is sent to https://www.google.com
      (address bar changes, unlike the /post/1/ lookup above).

Redirect fails with hard-coded URL
    - In blog/blog/urls.py the prefix was changed from 'post/' to 'posts/', and:
        path('<int:id>/', views.google)
    - In blog/posts/views.py the redirect still uses the old path:
        def google(request, id):
            return HttpResponseRedirect(f"/post/{id}/")
    - Open **http://127.0.0.1:8000/1/** -> redirects to /post/1/ -> 404 Page not found
      (only /posts/1/ exists now).
    - Lesson: changing a URL in urls.py breaks every hard-coded path in views (and home page links).
    - Fix: give the URL a name and build it from the name:
        # posts/urls.py
        path('<int:id>/', views.post_detail, name='post_detail')

        # views.py
        from django.shortcuts import redirect
        def google(request, id):
            return redirect('post_detail', id=id)   # Django builds "/posts/1/" itself
      (reverse('post_detail', args=[id]) gives the URL as a string.)
