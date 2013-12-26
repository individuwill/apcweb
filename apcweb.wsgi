import os, sys
os.chdir(os.path.dirname(__file__))
current_path = os.path.split(os.path.realpath(__file__))[0]
sys.path = [current_path] + sys.path

from apcweb import app as application
