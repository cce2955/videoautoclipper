import os
import subprocess
import speech_recognition as sr
from pydub import AudioSegment
def warn_and_clear_directory(directory_name):
    if os.path.exists(directory_name):
        user_input = input(f"The '{directory_name}' directory exists. Its contents will be deleted. Do you want to proceed? (y/n): ").lower()
        if user_input == 'y':
            for file in os.listdir(directory_name):
                os.remove(os.path.join(directory_name, file))
        else:
            print(f"Please backup the contents of '{directory_name}' and then run the script again.")
            exit()

warn_and_clear_directory("sub")
warn_and_clear_directory("output")
# Prompt the user for the video URL and the word to search for
video_url = input("Enter the video URL: ")
search_word = input("Enter the word to search for: ")

# Create a directory for the output if it doesn't exist
if not os.path.exists("sub"):
    os.makedirs("sub")

# Step 1: Download the video using yt-dlp
os.system(f"yt-dlp {video_url} -f 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]' -o video.webm")


# Step 2: Convert the downloaded video to .wav audio format using ffmpeg
subprocess.call(['ffmpeg', '-i', 'video.webm', 'audio.wav'])

# Step 3: Split the audio file into chunks
audio = AudioSegment.from_wav("audio.wav")
chunk_length_ms = 1000  # 1 second chunks
chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

# Step 4: Transcribe each chunk and search for the specified word
def transcribe_and_search(audio_chunk, chunk_number):
    # Save the audio chunk to a temporary file
    temp_filename = f'temp_chunk{chunk_number}.wav'
    audio_chunk.export(temp_filename, format="wav")
    
    r = sr.Recognizer()
    with sr.AudioFile(temp_filename) as source:
        audio_data = r.record(source)
        try:
            transcription = r.recognize_google(audio_data)
            if search_word.lower() in transcription.lower():
                # Calculate the start and end times for the video clip
                start_time = chunk_number  # start time in seconds
                end_time = chunk_number + 1  # end time in seconds
                
                                # Extract the video clip using ffmpeg
                output_filename = f'sub/chunk{chunk_number}.mp4'
                subprocess.call([
                    'ffmpeg',
                    '-y',  # Automatically overwrite output file without asking
                    '-i', 'video.webm',
                    '-ss', str(start_time),
                    '-to', str(end_time),
                    '-c:v', 'libx264',  # Copy video stream as is
                    '-c:a', 'aac',   # Convert audio stream to AAC
                    '-strict', 'experimental',  # This might not be necessary if using a newer version of FFmpeg
                    output_filename
                ])

                
                print(f"Word found in chunk {chunk_number}. Video saved to {output_filename}")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except sr.UnknownValueError:
            pass  # No transcription available for this chunk
        
    # Delete the temporary file
    os.remove(temp_filename)

# Transcribe each chunk and search for the specified word
for i, chunk in enumerate(chunks):
    transcribe_and_search(chunk, i)
def merge_clips():
    # Step 1: Prompt the user
    user_input = input("Do you want to merge all clips into a single file? (y/n): ").lower()
    if user_input == 'y':
        # Step 2: Create a text file listing all the video files
        with open('filelist.txt', 'w') as file:
            for i in range(100):  # Assuming there are 100 chunks; adjust as needed
                chunk_file = f'sub/chunk{i}.mp4'
                if os.path.exists(chunk_file):
                    file.write(f"file '{chunk_file}'\n")

        # Step 3: Use FFmpeg to merge the video files
        subprocess.call([
            'ffmpeg',
            '-y',  # Automatically overwrite output file without asking
            '-f', 'concat',
            '-safe', '0',
            '-i', 'filelist.txt',
            '-c', 'copy',
            'output/merged_output.mp4'
        ])
        print("Merging completed. The merged file is saved as merged_output.mp4.")

# Call the function to execute the merging process
merge_clips()

if os.path.exists("Audio.wav"):
    os.remove("Audio.wav")

if os.path.exists("Video.webm"):
    os.remove("Video.webm")