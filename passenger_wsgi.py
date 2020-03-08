import sys, os
INTERP = "/home/ntai/wednesday.cleanwinner.com/py3/bin/python"
#INTERP is present twice so that the new python interpreter 
#knows the actual executable path 
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/cworg')  #You must add your project here

sys.path.insert(0,cwd+'/py3/bin')
sys.path.insert(0,cwd+'/py3/lib/python3.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "cworg.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
