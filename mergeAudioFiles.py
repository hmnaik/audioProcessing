import glob
import os

import soundfile as sf

if __name__ == '__main__':
	# Path for the audio files
	# path = "D:\\Barn Stuff\\AudioSamples"
	audio_file_path = "X:\\HemalData\\Software Dev\\audioData"
	dates = ["7th", "8th", "9th", "10th"]
	soundData = []
	sampleRate = 100000
	for day in dates:
		audio_file_path_day = os.path.join(audio_file_path,day)
		compilation_file_day = os.path.join(audio_file_path_day, "compilation_"+day+".wav")
		audio_file_list = glob.glob(os.path.join(audio_file_path_day, "*.wav"))
		print(f"Processing file : {audio_file_list}" )
		for file in audio_file_list:
			data, sampleRate = sf.read(file)
			soundData = soundData + list(data)

		sf.write(compilation_file_day, soundData, sampleRate)