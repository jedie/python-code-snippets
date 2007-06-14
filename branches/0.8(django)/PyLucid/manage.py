#!/usr/bin/env python
from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    err_msg = ("Error:\n"
                "   Can't find the file 'settings.py' in the directory containing %r.\n\n"
                "   It appears you've customized some things.\n"
                "   You'll have to run django-admin.py, passing it your settings module.\n"
                "   (If the file settings.py does indeed exist,\n"
                "   it's causing an ImportError somehow.)\n\n"
                "   (If you've an settings-example.py in the directory\n"
                "   containing %r, rename it to 'settings.py')\n\n"
                    % (__file__, __file__))
    sys.stderr.write(err_msg)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
