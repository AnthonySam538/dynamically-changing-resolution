import os
from shutil import rmtree
import subprocess
from math import sin, cos, ceil, pi
import tkinter as tk
from tkinter import filedialog

# Recreate stuff
try:
    os.remove("resized frames.txt")
except FileNotFoundError:
    pass
try:
    rmtree("Frames")
except FileNotFoundError:
    pass
os.mkdir("Frames")
try:
    rmtree("Resized_PNGs")
except FileNotFoundError:
    pass
os.mkdir("Resized_PNGs")
try:
    rmtree("Resized_WebMs")
except FileNotFoundError:
    pass
os.mkdir("Resized_WebMs")

# Define stuff
root = tk.Tk()
root.withdraw()
input_file = filedialog.askopenfilename()
resolution = os.popen("ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 \"" + input_file + "\"").read()[:-1]
video_width = int(resolution[:resolution.find("x")])
video_height = int(resolution[resolution.find("x")+1:])
scaling_factor = 1/10 * 2

# Split the video into PNGs frame-by-frame
subprocess.Popen("ffmpeg -i \"" + input_file + "\" -r 30 " + os.path.join("Frames", "Frame#%04d.png")).wait()

# Resize the PNGs and convert them to WebMs
for iteration, file in enumerate(os.listdir("Frames")):
    frame_width = ceil(video_width * abs(cos(pi/4 + scaling_factor*iteration)))
    frame_height = ceil(video_height * abs(sin(pi/4 + scaling_factor*iteration)))
    subprocess.Popen("ffmpeg -i " + os.path.join("Frames", file) + " -vf scale=" + str(frame_width) + ":" + str(frame_height) + " " + os.path.join("Resized_PNGs", file)).wait()  #  + " & timeout 15")
    subprocess.Popen("ffmpeg -framerate 30 -f image2 -i " + os.path.join("Resized_PNGs", file) + " -c:v libvpx-vp9 -pix_fmt yuva420p " + os.path.join("Resized_WebMs", file[:-3]+"webm")).wait()  #  + " & pause")
    # print(str(iteration), end=" ")

# Prepare the WebMs for concatenation
with open("resized frames.txt", "w", encoding="utf-8") as frame_list:
    for file in os.listdir("Resized_WebMs"):
        frame_list.write("file '" + os.path.join("Resized_WebMs", file) + "'\n")

# Concatenate the WebMs into one WebM
subprocess.Popen("ffmpeg -y -f concat -safe 0 -i \"resized frames.txt\" -c copy \"output.webm\"").wait()
