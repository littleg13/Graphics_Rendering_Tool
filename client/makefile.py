import os
import subprocess
import sys

makefile = 'twoTriangles_V1/Makefile'
exec = 'twoTriangles_V1/main'

subprocess.call(' '.join(('python3 ~/dev/Graphics_Rendering_Tool/client/graphics_client.py', sys.argv[1], os.getcwd(), makefile, exec)), shell=True)