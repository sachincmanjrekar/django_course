## django-admin startproject blog

    - Creates a new Django project named "blog".
    - Makes a folder "blog" containing:
        manage.py        -> tool to run project commands (runserver, migrate, startapp, ...)
        blog/            -> project settings package
            __init__.py  -> marks the folder as a Python package
            settings.py  -> project configuration (installed apps, database, etc.)
            urls.py      -> main URL routes of the site
            asgi.py      -> entry point for async web servers
            wsgi.py      -> entry point for regular web servers

## python manage.py runserver

    - Starts the development server at http://127.0.0.1:8000/

## python manage.py runserver 1223

    - Starts the development server on port 1223 instead (http://127.0.0.1:1223/).

## Django apps (understanding)

    - A project is like a car; apps are its parts (music player, engine, AC, ...).
    - Each app is independent and does one job.
    - An app can be copied and reused in another project,
      like moving the music player to another car.

## python manage.py startapp posts

    - Creates a new app named "posts" (run inside the folder with manage.py).
    - Makes a folder "posts" containing:
        __init__.py   -> marks the folder as a Python package
        admin.py      -> register models to show in the admin site
        apps.py       -> app configuration
        migrations/   -> database change files for this app
        models.py     -> database tables (models) for this app
        tests.py      -> tests for this app
        views.py      -> functions that handle requests and return responses

## URLs and Views

    - urls.py  -> maps a URL (web address) to a view.
    - views.py -> fetches data from the database, checks authentication,
                  and sends the response back to the client.

## Page not found (404)

    - Removed path('post/helloworld/', views.hello_world) from blog/blog/urls.py.
    - Ran python manage.py runserver and opened http://127.0.0.1:8000/post/helloworld/
      -> "Page not found", because Django only serves URLs listed in urlpatterns.

## include() - connecting app URLs to the project

    - blog/blog/urls.py (project):
        from django.urls import include, path
        path('post/', include('posts.urls'))
          -> any URL starting with "post/" is sent to posts/urls.py
    - blog/posts/urls.py (app, created by hand):
        from . import views
        path('helloworld/', views.hello_world)
    - Result: post/ + helloworld/ = http://127.0.0.1:8000/post/helloworld/ -> "Hello, World!"
    - Each app keeps its own URLs, so the app can be reused in another project.

## ROOT_URLCONF - where Django starts looking for URLs

    - In blog/blog/settings.py:
        ROOT_URLCONF = 'blog.urls'
    - Tells Django the main URL file is blog/blog/urls.py.
    - Every request is matched there first; include() then passes it on to app URL files (e.g. posts/urls.py).

## HTML response with h1 tag

    - In blog/posts/views.py:
        def hello_world(request):
            return HttpResponse('<h1>Hello, World!</h1>')
    - HttpResponse can return HTML; the browser shows "Hello, World!" as a big heading.
    - Open **http://127.0.0.1:8000/post/helloworld/**

## Sample dynamic URL

    - In blog/posts/urls.py:
        path('<id>/', views.post_detail)
          -> <id> matches any value in that part of the URL and passes it to the view.
    - In blog/posts/views.py:
        def post_detail(request, id):
            return HttpResponse(f"<h1>Post detail page for post {id}</h1>")
    - Open **http://127.0.0.1:8000/post/sample_dynamic_url/**
        -> shows "Post detail page for post sample_dynamic_url"
    - id is received as a string (print(type(id)) -> <class 'str'>).

## Dynamic URL with int converter

    - In blog/posts/urls.py:
        path('<int:id>/', views.post_detail)
          -> <int:id> only matches whole numbers; id is passed to the view as int.
    - **http://127.0.0.1:8000/post/2/** -> "Post detail page for post 2"
    - **http://127.0.0.1:8000/post/sample_dynamic_url/** -> Page not found (404), not a number.

## Clickable posts on home page

    - In blog/posts/views.py, home() wraps each post title in a link:
        <a href="/post/{post["id"]}/">
            <h2>{post["id"]}-{post["title"]}</h2>
        </a>
    - **http://127.0.0.1:8000/post/home/** -> click a title to open its detail page (e.g. /post/1/).

## What happens when a link is clicked (e.g. /post/1/)

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

## Sample redirect URL

    - In blog/blog/urls.py:
        path('google/', views.google)
    - In blog/posts/views.py:
        from django.http import HttpResponseRedirect

        def google(request):
            return HttpResponseRedirect("https://www.google.com")
    - Open **http://127.0.0.1:8000/google/** -> browser is sent to https://www.google.com
      (address bar changes, unlike the /post/1/ lookup above).

## Redirect fails with hard-coded URL

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

## Redirect fixed by giving URLs a name

    - In blog/posts/urls.py:
        path('home/', views.home, name='home'),
        path('<int:id>/', views.post_detail, name='post_detail')
    - In blog/posts/views.py:
        from django.urls import reverse

        def google(request, id):
            url = reverse('post_detail', args=[id])   # builds "/post/1/" from the name
            return HttpResponseRedirect(url)
    - Open **http://127.0.0.1:8000/1/** -> redirects to /post/1/
    - If the prefix in blog/blog/urls.py changes (e.g. 'post/' -> 'posts/'), the redirect still works.
    - Still hard-coded: links in home() use href="/post/{post["id"]}/";
      could use reverse('post_detail', args=[post["id"]]) as well.
    - reverse() takes the URL's NAME and builds the full path (prefix included):
        reverse('post_detail', args=[1])   # -> "/post/1/"
        reverse('home')                    # -> "/post/home/"
      How it builds "/post/1/":
        1. finds name='post_detail' in posts/urls.py -> pattern '<int:id>/'
        2. sees posts/urls.py is included under 'post/' in blog/bloyes
        g/urls.py
        3. joins them and fills in id: 'post/' + '1/' -> "/post/1/"
      Using it in home():
        for post in post_list:
            url = reverse('post_detail', args=[post["id"]])
            html += f'''
                <div>
                    <a href="{url}">
                        <h2>{post["id"]}-{post["title"]}</h2>
                    </a>
                    <p>{post["content"]}</p>
                </div>
            '''
      If 'post/' changes to 'posts/' in blog/blog/urls.py, links become /posts/1/ automatically.
      Check: print(reverse('home')) prints /post/home/ in the terminal.
    - Every URL starts at blog/blog/urls.py: because settings.py has
      ROOT_URLCONF = 'blog.urls', every request is matched first there.

    Without redirect (clicking a link to /post/1/) -> ONE request:
        browser asks for /post/1/
           blog/blog/urls.py   -> 'post/' matches -> include('posts.urls')
           blog/posts/urls.py  -> '<int:id>/' matches "1/" -> views.post_detail(id=1)
           post_detail() returns the post page

    With redirect (opening /1/) -> TWO requests, blog/urls.py is checked twice:
        Request 1: browser asks for /1/
           blog/blog/urls.py   -> '<int:id>/' matches -> views.google(id=1)
           google() replies: "go to /post/1/"  (redirect)

        Request 2: browser now asks for /post/1/  (address bar changes)
           blog/blog/urls.py   -> 'post/' matches -> include('posts.urls')
           blog/posts/urls.py  -> '<int:id>/' matches "1/" -> views.post_detail(id=1)
           post_detail() returns the post page

## Home page with a template (render)

    - blog/posts/templates/home.html -> the HTML page (<h1>Home Page</h1>).
    - blog/blog/settings.py -> add the app to INSTALLED_APPS:
        INSTALLED_APPS = [
            ...
            'posts',
        ]
    - blog/posts/views.py:
        from django.shortcuts import render

        def home(request):
            return render(request, 'home.html')
          -> finds home.html and sends it back as the response.
    - Why settings.py is needed:
        TEMPLATES has 'APP_DIRS': True -> Django looks for templates in the
        templates/ folder of every app in INSTALLED_APPS.
        Without 'posts' there, Django never looks in posts/templates/
        -> error: TemplateDoesNotExist: home.html
    - Open **http://127.0.0.1:8000/post/home/** -> shows "Home Page".

## APP_DIRS: True vs False

    - In blog/blog/settings.py, TEMPLATES:
        'DIRS': [],
        'APP_DIRS': True,
    - APP_DIRS: True  -> Django searches the templates/ folder of every app in
                         INSTALLED_APPS (e.g. posts/templates/) -> home.html found.
    - APP_DIRS: False -> app folders are skipped; only folders listed in 'DIRS' are
                         searched. DIRS is empty -> error: TemplateDoesNotExist: home.html
    - Fix 1 (usual): set 'APP_DIRS': True
    - Fix 2: keep False and list the folder yourself:
        'DIRS': [BASE_DIR / 'posts' / 'templates'],
        'APP_DIRS': False,
      (DIRS is normally used for a shared project-level templates/ folder.)
    - 'posts' in INSTALLED_APPS + 'APP_DIRS': True work together;
      both are needed to find posts/templates/home.html.

## Template namespacing (posts/templates/posts/home.html)

    - Django searches templates in this order:
        1. folders in 'DIRS'
        2. templates/ folder of each app, in INSTALLED_APPS order
      It uses the FIRST home.html it finds and stops looking.
    - Problem: if another app (or a project templates/ folder) also has home.html,
      Django may return that one, and ours is never used.
    - Fix: put the template in a subfolder named after the app:
        posts/
          templates/
            posts/          <- extra folder named after the app
              home.html
    - In blog/posts/views.py:
        return render(request, 'posts/home.html')
      -> 'posts/home.html' can only match posts/templates/posts/home.html.

## Passing variables to a template (context)

    - blog/posts/views.py:
        return render(request, 'posts/home.html', {'name': 'Sachin'})
          -> 3rd argument = context: a dictionary of variables for the template.
    - blog/posts/templates/posts/home.html:
        <h1>Welcome - {{ name }}</h1>
    - Each key ('name') becomes a template variable; {{ name }} is replaced by its
      value ('Sachin') before the page is sent.
    - Browser receives plain HTML: <h1>Welcome - Sachin</h1>
    - Open **http://127.0.0.1:8000/post/home/** -> "Welcome - Sachin"
    - Change the value in views.py -> page changes; home.html stays the same.

## for tag in a template

    - blog/posts/views.py:
        return render(request, 'posts/home.html', {'posts': post_list})
    - blog/posts/templates/posts/home.html:
        {% for post in posts %}
            <div>
                <h2>{{ post.title }}</h2>
                <p>{{ post.content }}</p>
            </div>
        {% endfor %}
    - {% ... %} = tag (logic: for, if, ...);  {{ ... }} = variable (outputs a value).
    - {% for post in posts %} repeats the block once for each item in post_list.
    - {% endfor %} is required (templates have no indentation rules like Python).
    - {{ post.title }} -> templates use a DOT even for dictionaries
      (in Python it would be post["title"]).
    - Open **http://127.0.0.1:8000/post/home/** -> shows all 3 posts.

## if tag in a template

    - blog/posts/templates/posts/home.html:
        {% if posts %}
            <h1>Blog Posts</h1>
            {% for post in posts %}
                <div>
                    <h2>{{ post.title }}</h2>
                    <p>{{ post.content }}</p>
                </div>
            {% endfor %}
        {% else %}
            <h1>No posts available.</h1>
        {% endif %}
    - {% if posts %} is true when posts has items; an empty list is false (like Python).
    - {% else %} runs when the list is empty.
    - {% endif %} is required to close the if.
    - Test: uncomment  # post_list = []  in views.py -> page shows "No posts available."
    - Shortcut: {% empty %} inside the for loop does the same:
        {% for post in posts %}
            ...
        {% empty %}
            <h1>No posts available.</h1>
        {% endfor %}

## empty tag and forloop variables

    - blog/posts/templates/posts/home.html:
        <h1>Blog Posts</h1>
        {% for post in posts %}
            {{ forloop.counter }}
            <div>
                <h2>{{ post.title }}</h2>
                <p>{{ post.content }}</p>
            </div>
        {% empty %}
            <p>No posts available.</p>
        {% endfor %}
    - {% empty %} runs only when posts is empty (or missing).
      Same as the if/else version, but shorter.
      Note: <h1>Blog Posts</h1> is outside the loop, so it shows even with no posts.
    - forloop variables (available inside every {% for %} loop), for 3 posts:
        forloop.counter      -> position from 1          -> 1, 2, 3
        forloop.counter0     -> position from 0          -> 0, 1, 2
        forloop.revcounter   -> counting down to 1       -> 3, 2, 1
        forloop.revcounter0  -> counting down to 0       -> 2, 1, 0
        forloop.first        -> True on the first item   -> True, False, False
        forloop.last         -> True on the last item    -> False, False, True
        forloop.parentloop   -> the outer loop (in nested loops)
    - Example: {% if forloop.first %}<b>Latest</b>{% endif %} marks only the first post.
    - Open **http://127.0.0.1:8000/post/home/** -> shows 1, 2, 3 before each post.

## Template filters

    - A filter changes how a variable is shown: {{ variable | filter }}
    - Filters can be chained; they run left to right:
        {{ name | capfirst | truncatechars:2 }}
    - Filter argument comes after a colon, with NO space:
        truncatechars:2    -> correct
        truncatechars: 2   -> error: truncatechars requires 2 arguments, 1 provided
    - blog/posts/views.py:
        return render(request, 'posts/home.html', {'posts': post_list, 'name': 'sachin'})
    - blog/posts/templates/posts/home.html:
        {{ name | capfirst | truncatechars:2 }}   -> "sachin" -> "Sachin" -> "S…"
        {{ post.title | title }}                  -> "My first post" -> "My First Post"
        {{ post.content | truncatewords:4 }}      -> "This is my first …"
    - Filters used:
        capfirst          -> first letter uppercase
        title             -> first letter of every word uppercase
        truncatechars:N   -> cut to N characters, INCLUDING the "…"
        truncatewords:N   -> keep first N words, then add "…"

## Showing a single post (post.html)

    - blog/posts/templates/posts/home.html -> each title links to its post:
        <a href="/post/{{ post.id }}/"><h2>{{ post.title | title }}</h2></a>
    - blog/posts/urls.py -> '<int:id>/' sends the request to post_detail (as before).
    - blog/posts/views.py -> post_detail() finds the post and returns a template:
        return render(request, 'posts/post.html', {"post_dict": post_dict})
    - blog/posts/templates/posts/post.html (new) -> shows that one post:
        <h1>{{ post_dict.title | title }}</h1>
        <p>{{ post_dict.content }}</p>
    - **http://127.0.0.1:8000/post/home/** lists posts; click one ->
      **http://127.0.0.1:8000/post/1/** shows the full content.
    - Hard-coded link again (/post/...). Template version of reverse() is the url tag:
        <a href="{% url 'post_detail' post.id %}">

## Back to Home link and the url tag

    - blog/posts/templates/posts/post.html:
        <a href="/post/home/">Back to Home</a>
    - Problem: post URLs are now hard-coded in two places:
        post.html -> href="/post/home/"
        home.html -> href="/post/{{ post.id }}/"
      If 'post/' changes to 'posts/' in blog/blog/urls.py, both links break (404).
    - Fix: {% url %} tag = template version of reverse(); builds the link from the URL NAME
      (names already set in posts/urls.py: name='home', name='post_detail'):
        <!-- post.html -->
        <a href="{% url 'home' %}">Back to Home</a>

        <!-- home.html -->
        <a href="{% url 'post_detail' post.id %}"><h2>{{ post.title | title }}</h2></a>
    - {% url 'home' %}                -> /post/home/
      {% url 'post_detail' post.id %} -> /post/1/  (value after the name fills <int:id>)
    - Change 'post/' to 'posts/' in urls.py -> all links update automatically (one place only).
    - Example: change home URL from 'home/' to 'main/' in blog/posts/urls.py:
        path('main/', views.home, name='home'),   # path changed, name stays 'home'
      Hard-coded link in post.html:
        <a href="/post/home/">Back to Home</a>
          -> still goes to /post/home/ -> no longer exists -> 404 Page not found
          -> must find and fix /post/home/ by hand everywhere
      url tag in post.html:
        <a href="{% url 'home' %}">Back to Home</a>
          1. finds name='home' -> now points to 'main/'
          2. adds prefix 'post/' from blog/urls.py
          3. link becomes /post/main/ automatically -> works
    - Lesson: the NAME stays the same, only the path changes.
      Links using the name follow the change; hard-coded links break.
    - Fixed in blog/posts/templates/posts/post.html:
        <a href="{% url 'home' %}">Back to Home</a>
          -> /post/home/ now; becomes /post/main/ automatically if the path is renamed.
    - {% url 'home' %} in a template is just like reverse('home') in views.py:
        views.py:  reverse('home')                    -> "/post/home/"
        template:  {% url 'home' %}                   -> /post/home/
        views.py:  reverse('post_detail', args=[1])   -> "/post/1/"
        template:  {% url 'post_detail' 1 %}          -> /post/1/
    - Still hard-coded in home.html: <a href="/post/{{ post.id }}/">
      fix would be: <a href="{% url 'post_detail' post.id %}">
    - Fixed in blog/posts/templates/posts/home.html:
        <a href="{% url 'post_detail' post.id %}"><h2>{{ post.title | title }}</h2></a>
          -> /post/1/, /post/2/, /post/3/
          (same as reverse('post_detail', args=[post.id]) in views.py)
    - Now both templates use {% url %}; no hard-coded post links left.
      Change 'post/' in blog/urls.py -> every link follows automatically.

## Project-level templates folder (DIRS)

    - By default (APP_DIRS: True) Django looks in each app's templates/ folder (e.g. posts/templates/).
    - Another folder can be added in blog/blog/settings.py:
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
      BASE_DIR = folder with manage.py (Django_course/blog/) -> adds blog/templates/
    - Search order:
        1. DIRS        -> blog/templates/          (searched first)
        2. app folders -> posts/templates/ ...      (APP_DIRS: True)
    - Example page:
        # blog/blog/urls.py
        path("global/", views.global1, name="global"),

        # blog/posts/views.py
        def global1(request):
            return render(request, 'global.html', {'name': 'sachin'})
      'global.html' (no app prefix) is found in blog/templates/global.html
      -> **http://127.0.0.1:8000/global/**
    - Which to use:
        blog/templates/          -> shared by the whole site (base layout, navbar, error pages)
        posts/templates/posts/   -> belongs to one app (moves with the app if reused)
    - print("BASE DIR:", BASE_DIR / "templates") in settings.py shows the path at server start.

## Template inheritance (extends and block)

    - One base layout (parent); child templates fill in only their own part.
    - blog/templates/base.html (parent, shared layout):
        <nav>
            <a href="{% url 'home' %}">Back to Home</a>
        </nav>
        {% block body %}
        {% endblock body %}
        <footer>
            FOOTER
        </footer>
    - blog/posts/templates/posts/post.html (child; home.html works the same way):
        {% extends 'base.html' %}

        {% block body %}
            <h1>{{ post_dict.title | title }}</h1>
            <p>{{ post_dict.content }}</p>
        {% endblock body %}
    - {% extends 'base.html' %} -> start from base.html; must be the FIRST tag in the file.
    - {% block body %} in base = empty spot a child can fill.
    - Child's {% block body %} ... {% endblock body %} replaces that spot.
    - Result: every page gets the same <html>, <head>, nav and footer; only the middle changes.
    - base.html is found in blog/templates/ because of 'DIRS': [BASE_DIR / "templates"].
    - Benefits:
        no repeated HTML skeleton in every template
        "Back to Home" link lives once in base.html -> on every page
        change nav/footer in one file only
    - Improvement: all pages share <title>Document</title>; add
        {% block title %}Blog{% endblock %} in base.html so each child can set its own title.
    - Improvement done:
        # blog/templates/base.html
        <title>{% block title %}Blog{% endblock %}</title>
          -> "Blog" is the default title for every page.

        # blog/posts/templates/posts/post.html
        {% block title %}{{ post_dict.title }}{% endblock %}
          -> overrides the default; browser tab shows the post title.
    - **http://127.0.0.1:8000/post/1/** -> tab shows "My first post"
      **http://127.0.0.1:8000/post/home/** -> no title block in home.html -> tab shows "Blog"
    - A child only overrides the blocks it defines; others keep the base's default content.

## Static files (CSS)

    - Static files = CSS, JavaScript, images (files sent as they are, not templates).
    - Put them in the app's static/ folder, namespaced like templates:
        posts/
          static/
            posts/          <- extra folder named after the app
              home.css
              post.css
    - blog/posts/static/posts/home.css:
        body {
            background-color: aqua;
        }
    - blog/blog/settings.py (already there by default):
        STATIC_URL = 'static/'   -> static files are served under /static/...
        'django.contrib.staticfiles' in INSTALLED_APPS -> finds each app's static/ folder
    - blog/templates/base.html -> empty css block inside <head>:
        {% block css %} {% endblock css %}
    - blog/posts/templates/posts/home.html (post.html same, with post.css):
        {% extends 'base.html' %}

        {% load static %}
        {% block css %}
            <link rel="stylesheet" href="{% static 'posts/home.css' %}">
        {% endblock css %}
    - {% load static %} -> makes the {% static %} tag available in this template
      (needed in every template that uses it, even children).
    - {% static 'posts/home.css' %} -> /static/posts/home.css
      (builds the URL from STATIC_URL, like {% url %} does for pages).
    - Each page adds its own CSS through the css block in <head>.

## Global static file (STATICFILES_DIRS)

    - One CSS file for the whole site, loaded once in base.html.
    - blog/blog/settings.py:
        STATIC_URL = 'static/'
        STATICFILES_DIRS = [
            BASE_DIR / "static"
        ]
      -> adds blog/static/ (besides each app's static/ folder);
         like 'DIRS' for templates, but for static files.
    - blog/static/style.css -> site-wide CSS:
        body {
            background-color: aqua;
        }
    - blog/templates/base.html:
        {% load static %}
        ...
        <link rel="stylesheet" href="{% static 'style.css' %}">
        {% block css %} {% endblock css %}
      -> {% static 'style.css' %} -> /static/style.css (found in blog/static/)
      -> every page that extends base.html gets it.
      -> css block kept so a page can still add its own extra CSS.
    - home.html and post.html no longer link their own CSS.
    - Which to use:
        blog/static/            -> CSS/JS used by the whole site
        posts/static/posts/     -> files that belong to one app

## Removing the global static file

    - Deleted blog/static/style.css (had: body { background-color: aqua; }).
    - Page was still blue -> browser was showing its CACHED copy of the old CSS.
        Fix: Ctrl + F5 (hard refresh), or F12 -> Network -> tick "Disable cache" -> refresh.
    - base.html still had <link rel="stylesheet" href="{% static 'style.css' %}">
        -> every page asked for a missing file -> 404 for /static/style.css in the server log.
        Fix: removed that link line from base.html.
    - Kept {% load static %} and {% block css %}{% endblock css %} in base.html,
      so a page can still add its own CSS later.

## Bootstrap templates with base.html

    - base.html (blog/templates/) = full Bootstrap layout: <head> with Bootstrap CSS/fonts,
      navbar, footer, Bootstrap JS. Pages only fill {% block body %}.
    - base.html fixes:
        {% block title %}Blog{% endblock title %}  -> default tab title (empty block = blank tab)
        ABlog / Home links: href="#" -> href="{% url 'home' %}"  (no hard-coded links)
        Pagination moved OUT of base.html -> it would show on every page, even single posts.
        Removed a stray </div> that closed nothing.
        <div class="container"> now wraps navbar AND {% block body %} -> content lines up with navbar.
    - blog/posts/templates/posts/index.html (home page, views.py renders 'posts/index.html'):
        {% extends 'base.html' %}

        {% block body %}
            <h1 class="my-3">Latest</h1>
            <div class="row">
                {% for post in posts %}
                    ...Bootstrap card: {{ post.title }}, {{ post.content }},
                       <a href="{% url 'post_detail' post.id %}" class="btn btn-dark">Read More</a>
                {% endfor %}
            </div>
            ...pagination (Previous 1 2 3 Next) - only on the home page
        {% endblock body %}
      Missing {% endblock body %} -> error: TemplateSyntaxError: Unclosed tag 'block'
    - blog/posts/templates/posts/post.html (single post):
        Was a full copied page (own <head>, navbar, footer) -> changed back to:
        {% extends 'base.html' %}

        {% block title %}{{ post_dict.title }}{% endblock title %}

        {% block body %}
            ...post title, tags, {{ post_dict.content }}, comments
        {% endblock body %}
    - Lesson: keep shared parts (head, navbar, footer) ONLY in base.html;
      page-specific parts (posts list, pagination, single post) in the child templates.
    - Note for later: <form method='POST'> needs {% csrf_token %} inside it, otherwise 403 error.

## include tag (reusable template pieces)

    - Moved the post card HTML into its own file and included it in the loop.
    - blog/posts/templates/posts/includes/postcard.html (new) -> HTML for ONE card:
        <div class="col-sm-6 mb-3 mb-sm-0">
            <div class="card mb-3" style="max-width: 540px;">
                ...
                <h5 class="card-title fw-bold">{{ post.title }}</h5>
                <p class="card-text fw-normal">{{ post.content }}</p>
                <a href="{% url 'post_detail' post.id %}" class="btn btn-dark">Read More</a>
                ...
            </div>
        </div>
    - blog/posts/templates/posts/index.html:
        {% for post in posts %}
            {% include 'posts/includes/postcard.html' %}
        {% endfor %}
    - {% include %} inserts another template's content at that spot.
    - The included template sees the SAME variables as where it is included
      -> {{ post.title }} works in postcard.html because post comes from the for loop.
    - Path 'posts/includes/postcard.html' is found in posts/templates/ like any template.
    - extends vs include:
        {% extends %} -> child fills parts of a parent; for the overall layout (base.html);
                         only one per template, must be the first tag.
        {% include %} -> parent pulls in a small piece; for reusable parts (cards, navbar,
                         comment box); as many as you like, anywhere.
    - Benefits: index.html is shorter; the same card can be reused on other pages
      (tag page, search results) without copying.

## Http404 and a custom 404 page

    - Error: AttributeError: 'Http404' object has no attribute 'get'
        cause: return Http404()  -> Http404 is an EXCEPTION, not a response.
        fix:   raise Http404()
    - HttpResponseNotFound vs Http404:
        HttpResponseNotFound("...") -> response object -> use return -> shows your exact text
        Http404                     -> exception       -> use raise  -> shows Django's 404 page
                                                          (your 404.html when DEBUG = False)
      raise Http404() is the usual Django way; works even from inside helper functions.
    - blog/posts/views.py:
        from django.http import Http404

        if not post_dict:
            raise Http404()
    - blog/templates/404.html (new) -> custom page, extends base.html (same navbar/footer):
        {% extends 'base.html' %}

        {% block body %}
            <h1 class="text-danger text-center">404 - Page Not Found</h1>
            <p>Sorry, the page you are looking for does not exist.</p>
        {% endblock body %}
      Django looks for a template named exactly 404.html (found in blog/templates/ via DIRS).
    - blog/blog/settings.py:
        DEBUG = False
        ALLOWED_HOSTS = ["*"]
      404.html only shows when DEBUG = False
        (DEBUG = True -> Django's yellow developer error page instead).
      With DEBUG = False, ALLOWED_HOSTS must be set, otherwise every request -> 400 Bad Request.
    - Test: **http://127.0.0.1:8000/post/51/** or any made-up URL -> custom 404 page.
    - Notes:
        DEBUG = False -> runserver stops serving /static/ files (Bootstrap CDN still works).
                         Switch back to DEBUG = True while developing.
        ALLOWED_HOSTS = ["*"] only for local; on a real server list the domain, e.g. ["myblog.com"].
        SECRET_KEY is in settings.py (public on GitHub); before deploying, move it to an
        environment variable and generate a new one.

## Context processors (data for every template)

    - Problem: navbar Categories dropdown lives in base.html, but data passed from one view
      (home) only reaches that page -> dropdown empty on post page.
    - First try: {% block categories %} in base.html's <ul class="dropdown-menu">, filled from
      index.html with an <h1> + row/col-md-4 buttons -> buttons overlapped.
        why: a child block replaces the parent's block WHERE THE PARENT PUT IT (inside the
             dropdown), not where it is written in the child.
             block placed inside {% block body %} in the child -> rendered twice.
             .dropdown-menu is ~160px wide -> col-md-4 = ~53px each -> wide buttons overlap.
             <ul> should only contain <li>.
        dropdown content must be: <li><a class="dropdown-item" href="#">...</a></li>
    - Better: context processor = function(request) -> returns a dict; Django adds that dict
      to the context of EVERY template rendered with render().
    - blog/posts/context_processor.py (new):
        def cateofies(request):
            categories = ["Technology", "Science", "Health", "Travel", "Food"]
            return {'categories': categories}
    - blog/blog/settings.py -> TEMPLATES -> OPTIONS -> context_processors:
        'posts.context_processor.cateofies'      (app.file.function)
    - blog/templates/base.html (dropdown):
        {% for category in categories %}
            <li><a class="dropdown-item" href="#">{{ category }}</a></li>
        {% endfor %}
    - Result: categories show in the dropdown on home AND post pages; no view passes them.
    - Notes:
        Use for data every page needs (navbar menus, site name, logged-in user).
        Django's convention: name the file context_processors.py (not required).
        DEBUG = True and ALLOWED_HOSTS = [] again for development.

## STATICFILES_DIRS emptied (no global static folder)

    - blog/static/ (global style.css) was deleted earlier; settings still pointed to it.
    - blog/blog/settings.py:
        STATICFILES_DIRS = []          (was [BASE_DIR / "static"])
    - why: a folder listed in STATICFILES_DIRS that does not exist -> Django warning
      (staticfiles.W004: The directory ... does not exist).
    - App static files (posts/static/posts/...) still work without it -> found via APP_DIRS-like
      app lookup (AppDirectoriesFinder). STATICFILES_DIRS is only for extra, project-level folders.
    - Add it back when a global static/ folder is created again.

## Models (first model: Post)

    - Model = Python class that describes a database table; each attribute = a column.
      Django creates the table from it (no SQL needed).
    - blog/posts/models.py:
        from django.db import models

        class Post(models.Model):
            post_title = models.CharField(max_length=60)
            post_content = models.TextField()
            published_date = models.DateTimeField(auto_now=True)
    - Fields:
        CharField(max_length=60) -> short text, max_length is required
        TextField()              -> long text, no limit (post body)
        DateTimeField(...)       -> date + time
            auto_now=True     -> updated to "now" on EVERY save (= last modified)
            auto_now_add=True -> set once when the row is created (= published / created date)
    - Django adds an id column automatically (primary key) -> post.id
    - The model is not in the database yet -> needs migrations:
        python manage.py makemigrations -> writes posts/migrations/0001_initial.py (Create model Post)
        python manage.py migrate        -> creates the table in db.sqlite3
      makemigrations --dry-run -> shows what would be created without writing files.

## Migrations (makemigrations and migrate)

    - Workflow (from the course slide):

        +------------------+     +------------------+     +--------------------+
        | Add/Change model | --> |  makemigrations  | --> | Generates          |
        |  (models.py)     |     |                  |     | migration file     |
        +------------------+     +------------------+     +--------------------+
                                                                    |
                                                                    v
        +------------------+     +------------------+     +--------------------+
        |        DB        | <-- |   Executes SQL   | <-- |      migrate       |
        |   (db.sqlite3)   |     |                  |     |                    |
        +------------------+     +------------------+     +--------------------+
    - python manage.py makemigrations
        -> reads models.py, compares with existing migrations, writes the changes as a file:
           blog/posts/migrations/0001_initial.py   (CreateModel Post)
        -> nothing in the database changes yet; it is only a plan (Python file).
    - python manage.py migrate
        -> runs the migration files that are not applied yet -> creates the table in db.sqlite3
           (table name: posts_post = appname_modelname)
    - python manage.py sqlmigrate posts 0001
        -> shows the SQL a migration will run (read-only, changes nothing):
           CREATE TABLE "posts_post" (
               "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
               "post_title" varchar(60) NOT NULL,
               "post_content" text NOT NULL,
               "published_date" datetime NOT NULL);
        -> CharField -> varchar(60), TextField -> text, DateTimeField -> datetime
    - Order I ran: makemigrations -> sqlmigrate posts 0001 -> migrate
    - Inside 0001_initial.py:
        initial = True             -> first migration of the app
        dependencies = []          -> does not depend on other migrations
        CreateModel(name='Post', fields=[...])
            id -> BigAutoField(primary_key=True)  added automatically by Django
            post_title, post_content, published_date -> same as models.py
    - python manage.py showmigrations posts
        [X] 0001_initial  -> applied (table exists)
        [ ] 0001_initial  -> not applied yet (run migrate)
    - Rule: every time models.py changes (new field, rename, delete)
        -> makemigrations -> migrate   (new file 0002_..., 0003_...)
    - Migration files belong in the repo (they are the history of the database structure);
      never edit or delete applied ones by hand.

## Changing a model (second migration)

    - blog/posts/models.py:
        published_date = models.DateTimeField(auto_now=True)   (before)
        published_date = models.DateField(auto_now=True)       (after)
        DateTimeField -> date + time (2026-10-22 12:39)
        DateField     -> date only   (2026-10-22)
    - Commands I ran:
        python manage.py makemigrations   -> new file 0002_alter_post_published_date.py
        python manage.py showmigrations   -> [X] 0001_initial, [ ] 0002_... (not applied yet)
        python manage.py migrate          -> applies 0002
        python manage.py showmigrations   -> [X] 0001_initial, [X] 0002_alter_post_published_date
    - Inside 0002_alter_post_published_date.py:
        dependencies = [('posts', '0001_initial')]  -> runs only after 0001 (migrations form a chain)
        AlterField(model_name='post', name='published_date', field=models.DateField(auto_now=True))
        file name is generated from the change: alter + model + field
    - sqlmigrate posts 0002 -> SQLite cannot change a column type directly, so Django:
        1. CREATE TABLE "new__posts_post" (... "published_date" date ...)
        2. INSERT INTO new__posts_post SELECT ... FROM posts_post   (copies existing rows)
        3. DROP TABLE "posts_post"
        4. ALTER TABLE "new__posts_post" RENAME TO "posts_post"
    - Each model change = one new numbered migration file; old ones stay untouched.

## Django shell: creating objects (save and create)

    - python manage.py shell
        -> Python prompt with the project loaded (settings, models ready to use).
    - Way 1: object + save()  (2 steps)
        >>> from posts.models import Post
        >>> post = Post(post_title="title 1", post_content="content 1")
        >>> post.save()
        -> Post(...) only builds the object in memory (post.id is None);
           save() runs INSERT -> row in db, post.id = 1.
        -> useful when you want to change fields before saving:
             post.post_title = "new title"
             post.save()      -> same object again -> UPDATE (not a new row)
    - Way 2: objects.create()  (1 step)
        >>> Post.objects.create(post_title="title 2", post_content="content 2")
        -> builds AND saves in one call, returns the saved object (id = 2).
    - Creating object (course slide):

                +------------------------------+
                |  post1 = Post(title=...)     |
                |  post1.save()                |
                +------------------------------+
                               |
                               v
                       +---------------+
                       |  DJANGO ORM   |   (turns Python into SQL)
                       +---------------+
                               |
                               v
                       +---------------+
                       | SQL - INSERT  |   -> new row in posts_post
                       +---------------+

    - Making query (course slide):

            Post  .  objects  .  create(title=...)
             |          |            |
             v          v            v
           Model   Model Manager  Query Method
          (table)  (door to the   (what to do: create, all,
                    table)         get, filter...)

    - Post.objects = the "manager" -> the door to the table (create, all, get, filter...).
    - published_date not passed -> auto_now=True fills today's date automatically.
    - Check: Post.objects.all()  -> <QuerySet [<Post: Post object (1)>, <Post: Post object (2)>]>
    - Result in db (posts_post):
        id 1 | title 1 | content 1 | 2026-10-22
        id 2 | title 2 | content 2 | 2026-10-22
    - exit() -> leave the shell.

## Seeing the SQL Django runs (connection.queries)

    - What I ran in python manage.py shell:
        >>> from posts.models import Post
        >>> Post
        <class 'posts.models.Post'>
        >>> post1 = Post(post_title="title 1", post_content="content 1")
        >>> post1.save()
        >>> Post.objects.create(post_title="title 2",post_content="content 2")
        <Post: Post object (2)>
        >>> Post.objects.create(post_title="title 3",post_content="content 3")
        <Post: Post object (3)>
        >>> from django.db import connection
        >>> connection.queries
    - connection.queries -> list of every SQL query run in this shell session, with time:
        INSERT INTO "posts_post" ("post_title", "post_content", "published_date")
            VALUES ('title 1', 'content 1', '2026-10-22') RETURNING "posts_post"."id"
        (same INSERT for title 2 and title 3, each 'time': '0.003' seconds)
    - What it shows:
        save() and objects.create() -> both run the SAME INSERT (create = build + save).
        id is not in the INSERT -> the database gives it (AUTOINCREMENT),
            RETURNING "id" -> Django puts it back into the object (post1.id = 1).
        published_date '2026-10-22' -> filled by auto_now=True, date only (DateField).
    - <Post: Post object (2)> -> default text for an object = "Post object (id)".
      (can be made readable later with a __str__ method in the model.)
    - connection.queries only records queries when DEBUG = True.

## all() and QuerySet (reading rows)

    - What I ran in python manage.py shell:
        >>> Post.objects.all()
        <QuerySet [<Post: Post object (1)>, <Post: Post object (2)>, <Post: Post object (3)>]>
        >>> data = Post.objects.all()
        >>> data[0]
        <Post: Post object (1)>
        >>> data[0].post_title
        'title 1'
        >>> data[0].id
        1
      (I also typed date = Post.objects.all() by mistake -> just another variable, not used.)
    - Parts of the call (course slide):

            Post  .  objects  .  all()
             |          |          |
             v          v          v
           Model   Model Manager  Query Method

    - Flow (course slide):

        +-------------------+     +-----+     +-------+
        | Post.objects.all()| --> | ORM | --> |  SQL  |   SELECT ... FROM "posts_post"
        +-------------------+     +-----+     +-------+
                                                  |
                                                  v
        +-------------------+     +-----+     +-------+
        |     QuerySet      | <-- | ORM | <-- |  DB   |   rows come back
        +-------------------+     +-----+     +-------+

      ORM works both ways: Python -> SQL going in, rows -> Python objects coming out.
    - QuerySet = list-like collection of model objects; each table row -> one object
      (course slide):

        +-----------+          +----+------------+--------------+----------------+
        | QuerySet  |          | id | post_title | post_content | published_date |
        +-----------+          +----+------------+--------------+----------------+
        |  Object   |  <-----  | 1  | title 1    | content 1    | 2026-10-22     |
        |  Object   |  <-----  | 2  | title 2    | content 2    | 2026-10-22     |
        |  Object   |  <-----  | 3  | title 3    | content 3    | 2026-10-22     |
        +-----------+          +----+------------+--------------+----------------+

    - Using a QuerySet:
        data[0]             -> first object (index starts at 0, like a list)
        data[0].post_title  -> a column value = attribute of the object
        data[0].id          -> id added automatically by Django
        for post in data: ... -> loop over it (same as a list in a template {% for %})
    - all() returns ALL rows; the SQL runs only when the data is actually used
      (printing, indexing, looping) -> QuerySets are "lazy".

## get(), filter(), exclude() (reading specific rows)

    - (examples run on my 3 posts: title 1, title 2, title 3)
    - get() -> exactly ONE object (not a QuerySet)
        >>> Post.objects.get(id=1)
        <Post: Post object (1)>
        errors:
            Post.objects.get(id=50)    -> DoesNotExist: Post matching query does not exist.
            Post.objects.get(id__gt=1) -> MultipleObjectsReturned: get() returned more than
                                          one Post -- it returned 2!
        -> use get() only when exactly one row must match (usually id).
    - filter() -> QuerySet of ALL rows that match (0, 1 or many)
        >>> Post.objects.filter(post_title="title 2")
        <QuerySet [<Post: Post object (2)>]>
        >>> Post.objects.filter(id__gt=1)
        <QuerySet [<Post: Post object (2)>, <Post: Post object (3)>]>
        >>> Post.objects.filter(post_title="nope")
        <QuerySet []>            -> no match = empty QuerySet, NO error
    - exclude() -> QuerySet of all rows that do NOT match (opposite of filter)
        >>> Post.objects.exclude(id=1)
        <QuerySet [<Post: Post object (2)>, <Post: Post object (3)>]>
    - SQL behind it -> print(Post.objects.filter(id=1).query):
        SELECT "posts_post"."id", "posts_post"."post_title", ... FROM "posts_post"
        WHERE "posts_post"."id" = 1
        (filter/get = WHERE ... , exclude = WHERE NOT ...)
    - Field lookups (field__lookup=value), double underscore:
        id__gt=1                  -> id > 1        (gte, lt, lte also)
        post_title__contains="1"  -> LIKE '%1%'    (icontains = ignore case)
        post_title__startswith="t"
        id__in=[1, 3]             -> id IN (1, 3)
    - Summary:
        +-----------+--------------------+----------------------------------+
        | method    | returns            | no match / many matches          |
        +-----------+--------------------+----------------------------------+
        | all()     | QuerySet (all)     | empty QuerySet                   |
        | get()     | ONE object         | DoesNotExist / MultipleObjects.. |
        | filter()  | QuerySet (match)   | empty QuerySet, no error         |
        | exclude() | QuerySet (no match)| empty QuerySet, no error         |
        +-----------+--------------------+----------------------------------+
    - Can chain: Post.objects.filter(id__gt=1).exclude(post_title="title 3")

## More QuerySet methods (order_by, reverse, values, count, contains, first, last)

    - What I ran in python manage.py shell (data = Post.objects.all()):
        >>> s1 = Post.objects.get(id=2)
        >>> s1.id
        2
        >>> s1.post_title
        'title 2'
        >>> data.order_by('id')
        <QuerySet [<Post: Post object (1)>, <Post: Post object (2)>, <Post: Post object (3)>]>
        >>> data.order_by('-id')
        <QuerySet [<Post: Post object (3)>, <Post: Post object (2)>, <Post: Post object (1)>]>
        >>> data.order_by('-id').reverse()
        <QuerySet [<Post: Post object (1)>, <Post: Post object (2)>, <Post: Post object (3)>]>
        >>> data.values()
        <QuerySet [{'id': 1, 'post_title': 'title 1', 'post_content': 'content 1',
                    'published_date': datetime.date(2026, 10, 22)}, {...id 2...}, {...id 3...}]>
        >>> Post.objects.all().count()
        3
        >>> data.contains(s1)
        True
        >>> data.first()
        <Post: Post object (1)>
        >>> data.last()
        <Post: Post object (3)>
    - Methods:
        order_by('field')  -> sort ascending (1, 2, 3)          SQL: ORDER BY id ASC
        order_by('-field') -> minus = descending (3, 2, 1)      SQL: ORDER BY id DESC
        reverse()          -> flips the current order ('-id' reversed -> 1, 2, 3)
        values()           -> QuerySet of DICTIONARIES instead of objects
                              (column name -> value), handy to see all data at once
                              values('post_title') -> only that column
        count()            -> number of rows (SQL COUNT, faster than len())
        contains(obj)      -> True/False, is this object in the QuerySet?
        first() / last()   -> first / last object (None if empty, no error)
    - get() vs first():
        get(id=2)  -> must match exactly one, otherwise error
        first()    -> just the first one, None if the QuerySet is empty
    - Errors I made (typos) -> Python suggests the right name:
        Post.objetcts            -> AttributeError: type object 'Post' has no attribute
                                    'objetcts'. Did you mean: 'objects'?
        Post.objects.getA(id=2)  -> AttributeError: 'Manager' object has no attribute
                                    'getA'. Did you mean: 'get'?
        .reverese()              -> AttributeError: 'QuerySet' object has no attribute
                                    'reverese'. Did you mean: 'reverse'?
      -> error message says WHICH object: 'Post' (model), 'Manager' (objects),
         'QuerySet' (result of all/filter/order_by).

## AND / OR operators (combining conditions)

    - (examples run on my 3 posts: title 1, title 2, title 3)
    - AND -> row must match ALL conditions
        1. commas inside filter():
            >>> Post.objects.filter(id=1, post_title="title 1")
            <QuerySet [<Post: Post object (1)>]>
            >>> Post.objects.filter(id=1, post_title="title 2")
            <QuerySet []>                 -> both must be true, none match
        2. & between two QuerySets:
            >>> Post.objects.filter(id=1) & Post.objects.filter(post_title="title 1")
            <QuerySet [<Post: Post object (1)>]>
        3. chaining: Post.objects.filter(id=1).filter(post_title="title 1")
    - OR -> row must match AT LEAST ONE condition
        | between two QuerySets:
            >>> Post.objects.filter(id=1) | Post.objects.filter(id=3)
            <QuerySet [<Post: Post object (1)>, <Post: Post object (3)>]>
    - Q objects -> conditions inside ONE filter():
        from django.db.models import Q
        >>> Post.objects.filter(Q(id=1) | Q(post_title="title 3"))         -> OR
        <QuerySet [<Post: Post object (1)>, <Post: Post object (3)>]>
        >>> Post.objects.filter(Q(id__gt=1) & Q(post_content="content 2"))  -> AND
        <QuerySet [<Post: Post object (2)>]>
        >>> Post.objects.filter(~Q(id=2))                                   -> NOT
        <QuerySet [<Post: Post object (1)>, <Post: Post object (3)>]>
    - SQL behind Q(id=1) | Q(post_title="title 3"):
        ... FROM "posts_post" WHERE ("posts_post"."id" = 1 OR "posts_post"."post_title" = 'title 3')
    - Summary:
        +----------+---------------------------------------+---------+
        | operator | Django                                | SQL     |
        +----------+---------------------------------------+---------+
        | AND      | filter(a=1, b=2)  /  &  /  Q() & Q()  | AND     |
        | OR       | qs1 | qs2  /  Q() | Q()               | OR      |
        | NOT      | ~Q()  /  exclude()                    | NOT     |
        +----------+---------------------------------------+---------+
    - Q is needed for OR inside one filter(); commas can only do AND.

## Slicing a QuerySet (LIMIT / OFFSET)

    - (examples run on my 3 posts, data = Post.objects.all())
    - Works like slicing a Python list [start:stop] (stop not included):
        >>> data[0]
        <Post: Post object (1)>                  -> one object (index)
        >>> data[:2]
        <QuerySet [<Post: Post object (1)>, <Post: Post object (2)>]>   -> first 2
        >>> data[1:3]
        <QuerySet [<Post: Post object (2)>, <Post: Post object (3)>]>   -> skip 1, take 2
        >>> data[1:]
        <QuerySet [<Post: Post object (2)>, <Post: Post object (3)>]>   -> all except first
        >>> data.order_by('-id')[:2]
        <QuerySet [<Post: Post object (3)>, <Post: Post object (2)>]>   -> latest 2 posts
    - SQL behind it (slice -> LIMIT / OFFSET, database does the work):
        data[:2]   -> ... FROM "posts_post" LIMIT 2
        data[1:3]  -> ... FROM "posts_post" LIMIT 2 OFFSET 1
            OFFSET = how many rows to skip, LIMIT = how many rows to take
    - Errors / differences from a list:
        data[-1]   -> ValueError: Negative indexing is not supported.
                      use data.last() or data.order_by('-id')[0] instead
        data[50]   -> IndexError: list index out of range   (single index, no row)
        data[5:]   -> <QuerySet []>                          (slice, no error)
        data[:2].filter(id=1)
                   -> TypeError: Cannot filter a query once a slice has been taken.
                      -> filter / order_by FIRST, slice LAST
    - Uses: "latest 3 posts" on the home page, pagination (page 2 = [10:20]).

## Field lookups (field__lookup=value)

    - Syntax: Post.objects.filter(fieldname__lookup=value)   -> DOUBLE underscore
      works in filter(), exclude(), get().
      filter(id=1) is short for filter(id__exact=1).
    - (examples run on my 3 posts: title 1/content 1, title 2/content 2, title 3/content 3)
        +-------------------------------------+------------+--------------------------------+
        | lookup                              | result ids | SQL (WHERE ...)                |
        +-------------------------------------+------------+--------------------------------+
        | text                                |            |                                |
        | post_title__exact="title 1"         | [1]        | post_title = 'title 1'         |
        | post_title__iexact="TITLE 1"        | [1]        | LIKE 'TITLE 1'  (ignore case)  |
        | post_title__contains="2"            | [2]        | LIKE '%2%'                     |
        | post_title__icontains="TITLE"       | [1, 2, 3]  | LIKE '%TITLE%'  (ignore case)  |
        | post_title__startswith="title"      | [1, 2, 3]  | LIKE 'title%'                  |
        | post_content__endswith="3"          | [3]        | LIKE '%3'                      |
        | numbers                             |            |                                |
        | id__gt=1                            | [2, 3]     | id > 1                         |
        | id__gte=2                           | [2, 3]     | id >= 2                        |
        | id__lt=3                            | [1, 2]     | id < 3                         |
        | id__lte=1                           | [1]        | id <= 1                        |
        | id__in=[1, 3]                       | [1, 3]     | id IN (1, 3)                   |
        | id__range=(2, 3)                    | [2, 3]     | id BETWEEN 2 AND 3  (both incl)|
        | dates                               |            |                                |
        | published_date__year=2026           | [1, 2, 3]  | BETWEEN 2026-01-01 AND 12-31   |
        | published_date__month=10            | [1, 2, 3]  | month of date = 10             |
        | published_date__day=22              | [1, 2, 3]  | day of date = 22               |
        | empty values                        |            |                                |
        | post_title__isnull=False            | [1, 2, 3]  | post_title IS NOT NULL         |
        +-------------------------------------+------------+--------------------------------+
    - "i" in front (iexact, icontains, istartswith, iendswith) -> ignore upper/lower case.
      Note: on SQLite, LIKE already ignores case for English letters, so contains and
      icontains behave the same here; on PostgreSQL contains IS case-sensitive.
    - % in LIKE = "any characters": '%2%' anywhere, 'title%' at start, '%3' at end.
    - Combine: Post.objects.filter(id__gte=2, post_title__icontains="title")  -> AND
               Post.objects.filter(Q(id__lt=2) | Q(post_content__endswith="3")) -> OR
    - Wrong lookup name -> error, e.g. filter(id__bigger=1) ->
        FieldError: Unsupported lookup 'bigger' for BigAutoField or join on the field not permitted.

## QuerySets are lazy (proved with connection.queries)

    - Lazy = building a QuerySet does NOT touch the database; SQL runs only when the
      data is actually needed (evaluated).
    - Test (DEBUG = True, counting queries with connection.queries):
        >>> from django.db import connection, reset_queries
        >>> reset_queries()                                 -> start count at 0
        >>> data = Post.objects.all()                       -> queries: 0
        >>> f = data.filter(id__gt=1).order_by('-id')       -> queries: 0  (still nothing!)
        >>> list(f)                                         -> queries: 1  (SQL runs NOW)
        [<Post: Post object (3)>, <Post: Post object (2)>]
            SQL: ... FROM "posts_post" WHERE "posts_post"."id" > 1
                 ORDER BY "posts_post"."id" DESC
            -> all + filter + order_by became ONE query
        >>> list(f)                                         -> queries: 1  (cached, no new SQL)
        >>> data[0]; data[0]                                -> queries: 3  (+2, not cached)
        >>> data.count()                                    -> queries: 4  (+1, SELECT COUNT)
        >>> for p in data: pass                             -> queries: 5  (+1, loads all rows)
        >>> for p in data: pass                             -> queries: 5  (cached)
    - What evaluates a QuerySet (runs SQL):
        list(qs), for loop, printing/repr in shell, len(qs), bool / if qs:,
        qs[0] (single index), count(), first(), last(), get(), exists()
    - What does NOT run SQL:
        all(), filter(), exclude(), order_by(), slicing qs[:2]  -> they just build the query
    - Cache:
        once a QuerySet is fully evaluated (list, for loop), results are stored in it
        -> using the SAME QuerySet again = no new query.
        qs[0] / count() on a not-yet-evaluated QuerySet -> new query every time.
    - Why it matters:
        can build a query step by step (filter, then order, then slice) -> one SQL at the end.
        in templates, {% for post in posts %} is where the query actually runs.

## Updating rows (single row and multiple rows)

    - (examples run on my 3 posts inside a test transaction that was rolled back,
       so the real data was NOT changed)
    - Single row -> get the object, change attribute, save()
        >>> p = Post.objects.get(id=1)
        >>> p.post_title = "new title 1"
        >>> p.save()
        SQL: UPDATE "posts_post" SET "post_title" = 'new title 1',
                                     "post_content" = 'content 1',
                                     "published_date" = '2026-10-22'
             WHERE "posts_post"."id" = 1
        -> object already has an id -> save() does UPDATE (no id -> INSERT, see save() notes)
        -> writes ALL columns, even the ones that did not change
        -> auto_now=True sets published_date to today on every save()
    - Single row, only some columns -> save(update_fields=[...])
        >>> p.post_content = "new content 1"
        >>> p.save(update_fields=['post_content'])
        SQL: UPDATE "posts_post" SET "post_content" = 'new content 1' WHERE "posts_post"."id" = 1
        -> only the listed column is written (published_date NOT updated here)
    - Multiple rows -> filter(...).update(...)   (one SQL, no objects loaded)
        >>> Post.objects.filter(id__gt=1).update(post_content="updated")
        2                                         -> returns number of rows changed
        SQL: UPDATE "posts_post" SET "post_content" = 'updated' WHERE "posts_post"."id" > 1
        >>> Post.objects.filter(id=2).update(post_title="title two")
        1                                         -> update() also works for one row
        >>> Post.objects.filter(id=99).update(post_title="x")
        0                                         -> no match = 0, no error
        Post.objects.all().update(...)            -> changes EVERY row (careful!)
    - Result before rollback:
        (1, 'new title 1', 'new content 1')
        (2, 'title two',   'updated')
        (3, 'title 3',     'updated')
    - save() vs update():
        +----------------------------+----------------------------------------------+
        | obj.save()                 | qs.update(field=value)                       |
        +----------------------------+----------------------------------------------+
        | one object                 | many rows at once (whatever filter matched)  |
        | 2 queries (get + UPDATE)   | 1 query (UPDATE ... WHERE)                   |
        | writes all columns         | writes only the given columns                |
        | auto_now fields updated    | auto_now fields NOT updated                  |
        | returns None               | returns number of rows changed               |
        +----------------------------+----------------------------------------------+
    - update() is on a QuerySet, not on one object:
        Post.objects.get(id=1).update(...)
            -> AttributeError: 'Post' object has no attribute 'update'  (get returns an object)
        use Post.objects.filter(id=1).update(...) instead.

## Deleting rows (single row and multiple rows)

    - (examples run on my 3 posts inside a test transaction that was rolled back,
       so the real data was NOT deleted)
    - Single row -> get the object, then delete()
        >>> p = Post.objects.get(id=1)
        >>> p.delete()
        (1, {'posts.Post': 1})        -> (total rows deleted, {model: rows deleted})
        SQL: DELETE FROM "posts_post" WHERE "posts_post"."id" IN (1)
        >>> p.id
        None                          -> object still exists in Python, but has no id now
        >>> p.post_title
        'title 1'                     -> values still there (p.save() would INSERT it again)
        rows left: [2, 3]
    - Multiple rows -> filter(...).delete()   (one SQL)
        >>> Post.objects.filter(id__gt=1).delete()
        (2, {'posts.Post': 2})
        SQL: DELETE FROM "posts_post" WHERE "posts_post"."id" > 1
        >>> Post.objects.filter(id=99).delete()
        (0, {})                       -> no match = 0, no error
        rows left: []
        Post.objects.all().delete()   -> deletes EVERY row (careful, no undo!)
    - get() + delete() on a missing row:
        Post.objects.get(id=99).delete()
            -> DoesNotExist: Post matching query does not exist.  (error comes from get)
        filter(id=99).delete() -> (0, {}) instead, no error.
    - Deleted ids are NOT reused: after deleting id 3, the next new post gets id 4
      (AUTOINCREMENT).
    - Summary:
        +-------------------------------+---------------------------------------------+
        | obj.delete()                  | qs.delete()                                 |
        +-------------------------------+---------------------------------------------+
        | one object                    | all rows the filter matched                 |
        | object must exist (get first) | 0 matches -> (0, {}), no error              |
        | returns (1, {'posts.Post': 1})| returns (count, {'posts.Post': count})      |
        +-------------------------------+---------------------------------------------+
    - CRUD so far with the ORM:
        Create -> Post(...).save() / Post.objects.create(...)
        Read   -> all(), get(), filter(), exclude(), order_by(), slicing
        Update -> obj.save() / qs.update(...)
        Delete -> obj.delete() / qs.delete()

## Fetching from the database and rendering in a template

    - Before: home() used the hard-coded post_list (list of dicts).
      Now: posts come from the database (posts_post table) with the ORM.
    - blog/posts/views.py:
        from .models import Post        -> . = same app folder (posts/models.py)

        def home(request):
            all_posts = Post.objects.all()
            print(all_posts)
            return render(request, 'posts/index.html', {'posts': all_posts, 'name': 'sachin'})
        print(all_posts) -> shows in the runserver terminal:
            <QuerySet [<Post: Post object (1)>, <Post: Post object (2)>, <Post: Post object (3)>]>
    - blog/posts/templates/posts/includes/postcard.html -> use the MODEL field names:
        {{ post.title }}    -> {{ post.post_title }}
        {{ post.content }}  -> {{ post.post_content }}
        5 Th August 2023    -> {{ post.published_date }}   (was hard-coded)
        {% url 'post_detail' post.id %}  -> unchanged, id comes from the database
    - index.html did not change: {% for post in posts %} works the same for a list of
      dicts and for a QuerySet of objects ({{ post.x }} looks up dict key OR attribute).
    - Flow:
        browser /post/home/ -> urls.py -> home() -> Post.objects.all() (lazy, no SQL yet)
        -> render() -> {% for post in posts %} runs the SQL -> HTML cards -> browser
    - Result (checked by rendering the page):
        titles: title 1, title 2, title 3
        dates:  Oct. 22, 2026   -> Django formats DateField automatically
                                   (can change later with the |date filter)
        links:  /post/1/, /post/2/, /post/3/
    - Note: post_detail() still uses the old post_list, so "Read More" shows the old
      hard-coded posts, not the database ones (next step: Post.objects.get(id=id)).

## Single post page from the database (get + Http404)

    - blog/posts/views.py:
        post_list (hard-coded dicts) removed -> all data now comes from the database.

        def post_detail(request, id):
            try:
                post_dict = Post.objects.get(id=id)
            except:
                raise Http404()
            return render(request, 'posts/post.html', {"post_dict": post_dict})
        get(id=id) -> one Post object; if no row -> DoesNotExist -> caught -> raise Http404()
        (before: for loop over post_list to find the matching dict)
    - blog/posts/templates/posts/post.html -> model field names:
        {{ post_dict.title }}    -> {{ post_dict.post_title }}
        {{ post_dict.content }}  -> {{ post_dict.post_content }}
        25th January 2024        -> {{ post_dict.published_date }}
    - Result (checked by rendering):
        /post/1/  -> title 1, content 1, Oct. 22, 2026   (same for 2 and 3)
        /post/99/ -> Http404 -> custom 404.html (when DEBUG = False)
    - Name: post_dict is now a Post OBJECT, not a dict (works, but post would be clearer).
    - Notes / to improve:
        {% block title %}{{ post_dict.title }}{% endblock %} -> browser tab is EMPTY,
            because the model field is post_title, not title.
            a wrong name in a template gives "" (no error) -> easy to miss.
        bare except: catches EVERY error (even typos) and shows 404.
            better: except Post.DoesNotExist:
        Django shortcut doing the same in one line:
            from django.shortcuts import get_object_or_404
            post = get_object_or_404(Post, id=id)

## get_object_or_404 (shortcut)

    - blog/posts/views.py:
        from django.shortcuts import render, get_object_or_404

        def post_detail(request, id):
            post_dict = get_object_or_404(Post, id=id)
            return render(request, 'posts/post.html', {"post_dict": post_dict})
    - Replaces 4 lines:
        try:
            post_dict = Post.objects.get(id=id)
        except:
            raise Http404()
    - get_object_or_404(Model, lookups) = Model.objects.get(lookups)
        found     -> returns the object
        not found -> raises Http404 for you (only for DoesNotExist, not for other errors)
        -> also fixes the bare except problem.
    - Any lookup works: get_object_or_404(Post, post_title="title 1")
      (more than one match -> MultipleObjectsReturned error, same as get()).
    - Result (checked by rendering): /post/1/, /post/2/, /post/3/ -> correct post;
      /post/99/ -> Http404.
    - from django.http import Http404 is not used in views.py anymore (can be removed).
    - Similar: get_list_or_404(Post, ...) -> filter(); raises 404 if the list is empty.

## Aggregate functions (Count, Sum, Avg, Max, Min)

    - Aggregate = one value calculated from MANY rows (count, total, average, biggest, smallest).
      Returns a DICTIONARY, not a QuerySet.
    - from django.db.models import Count, Sum, Avg, Max, Min
    - (examples run on my 3 posts, ids 1, 2, 3)
        >>> Post.objects.aggregate(Count('id'))
        {'id__count': 3}
            SQL: SELECT COUNT("posts_post"."id") AS "id__count" FROM "posts_post"
        >>> Post.objects.aggregate(Sum('id'))
        {'id__sum': 6}                                  -> 1 + 2 + 3
        >>> Post.objects.aggregate(Avg('id'))
        {'id__avg': 2.0}                                -> 6 / 3
        >>> Post.objects.aggregate(Max('id'), Min('id'))
        {'id__max': 3, 'id__min': 1}                    -> several in one query
        >>> Post.objects.aggregate(Max('post_title'))
        {'post_title__max': 'title 3'}                  -> Max/Min work on text and dates too
    - Key name:
        default -> fieldname__function   ('id__count', 'id__sum', ...)
        own name -> keyword argument:
            >>> Post.objects.aggregate(total=Count('id'), latest=Max('published_date'))
            {'total': 3, 'latest': datetime.date(2026, 10, 22)}
                SQL: SELECT COUNT(...) AS "total", MAX(...) AS "latest" FROM "posts_post"
        get just the number:
            >>> Post.objects.aggregate(Count('id'))['id__count']
            3
    - With filter (filter first, then aggregate):
        >>> Post.objects.filter(id__gt=1).aggregate(Avg('id'))
        {'id__avg': 2.5}                                -> only ids 2 and 3
            SQL: ... WHERE "posts_post"."id" > 1
        >>> Post.objects.filter(id=99).aggregate(Max('id'))
        {'id__max': None}                               -> no rows -> None, no error
    - aggregate() is the LAST step -> result is a dict:
        Post.objects.aggregate(Count('id')).filter(id=1)
            -> AttributeError: 'dict' object has no attribute 'filter'
    - aggregate() runs the SQL immediately (not lazy, like count()).
    - count() vs aggregate(Count()):
        Post.objects.count()               -> 3 (just the number)
        Post.objects.aggregate(Count('id')) -> {'id__count': 3} (dict, can add more functions)

## Helpful resources (Django docs: models, fields, querysets, migrations)

    - Models (how to define models, fields, Meta, methods):
        https://docs.djangoproject.com/en/6.0/topics/db/models/
    - Model field reference (CharField, TextField, DateField, options like max_length,
      auto_now, null, blank...):
        https://docs.djangoproject.com/en/6.0/ref/models/fields/
    - QuerySet API reference (all, get, filter, exclude, order_by, update, delete,
      aggregate, field lookups...):
        https://docs.djangoproject.com/en/6.0/ref/models/querysets/
    - Migrations (makemigrations, migrate, showmigrations, sqlmigrate):
        https://docs.djangoproject.com/en/6.0/topics/migrations/
    - Admin site (ModelAdmin options: list_display, list_filter, search_fields...;
      site_header, site_title, index_title):
        https://docs.djangoproject.com/en/6.0/ref/contrib/admin/

## Django admin (createsuperuser, register a model, __str__)

    - Admin = ready-made website to add / edit / delete rows: http://127.0.0.1:8000/admin/
      (path('admin/', admin.site.urls) is already in blog/blog/urls.py)
    - python manage.py createsuperuser
        -> asks username, email, password -> creates an admin user (mine: admin)
        -> stored in the auth_user table (created by the first migrate)
    - blog/posts/admin.py -> register the model so it shows in the admin:
        from django.contrib import admin
        from .models import Post

        admin.site.register(Post)
      -> admin home now has a POSTS section with "Posts" (+ Add)
         list page: /admin/posts/post/  -> "3 posts"
    - Problem: list showed Post object (3), Post object (2), Post object (1)
        -> default text for an object = "ModelName object (id)"
    - Fix: __str__ method in the model = text used when the object is shown/printed
        blog/posts/models.py:
            class Post(models.Model):
                post_title = models.CharField(max_length=60)
                post_content = models.TextField()
                published_date = models.DateField(auto_now=True)

                def __str__(self):
                    return self.post_title
      -> admin list: title 3, title 2, title 1
      -> shell too: Post.objects.all() -> <QuerySet [<Post: title 1>, <Post: title 2>, <Post: title 3>]>
    - Mistake I made: def __str__ NOT indented -> it was a separate function outside the
      class, Django never used it, admin still showed "Post object (1)".
      Indentation decides what belongs to the class -> 4 spaces inside class Post.
    - __str__ does not change the table -> no migration needed
      (makemigrations -> "No changes detected").
    - Naming in the admin ("Posts", "3 posts", "Add post"):
        Django builds the names from the class name Post automatically:
            verbose_name        = "post"    -> class name in lower case (one row)
            verbose_name_plural = "posts"   -> verbose_name + "s"        (many rows)
        -> sidebar "Posts", list page "Select post to change", bottom "3 posts",
           button "ADD POST", app section "POSTS" (app name posts).
        Django just adds "s", it does not know English plurals:
            class Category -> "Categorys"  (wrong)
        Fix with class Meta inside the model:
            class Category(models.Model):
                ...
                class Meta:
                    verbose_name_plural = "Categories"
        Convention: model class name is SINGULAR (Post, not Posts) -> one object = one post.

## Admin panel: add, update, delete a post

    - All done from http://127.0.0.1:8000/admin/posts/post/ (no code, no shell).
    - What I did (from the admin history, LogEntry table):
        Addition -> "title 4"                      -> Added.
        Change   -> "title 4 - using admin panel"  -> Changed Post title.
        Deletion -> "title 4 - using admin panel"
      Posts in the database afterwards: title 1, title 2, title 3 (id 4 is gone).
    - Add    -> "ADD POST +" button -> form with Post title + Post content -> SAVE
                published_date not in the form (auto_now=True -> not editable, filled automatically)
                = Post.objects.create(...)   -> SQL INSERT
    - Update -> click a post in the list -> change fields -> SAVE
                = obj.post_title = "..."; obj.save()  -> SQL UPDATE
    - Delete -> open post -> DELETE button -> "Are you sure?" page -> "Yes, I'm sure"
                or tick posts in the list -> Action: "Delete selected posts" -> Run
                = obj.delete() / qs.delete()  -> SQL DELETE
    - Form labels come from field names: post_title -> "Post title", post_content -> "Post content".
      CharField -> one-line input, TextField -> big text box.
    - Every admin action is saved in the django_admin_log table
      -> "Recent actions" box on the admin home page, and "HISTORY" button on each post.
    - Deleted id 4 is not reused -> next new post gets id 5 (AUTOINCREMENT).

## Customising the admin list (ModelAdmin, list_display)

    - blog/posts/admin.py:
        from django.contrib import admin
        from .models import Post

        @admin.register(Post)
        class PostAdmin(admin.ModelAdmin):
            list_display = ('id', 'post_title', 'published_date')
            list_display_links = ('id', 'post_title')

        # admin.site.register(Post, PostAdmin)
    - ModelAdmin = class with settings for how ONE model looks/behaves in the admin.
      Name convention: ModelName + Admin -> PostAdmin.
    - Two ways to register (do only ONE, both together -> AlreadyRegistered error):
        @admin.register(Post)                     -> decorator above the class
        admin.site.register(Post, PostAdmin)      -> function call after the class
      (before: admin.site.register(Post) -> default admin, no customising)
    - list_display -> columns in the list page (instead of only the __str__ text):
        ID | POST TITLE | PUBLISHED DATE
        column headers come from the field names (post_title -> "Post title").
    - list_display_links -> which columns are clickable links to the edit page
        default: only the first column; here id AND post_title.
    - It is a tuple ( ... ) -> one item needs a comma: ('post_title',)
    - python manage.py check -> "System check identified no issues" (checks admin settings too,
      e.g. a wrong field name in list_display gives an error here).
    - More options for later: ordering, list_per_page.
    - list_filter and search_fields (added next):
            list_filter = ('published_date',)
            search_fields = ('post_title',)
        list_filter -> "FILTER" sidebar on the right of the list page.
            for a date field: Any date / Today / Past 7 days / This month / This year
            -> click one -> URL gets ?published_date__gte=...  (field lookups again)
        search_fields -> search box above the list.
            searches post_title with icontains (ignore case, anywhere in the text)
            -> SQL: WHERE post_title LIKE '%word%'
            more fields: ('post_title', 'post_content') -> matches in title OR content
        Both are tuples -> trailing comma for one item: ('published_date',)
        Without the comma ('published_date') is just a string -> manage.py check error
        (admin.E112: The value of 'list_filter' must be a list or tuple.)

## Admin site names (site_header, site_title, index_title)

    - blog/blog/urls.py (after urlpatterns):
        admin.site.site_header = "My Blog"
        admin.site.site_title = "Admin Portal"
        admin.site.index_title = "Welcome to My Blog Portal"
      (default for all 3: "Django administration" / "Django site admin" / "Site administration")
    - Where each one shows (checked by rendering the admin pages):
        +--------------+-------------------------------------+-------------------------------------+
        | setting      | where                               | result                              |
        +--------------+-------------------------------------+-------------------------------------+
        | site_header  | big text top-left, EVERY admin page | My Blog                             |
        | site_title   | browser TAB title, after the "|"    | ... | Admin Portal                  |
        | index_title  | heading on the admin HOME page only | Welcome to My Blog Portal           |
        +--------------+-------------------------------------+-------------------------------------+
        /admin/            -> tab: "Welcome to My Blog Portal | Admin Portal"
        /admin/posts/post/ -> tab: "Select post to change | Admin Portal"
    - My confusion: set site_title = "Admin Portal" and expected it on the page;
      it only shows in the browser tab -> index_title is the heading on the home page.
    - admin.site = the default admin site object; admin.py files use it too
      (admin.site.register). Setting it in urls.py works because urls.py is loaded at startup;
      could also go in posts/admin.py.

## Django forms: what {{ form }} renders vs what I write myself

    - Template with a Django form:
        <form method="POST">                     <- 1. form tag      -> I write it
            {% csrf_token %}                     <- 2. CSRF token    -> I write it (POST only)
            {{ form }}                           <- 3. fields        -> Django renders it
            <button type="submit">Save</button>  <- 4. submit button -> I write it
        </form>
    - Django renders with {{ form }}:
        <label> for each field
        the right input for each field type (input / textarea / select)
        name, id, required, maxlength attributes
        error messages after a wrong submit + keeps the values already typed
    - I write myself, and why:
        <form method="POST" action="..."> -> Django does not know which URL to send to
                                             or GET vs POST
        {% csrf_token %} -> hidden security token; every POST without it -> 403 Forbidden
                            (comment form in post.html does not have it yet)
        submit button    -> only I know the text (Save / Comment / Login), and one page
                            can have several forms
    - In short: Django builds the fields; form tag, csrf_token and button wrap around them.

## GET vs POST (HTTP methods)

    - Every browser request has a METHOD; the two used with forms are GET and POST.
    - GET -> "give me something" (read)
        typing a URL, clicking a link, <form method="GET">
        form data goes IN THE URL as a query string:
            /post/search/?q=django&page=2
        visible in the address bar, browser history, server logs; can be bookmarked/shared
        length limited (URL), never for passwords or private data
        should NOT change data on the server (safe to repeat / refresh)
        use for: search boxes, filters, pagination (admin list_filter uses GET: ?published_date__gte=...)
    - POST -> "here is data, do something with it" (create / change)
        <form method="POST">
        form data goes in the REQUEST BODY, not in the URL
        not bookmarked; refresh -> browser asks "resend form data?"
        use for: login, sign up, create/edit/delete a post, comments
        Django needs {% csrf_token %} in every POST form (else 403 Forbidden)
    - <form> without method -> GET by default.
    - In a Django view:
        request.method      -> "GET" or "POST"
        request.GET         -> dict-like of URL query values:   request.GET.get('q')
        request.POST        -> dict-like of form body values:    request.POST.get('post_title')
    - Usual pattern for a form view (one URL, two methods):
        def create_post(request):
            if request.method == "POST":       # form was submitted
                ... read request.POST, validate, save ...
                return redirect(...)           # redirect after POST -> refresh won't resubmit
            else:                              # GET: first visit
                ... show empty form ...
            return render(request, 'posts/create.html', {...})
    - Summary:
        +----------------+------------------------------+------------------------------+
        |                | GET                          | POST                         |
        +----------------+------------------------------+------------------------------+
        | purpose        | read / fetch                 | create / change data         |
        | data           | in URL ?key=value            | in request body              |
        | visible        | yes (address bar, history)   | no (not in URL)              |
        | bookmark       | yes                          | no                           |
        | refresh        | safe                         | "resend form data?"          |
        | csrf_token     | not needed                   | required in Django           |
        | in the view    | request.GET                  | request.POST                 |
        +----------------+------------------------------+------------------------------+
    - POST is NOT encryption: data is still readable in transit without HTTPS.

## CSRF attack and {% csrf_token %}

    - CSRF = Cross-Site Request Forgery: another website makes YOUR browser send a request
      to a site where you are logged in, without you knowing.
    - Attack WITHOUT token (course slide):

        +------+      logged in       +-------------+
        | user | -------------------> | FRIENDS.COM |   (has a delete-account form)
        +------+                      +-------------+
           |
           | visits
           v
        +----------+   hidden form    +----------------------------------------+
        | EVIL.COM | ---------------> | POST https://friends.com/delete-account |
        +----------+  (auto-submits)  +----------------------------------------+
                                                         |
                                                         v
                                              +---------------------+
                                              | DELETED THE ACCOUNT |
                                              +---------------------+
        why it works: the browser sends friends.com's login cookie automatically with
        every request to friends.com -> the server thinks it is the real user.

    - Attack WITH token (course slide):

        +------+                      +----------------------------+
        | user | -------------------> | FRIENDS.COM                |
        +------+                      | delete form WITH TOKEN     |
           |                          +----------------------------+
           v
        +----------+    NO TOKEN      +----------------------------------------+
        | EVIL.COM | ---------------> | POST https://friends.com/delete-account |
        +----------+                  +----------------------------------------+
             ^                                           |
             |                  FAILED                   |
             +-------------------------------------------+
        why it fails: the token is a secret random value placed inside friends.com's own
        form; evil.com cannot read friends.com's pages, so it cannot know the token.

    - In Django:
        <form method="POST">
            {% csrf_token %}
            ...
        </form>
        {% csrf_token %} -> renders a hidden input:
            <input type="hidden" name="csrfmiddlewaretoken" value="...random...">
        CsrfViewMiddleware (on by default in settings.py MIDDLEWARE) checks every POST:
            token missing / wrong -> 403 Forbidden "CSRF verification failed"
            token correct         -> request goes to the view
    - Only POST (and PUT/PATCH/DELETE) are checked; GET is not -> another reason
      GET must never change data.
    - Admin forms already include it; my own POST forms (comment form in post.html) need it.

## Form fields (django.forms)

    - A form is a Python class (usually in posts/forms.py), like a model but for HTML input:
        from django import forms

        class PostForm(forms.Form):
            post_title = forms.CharField(max_length=60)
            post_content = forms.CharField(widget=forms.Textarea)
            email = forms.EmailField(required=False)
            views = forms.IntegerField(min_value=0)
            published = forms.BooleanField(required=False)
            published_date = forms.DateField()
            category = forms.ChoiceField(choices=[('tech', 'Technology'), ('food', 'Food')])
    - Each field -> HTML input (checked by rendering this form):
        CharField(max_length=60)    -> <input type="text" name="post_title" maxlength="60" required id="id_post_title">
        CharField(widget=Textarea)  -> <textarea name="post_content" cols="40" rows="10" required ...>
        EmailField(required=False)  -> <input type="email" name="email" maxlength="320" ...>   (no required)
        IntegerField(min_value=0)   -> <input type="number" name="views" min="0" required ...>
        BooleanField(required=False)-> <input type="checkbox" name="published" ...>
        DateField()                 -> <input type="text" name="published_date" required ...>
        ChoiceField(choices=[...])  -> <select name="category"><option value="tech">Technology</option>...
      name  = field name (key in request.POST)
      id    = "id_" + field name (label for="id_..." points to it)
      choices: (value saved, text shown)
    - Common options:
        required=True (default) -> adds required; False -> field may be empty
        max_length / min_length, min_value / max_value
        label="Title"          -> own label text (default: from field name, "Post title")
        initial="..."          -> pre-filled value
        help_text="..."        -> small hint under the field
        widget=forms.Textarea / forms.PasswordInput / forms.DateInput(attrs={'type': 'date'})
            widget = HOW the field looks in HTML; field = WHAT data it accepts
    - Validation -> form = PostForm(request.POST); form.is_valid()
        valid data -> True, form.cleaned_data = values converted to Python types:
            {'post_title': 'Hi', 'post_content': 'Body', 'email': '', 'views': 5,
             'published': False, 'published_date': datetime.date(2026, 10, 23), 'category': 'tech'}
            ('5' string -> 5 int, '2026-10-23' -> date, unticked checkbox -> False)
        bad data -> False, form.errors:
            post_title     -> Ensure this value has at most 60 characters (it has 70).
            post_content   -> This field is required.
            email          -> Enter a valid email address.
            views          -> Ensure this value is greater than or equal to 0.
            published_date -> Enter a valid date.
            category       -> Select a valid choice. zzz is not one of the available choices.
        {{ form }} shows these errors next to the fields automatically.
    - Model field vs form field:
        models.CharField -> database column      forms.CharField -> HTML input + validation
        models.TextField -> forms.CharField(widget=forms.Textarea)  (no forms.TextField)

## Form field options: required, label, label_suffix, help_text, error_messages

    - (all examples checked by rendering a test form)
        class DemoForm(forms.Form):
            post_title = forms.CharField(max_length=10)
            post_content = forms.CharField(label="Your text", required=False)
            author_name = forms.CharField(label_suffix=" ->")
            email = forms.EmailField(help_text="We never share your email.")
            age = forms.IntegerField(
                min_value=18,
                error_messages={'required': 'Please enter your age.',
                                'min_value': 'You must be at least 18.',
                                'invalid': 'Age must be a number.'})
    - required (default True)
        True  -> HTML gets required + empty submit -> "This field is required."
        False -> field may be empty (post_content had no error on empty submit)
    - label -> text of the <label>
        default: from the variable name -> "_" becomes space, first letter capital
            post_title  -> <label for="id_post_title">Post title:</label>
            author_name -> Author name
            email       -> Email
        own text: label="Your text" -> <label for="id_post_content">Your text:</label>
    - label_suffix -> text after the label, default ":"
        per field: label_suffix=" ->"  -> <label ...>Author name -&gt;</label>   (-&gt; = ">")
        whole form: DemoForm(label_suffix="") -> <label ...>Post title</label>  (no colon)
    - help_text -> small hint shown under the field
        email -> <span class="helptext" id="id_email_helptext">We never share your email.</span>
                 input gets aria-describedby="id_email_helptext" (screen readers read it)
    - error_messages -> replace Django's default messages, dict {error code: text}
        empty submit:   age -> "Please enter your age."      (default: This field is required.)
        age = "10":     age -> "You must be at least 18."    (min_value)
        age = "abc":    age -> "Age must be a number."       (invalid)
        fields without error_messages keep the default text:
            post_title "x"*12 -> Ensure this value has at most 10 characters (it has 12).
        common codes: required, invalid, max_length, min_length, max_value, min_value
