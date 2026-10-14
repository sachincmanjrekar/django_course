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
