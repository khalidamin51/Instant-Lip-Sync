import cv2
import os
import sys
from os.path import isfile, join

FFMPG_PATH = "res\\ffmpeg\\bin\gffmpeg.exe"
RHUBARB_PATH = "rhubarb.exe"

RHUBARB_EMOTIONS_MAP={
            'A':0,
            'B':1,
            'C':2,
            'D':3,
            'E':4,
            'F':5,
            'G':6,
            'H':7,
            'X':8
            }


def merge_videos(video_parts_path,output_file):
    #delete output video if already exits
    if os.path.exists(output_file):
        os.remove(output_file)
        
    temp_path = os.path.join(video_parts_path,"temp_file.txt")
    print("Video parts path : ",video_parts_path)
    with open(temp_path, "w") as tempfile:
        video_files = ["file '%s'\n"%w for w in os.listdir(video_parts_path) if w.endswith('.avi')]
        tempfile.writelines(video_files)
    temp_path = temp_path.replace("\\","/")
    print("generating to : ",output_file," using temppath : ",temp_path)
    os.system("%s -f concat -i %s -c copy %s"%(FFMPG_PATH,temp_path,output_file))
    os.remove(temp_path)
    
    
def execute_rhubarb(audio,tarteb_fname):
    adjusted_path=audio.replace('.wav','_adjusted.wav')
    if os.path.exists(adjusted_path):
        os.remove(adjusted_path)
    os.system("%s -i %s -ar 32000 %s"%(FFMPG_PATH,audio,adjusted_path))
    os.system("%s -o %s %s"%(RHUBARB_PATH,tarteb_fname,adjusted_path))
  

def add_audio(audio,final,no_aud):
    if os.path.exists(final):
        os.remove(final)
    os.system("%s -loglevel error -nostdin -i %s -i %s -c copy %s"%(FFMPG_PATH,no_aud,audio,final))

def generate_Tarteeb(tarteb_fname):
    tarteb ={}
    with open(tarteb_fname,'r') as tartebfile:
        lines = tartebfile.readlines() 
        for l in lines:
            parts = l.split()
            tarteb[float(parts[0])]=parts[1]
        
    return tarteb


def convert_frames_to_video(pathIn,pathOut,fps,tarteeb):
    frame_array = []
    files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
    
    #for sorting the file names properly
    files.sort(key = lambda x: int(x[5:-4]))
 
    for i in range(len(files)):
        #print(tarteeb2[i])
        filename=pathIn + files[i]
        #reading each files
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        #inserting the frames into an image array
        frame_array.append(img)
 
    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
 
    current_time = 0.00
    frame_change_times = list(tarteeb.keys())
    current_emotion = 0
    video_time = frame_change_times[-1]
    #print("Our video time is ",video_time)
    
    while current_time < video_time:
        #write frame for current time
        emotion_key =tarteeb[frame_change_times[current_emotion]]
        out.write(frame_array[RHUBARB_EMOTIONS_MAP.get(emotion_key,0)])
        
        #increment time
        current_time+=0.01
        if current_time >= frame_change_times[current_emotion+1] and current_emotion<len(frame_change_times)-1:
            current_emotion+=1
            
    out.release()
 



def generate_video(characters_path,input_audio,output_file_path):
    
    pathIn= characters_path
    temp_dir = 'temp'
    no_audio_path = os.path.join(temp_dir,os.path.basename(output_file_path).replace('.avi','_no_audio.avi'))
    pathOut = no_audio_path
    final_vid = output_file_path
    audio_file = input_audio
    tarteb_fname =input_audio.replace('.wav','.seq')
    fps = 100.0

    #executing functions
    execute_rhubarb(audio_file,tarteb_fname)
    tarteeb = generate_Tarteeb(tarteb_fname)
    convert_frames_to_video(pathIn, pathOut, fps,tarteeb)
    add_audio(audio_file,final_vid,pathOut)


if __name__=="__main__":
    generate_video(sys.argv[1],sys.argv[2],sys.argv[3])
    
    if len(sys.argv) >4:
        print("Merging videos in the output folder")
        video_parts_path= os.path.dirname(sys.argv[3])
        output_video_path = sys.argv[3].replace('.avi',"_merged.avi")   
        merge_videos(video_parts_path,output_video_path)
    #generate_video("./character/","10.wav","output/final_vid24.avi")
    
    