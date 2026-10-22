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

Redirect fixed by giving URLs a name
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

Home page with a template (render)
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

APP_DIRS: True vs False
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

Template namespacing (posts/templates/posts/home.html)
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

Passing variables to a template (context)
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

for tag in a template
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

if tag in a template
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

empty tag and forloop variables
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

Template filters
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

Showing a single post (post.html)
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

Back to Home link and the url tag
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

Project-level templates folder (DIRS)
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

Template inheritance (extends and block)
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

Static files (CSS)
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

Global static file (STATICFILES_DIRS)
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

Removing the global static file
    - Deleted blog/static/style.css (had: body { background-color: aqua; }).
    - Page was still blue -> browser was showing its CACHED copy of the old CSS.
        Fix: Ctrl + F5 (hard refresh), or F12 -> Network -> tick "Disable cache" -> refresh.
    - base.html still had <link rel="stylesheet" href="{% static 'style.css' %}">
        -> every page asked for a missing file -> 404 for /static/style.css in the server log.
        Fix: removed that link line from base.html.
    - Kept {% load static %} and {% block css %}{% endblock css %} in base.html,
      so a page can still add its own CSS later.

Bootstrap templates with base.html
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

include tag (reusable template pieces)
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

Http404 and a custom 404 page
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

Context processors (data for every template)
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

STATICFILES_DIRS emptied (no global static folder)
    - blog/static/ (global style.css) was deleted earlier; settings still pointed to it.
    - blog/blog/settings.py:
        STATICFILES_DIRS = []          (was [BASE_DIR / "static"])
    - why: a folder listed in STATICFILES_DIRS that does not exist -> Django warning
      (staticfiles.W004: The directory ... does not exist).
    - App static files (posts/static/posts/...) still work without it -> found via APP_DIRS-like
      app lookup (AppDirectoriesFinder). STATICFILES_DIRS is only for extra, project-level folders.
    - Add it back when a global static/ folder is created again.

Models (first model: Post)
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

Migrations (makemigrations and migrate)
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

Changing a model (second migration)
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

Django shell: creating objects (save and create)
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

Seeing the SQL Django runs (connection.queries)
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

all() and QuerySet (reading rows)
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

get(), filter(), exclude() (reading specific rows)
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
