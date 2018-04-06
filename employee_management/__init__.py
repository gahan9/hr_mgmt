import os
if os.sys.platform == 'linux':
    host_name = os.popen('hostname -I').read().strip()
    if host_name.startswith('192.'):
        from .local_settings import *
    else:
        from .server_settings import *
else:
    from .local_settings import *
