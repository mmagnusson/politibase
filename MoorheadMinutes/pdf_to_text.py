#CHECK THE FOR LOOP -> IT IS DEPENDANT ON THE PATH VARIABLE LENGTH!
#THIS IS A STUPID HACK THAT WORKS FOR NOW, BUT FIX LATER
#looping through directory where pdf downloads are stored
#perform the pdf2txt.py on each

import subprocess
import os
import glob
#os.system("ls -l")

#possibly grab user input for dir location, hardcoded for now
path = "/Users/mike/Desktop/MoorheadMinutes/"
glob_path = path + "*.pdf"
#filenames = os.listdir(filepath)
#filenames = os.system("ls")

# looping_filenames = str(filenames)
#
# for pdf in looping_filenames:
#     bare_name = os.path.splitext(pdf)
#     command_string = "pdf2txt.py -o " + bare_name + ".txt " + filepath + "/" + bare_name +".pdf"
#     os.system(command_string)


for f in glob.glob(glob_path):
    filename = f[36:]
    cmd = 'pdf2txt.py -o %s.txt %s' % (filename.split('.')[0], filename)
    #os.system(cmd)
    run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = run.communicate()


#/Users/mike/Desktop/mhd_city_council_minutes/" + pdf_number ".pdf"


# 12943604232014073923436.pdf test in my /Users/mike/Desktop/mhd_city_council_minutes/ folder


#pdf2txt.py -o minutes.txt mike/Desktop/12943604232014073923436.pdf

#pdf2txt.py -o minutes.txt /Users/mike/Desktop/mhd_city_council_minutes/12943604232014073923436.pdf



###############
