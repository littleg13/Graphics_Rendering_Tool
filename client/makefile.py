import os
import subprocess
import sys

# Only change the following four lines
makefile = 'project1/Makefile'
exec = 'project1/main'
arguments = 'Project1_SampleData.txt'

client_file = '~/dev/Graphics_Rendering_Tool/client/graphics_client.py'


subprocess.call(' '.join(('python3', client_file, sys.argv[1], os.getcwd(), makefile, exec, arguments)), shell=True)