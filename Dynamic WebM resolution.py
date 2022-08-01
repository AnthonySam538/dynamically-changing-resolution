import os
from shutil import rmtree
import subprocess
from math import sin, cos, fabs, ceil

# Define stuff
resolution = os.popen("ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 \"Etika Screaming (Template).mp4\"").read()[:-1]
video_width = int(resolution[:resolution.find("x")])
video_height = int(resolution[resolution.find("x")+1:])
scaling_factor = 1/10 * 2

# Delete stuff
try:
    os.remove("resized frames.txt")
except FileNotFoundError:
    pass
try:
    rmtree("Frames")
except FileNotFoundError:
    pass
try:
    rmtree("Resized_PNGs")
except FileNotFoundError:
    pass
try:
    rmtree("Resized_WebMs")
except FileNotFoundError:
    pass


# Recreate stuff
os.mkdir("Frames")
os.mkdir("Resized_PNGs")
os.mkdir("Resized_WebMs")

# Split the video into PNGs frame-by-frame
subprocess.Popen("ffmpeg -i \"Etika Screaming (Template).mp4\" -r 30 " + os.path.join("Frames", "Frame#%04d.png")).wait()

# Resize the PNGs and convert them to WebMs
for iteration, file in enumerate(os.listdir("Frames")):
    frame_width = video_width  # str(ceil(video_width * abs(cos(scaling_factor*iteration))))
    frame_height = str(ceil(video_height * abs(cos(scaling_factor*iteration))))
    subprocess.Popen("ffmpeg -i " + str(os.path.join("Frames", str(file))) + " -vf scale=" + str(frame_width) + ":" + str(frame_height) + " " + str(os.path.join("Resized_PNGs", str(file))), creationflags=0x08000000).wait()  #  + " & timeout 15")
    subprocess.Popen("ffmpeg -framerate 30 -f image2 -i " + str(os.path.join("Resized_PNGs", str(file))) + " -c:v libvpx-vp9 -pix_fmt yuva420p " + str(os.path.join("Resized_WebMs", str(file)[:-3]+"mp4")), creationflags=0x08000000).wait()
    print(str(iteration), end=" ")

# Prepare the WebMs for concatenation
with open("resized frames.txt", "w", encoding="utf-8") as frame_list:
    for file in os.listdir("Resized_WebMs"):
        frame_list.write("file Resized_WebMs\\\\" + str(file) + "\n")

# Concatenate the WebMs into one WebM
subprocess.Popen("ffmpeg -f concat -safe 0 -i \"resized frames.txt\" -c copy \"output.mp4\"").wait()
