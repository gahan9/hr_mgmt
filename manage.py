#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    try:
        if os.sys.platform == "win32":
            import socket
            host_name = socket.gethostbyname(socket.gethostname())
        else:
            host_name = os.popen('hostname -I').read().strip()
            print("Host: {}".format(host_name))
    except Exception as e:
        print("Couldn't get host name due to : {}".format(e))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "employee_management.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
