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
