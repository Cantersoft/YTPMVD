#TODO
#Clean out old dead code
#Change the linear/grouped track mech to Video only/linked. Video only mode copies video tracks and leaves the audio unaffected in place. Linked mode copies them together. 
#Make y flips start correctly
#fix weird indexerror when another track gets added and then the program gets restarted
#Pitch shifting will not be supported until it is implemented into the Davinci Resolve API

#20261103
data_installation_directory_name = r'%PROGRAMFILES%\Blackmagic Design\YTPMVD'
import os
import sys
data_installation_directory =  os.path.abspath(os.path.expandvars(data_installation_directory_name))
sys.path.insert(0, data_installation_directory)

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import tkinter.filedialog as tf
from tkinter import messagebox
import YTPMVE
#Mido is a requirement to import YTPMVE, so this line will not be reached if mido is not installed.
import mido

resolve_project_manager = resolve.GetProjectManager()
resolve_project = resolve_project_manager.GetCurrentProject()
if resolve_project.GetTimelineCount() == 0:
	messagebox.showerror("No timeline in project", "What are you even trying to do bruh? There is no timeline in this project.")
	YTPMVE.exitScript("No timeline.", 1)
	
resolve_timeline = resolve_project.GetCurrentTimeline()
resolve_timeline_fps = float(resolve_timeline.GetSetting("timelineFrameRate"))
resolve_media_pool = resolve_project.GetMediaPool()



global execution_stop
execution_stop = False

bgcolor = '#d9d9d9'
bgcolor_GO_button = '#009900'
bgcolor_GO_button_pressed = '#006600'
bgcolor_STOP_button = '#990000'
bgcolor_STOP_button_pressed = '#006600'
bgcolor_disabled = '#9e9e9e'
fgcolor_disabled = '#cccccc'

font = ("Comic Sans MS", 10)
font_bold = ("Comic Sans MS", 10, "bold")

global root
root = tk.Tk()
root.iconbitmap(os.path.expandvars(data_installation_directory_name + r'\cantersoft.ico'))
root.protocol('WM_DELETE_WINDOW', root.destroy)
root.resizable(False, False)
root.title("YTPMVD")
root.configure(background=bgcolor)

combo_box_event_track = tk.StringVar()
combo_box_MIDI_channel = tk.StringVar()
spin_box_track_mode = tk.StringVar()
MIDI_filename = tk.StringVar()
checkbox_auto_map_outputs_value = tk.IntVar()
checkbox_flip_y_value = tk.IntVar()
checkbox_flip_x_value = tk.IntVar()
checkbox_legato_video_value = tk.IntVar()
checkbox_legato_audio_value = tk.IntVar()

default_checkbox_flip_y_value = 0
default_checkbox_flip_x_value = 1
default_checkbox_legato_video_value = 1
default_checkbox_legato_audio_value = 0

default_note_duration = 0.1

dict_event_tracks = {}
global dict_midi_channels
dict_midi_channels = {}
array_midi_channel_indexes = []
midi_file_imported = False

#Data for comboboxes
def update_tracks_list():
	global combo_values_event_track_linear
	combo_values_event_track_linear = []
	global combo_values_event_track_grouped
	combo_values_event_track_grouped = []

	track_quantity = resolve_timeline.GetTrackCount("video")
	#Davinci is 1-indexed, so gotta shift stuff
	for track_index in range(1, track_quantity+1):
		combo_values_event_track_linear.append((str(f'Track {track_index}: "{resolve_timeline.GetTrackName("video", track_index)}"')))
		combo_values_event_track_grouped.append((str(f'Track {track_index}: "{resolve_timeline.GetTrackName("video", track_index)}"')))
		#if len(combo_values_event_track_linear) == 0:
			#YTPMVE.exitScript("No tracks selected.", 1)

	global combo_values_event_track
	combo_values_event_track = combo_values_event_track_linear
	#except:
		#combo_values_event_track = ["Track 0", "Track 1", "Track 2", "Track 3", "Track 4", "Track 5", "Track 6", "Track 7", "Track 8", "Track 9", "Track 10", "Track 11", "Track 12", "Track 13", "Track 14", "Track 15"]
		#combo_values_event_track_linear = combo_values_event_track
		#combo_values_event_track_grouped = combo_values_event_track
		
	global combo_values_MIDI_channel
	combo_values_MIDI_channel = []
	global spin_values_track_mode
	spin_values_track_mode = ["linear", "grouped"]

def file_open_dialogue():
	MIDI_filename_read = tf.askopenfilename(initialdir = "\\", title = "Select MIDI file", filetypes = [('MIDI', '*.mid')])
	if MIDI_filename_read:
		print("read")
		MIDI_filename.set(MIDI_filename_read)
		MIDI_file = mido.MidiFile(MIDI_filename.get(), clip=True)
		global midi_file_imported
		midi_file_imported = True
		set_midi_channel_titles(MIDI_file)
		set_dictionary_to_tracks_length()
		button_GO.configure(state=NORMAL, background=bgcolor_GO_button)
	else:
		print("not read")	
		
def set_midi_channel_titles(MIDI_file):
	#dict_midi_channels dictionary is filled with the channel of each track name.
	global dict_midi_channels
	dict_midi_channels = {}
	track_name = "Untitled"
	for msg in MIDI_file:
		if msg.type == "track_name":
			track_name = msg.name
		#This might grab control changes unrelated to tracks? Not sure, may be an issue later and this should be refined.
		#Update 20250125: Only control change 0 is used for bank select, which serves a similar purpose to a program change.
		#Update 20250128: Some horribly malformed MIDIs jump right into notes and never specify which channels are being used, so note_on, and note_off messages also add channels now.
		elif (msg.type == "control_change" and msg.control == 0) or msg.type == "program_change" or msg.type == "note_on" or msg.type == "note_off":
			channel = msg.channel
			if channel not in dict_midi_channels:
				dict_midi_channels[channel] = ('Channel {}: {}'.format(channel, track_name))
				track_name = "Untitled"
				
	dict_midi_channels[-1] = ('Channel {}: {}'.format(-1, "Deselected (None)")) 		
	global array_midi_channel_indexes
	
	array_midi_channel_indexes = sorted(dict_midi_channels.items())
	dict_midi_channels = dict(array_midi_channel_indexes)
	print(dict_midi_channels)
		
	global combo_values_MIDI_channel
	combo_values_MIDI_channel = []
	for channel, track_name in dict_midi_channels.items():
		combo_values_MIDI_channel.append(track_name)
	print(combo_values_MIDI_channel)
	combo_box_MIDI_channel.configure(values=combo_values_MIDI_channel)
	try:
		combo_box_MIDI_channel.set(combo_values_MIDI_channel[0])
		on_combo_box_midi_channel_select("<<ComboboxSelected>>")
	except IndexError:
		YTPMVE.exitScript("Unable to index MIDI channels from the file selected. Please report this issue to the developer.", 1)
	
def set_dictionary_to_tracks_length():
	array_event_track_titles = []

	global dict_event_tracks
	global combo_values_event_track
	
	dict_event_tracks = {}
	for counter, event_track in enumerate(combo_values_event_track):
		array_event_track_titles.append(event_track)
		
		dict_event_tracks[counter] = {}
		dict_event_tracks[counter]['channel'] = array_midi_channel_indexes[0][0] #Set default channel to first possible channel
		dict_event_tracks[counter]['flip_x'] = default_checkbox_flip_x_value  #Set default value for flip_x
		dict_event_tracks[counter]['flip_y'] = default_checkbox_flip_y_value  #Set default value for flip_y
		dict_event_tracks[counter]['legato_video'] = default_checkbox_legato_video_value  #Set default value for legato video	
		dict_event_tracks[counter]['legato_audio'] = default_checkbox_legato_audio_value  #Set default value for legato audio	
		
	combo_values_event_track = array_event_track_titles	
	combo_box_event_track.configure(values=combo_values_event_track)
	on_combo_box_event_track_select("<<ComboboxSelected>>")	
		
#This will always map from the first event track value. It might eventually be worth setting the mapping based on the currently selected event track.		
def auto_map_outputs():
	if midi_file_imported:
		print(combo_values_MIDI_channel)
		MIDI_channel = combo_box_MIDI_channel.current() #combo_box_MIDI_channel.current()#Midi channel should equal dict_chan_to_name{array_chan_to_chan_index[combo_box_MIDI_channel.current()]}
		local_checkbox_flip_x_value = checkbox_flip_x_value.get()
		local_checkbox_flip_y_value = checkbox_flip_y_value.get()
		local_checkbox_legato_video_value = checkbox_legato_video_value.get()
		local_checkbox_legato_audio_value = checkbox_legato_audio_value.get()
		
		max = len(array_midi_channel_indexes)-1 #len(combo_values_MIDI_channel)-1
		
		if MIDI_channel < 0:
			MIDI_channel = 1
		
		for counter, event_track in enumerate(combo_values_event_track):
			#if counter >= len(combo_values_MIDI_channel):
				#break
			current_MIDI_channel = MIDI_channel+counter

			if current_MIDI_channel > max:
				current_MIDI_channel = max
			if current_MIDI_channel < 0:
				current_MIDI_channel = 0
				
			if counter not in dict_event_tracks:
				dict_event_tracks[counter] = {}	
				
			dict_event_tracks[counter]['channel'] = array_midi_channel_indexes[current_MIDI_channel][0] #combo_values_MIDI_channel[current_MIDI_channel]  
			
			dict_event_tracks[counter]['flip_x'] = local_checkbox_flip_x_value
			dict_event_tracks[counter]['flip_y'] = local_checkbox_flip_y_value
			dict_event_tracks[counter]['legato_video'] = local_checkbox_legato_video_value 
			dict_event_tracks[counter]['legato_audio'] = local_checkbox_legato_audio_value 
			
		combo_box_event_track.set(combo_values_event_track[0])
		on_combo_box_event_track_select("<<ComboboxSelected>>")

def STOP():
	execution_stop = True
	
def GO():
	#button_STOP.configure(state=NORMAL, background=bgcolor_STOP_button)
	#button_STOP.update_idletasks() 
	YTPMVE.save_config(dict_event_tracks)
	YTPMVE.save_track_mode(spin_box_track_mode.get())
	Davinci_Resolve_Process()

		
def Davinci_Resolve_Process():
	#Keep track of the 1-based indices of tracks we dynamically create
	YTPMVD_track_indexes = set()
	original_track_quantity = resolve_timeline.GetTrackCount("video")
	track_quantity = resolve_timeline.GetTrackCount("video")
	
	#Clear cache
	for track_index in range(1, original_track_quantity):
		dict_event_tracks[track_index-1]['clips'] = []
		
	#Find the mediapool items associated with all clips in each track, and note where they are in the timeline. Then delete the clips because they will be in the way later	
	for track_index in range(1, original_track_quantity+1):
		#root.after(10, lambda: button_STOP.update_idletasks())
		if execution_stop == True:
			break
		else:	
			if dict_event_tracks[track_index-1]['channel'] == -1:
				#If the track is assigned the channel -1 ("None", deselected basically), ignore and continue
				continue	
			items_in_track = resolve_timeline.GetItemListInTrack("video", track_index)
			if items_in_track:
				for item in items_in_track:
					item_mediapool_item = item.GetMediaPoolItem()
					#Convert non-mediapool items such as internal generators into compound clips so they can be accessed properly
					if item_mediapool_item is None:
						print(f"'{item.GetName()}' has no media pool item. Converting to Compound Clip...")
						new_compound = resolve_timeline.CreateCompoundClip([item], {"name": f"YTPMVD_CONVERT_{item.GetName()}"})
						if new_compound:
							item_mediapool_item = new_compound.GetMediaPoolItem()
							#Switch the item over to the compound clip version, otherwise its start time is registered as None.
							item = new_compound
					
					#So we can switch up clips halfway through the timeline
					item_timeline_start_frame = item.GetStart(True)
					#So that the clip stays trimmed in the same position
					item_source_start_frame = item.GetLeftOffset(True)
					
					#Linked audio collection
					linked_audio_data = []
					linked_items = item.GetLinkedItems()
					for linked_item in linked_items:
						if linked_item.GetMediaPoolItem() is not None:
							linked_audio_data.append({
								"mediaPoolItem": linked_item.GetMediaPoolItem(),
								"sourceStart": linked_item.GetLeftOffset(),
								"duration": linked_item.GetDuration()
							})
					
					dict_event_tracks[track_index-1].setdefault('clips', []).append([
						item_mediapool_item, 
						item_timeline_start_frame, 
						item_source_start_frame, 
						linked_audio_data
					])

					#Delete target clip and linked items to prevent collisions
					clips = [item]
					clips.extend(linked_items)
					resolve_timeline.DeleteClips(clips, False)
	
	print("Cached timeline assets: ", dict_event_tracks)		
	note_channels, note_tones, note_starts, note_durations = YTPMVE.process_midi(MIDI_filename.get())

	
	print(note_channels, note_tones, note_starts, note_durations)
	
	flip_x_boolean = False
	flip_y_boolean = False
	
	#Default values for flips. Flips are assigned to and separated by channels so that a new note in one channel doesn't trigger a flip in another.
	flip_clip = []
	flip_sequence_counter = []
	for i in range(0, 16):
		flip_clip.append(True)
		flip_sequence_counter.append(1)
	
	for iterator, note_channel in enumerate(note_channels):
		if execution_stop == True:
			break
		else:	
			note_tone = note_tones[iterator]
			note_start = note_starts[iterator]
			note_duration = note_durations[iterator]
			
			#If a note had an unknown duration, insert a default value.
			if note_duration == "NULL" or note_duration is None:
				note_duration = default_note_duration
				
			note_end = note_start+note_duration	

			for next_legato_note_start_index, next_legato_note_start in enumerate(note_starts[iterator:]):
				if next_legato_note_start > note_start:
					#Make sure this note is on the same channel
					if note_channels[next_legato_note_start_index] == note_channel:
						legato_note_duration = next_legato_note_start-note_start
						break
				#If this is the final note, no legato
				if next_legato_note_start_index == (len(note_starts[iterator:]) - 1):
					legato_note_duration = None
	
			target_start_frame = (resolve_timeline.GetStartFrame() + round(note_start * resolve_timeline_fps))	
			target_next_start_frame = (resolve_timeline.GetStartFrame() + round(next_legato_note_start * resolve_timeline_fps))	
			
			if legato_note_duration != None:
				legato_duration_frames = target_next_start_frame - target_start_frame #(float(legato_note_duration * resolve_timeline_fps))
			else:
				legato_duration_frames = (float(note_duration * resolve_timeline_fps))		
				
			previous_note_in_channel_start = None
			
			if len(note_starts) > 0:	
				#Subtract one to the iterator so we don't pull the current note as the previous note
				for previous_note_in_channel_start_index in range(iterator-1, 0, -1):
					previous_note_in_channel_start = note_starts[previous_note_in_channel_start_index]
					#Make sure this note is on the same channel
					if note_channels[previous_note_in_channel_start_index] == note_channel:
						break
							
				

			if iterator is not (len(note_starts)):
				if previous_note_in_channel_start is not None:
					#Don't flip on block chords and simultaneous notes		
					#Compares the next note against the chronologically next note (at a higher number of seconds) in the same channel			
					print(note_start, previous_note_in_channel_start)
					if note_start > previous_note_in_channel_start:#or note_end < next_channel_note_end:
						print(f"{note_start} is not {previous_note_in_channel_start}, therefore, clip flipping will switch to {not flip_clip}")
						#print(f"Channel {note_channel}")
						flip_clip[note_channel] = not flip_clip[note_channel]
						flip_sequence_counter[note_channel] += 1
						if flip_sequence_counter[note_channel] > 4:
							flip_sequence_counter[note_channel] = 1
			
			print(f"Current flip sequence counter on {note_channel}: {flip_sequence_counter[note_channel]}")
			print(f"Current flip mode on {note_channel}: {flip_clip[note_channel] }")
			
			for track_index in range(1, original_track_quantity+1):	
				#Find all Resolve tracks where a channel is to dump notes and dump notes.
				if execution_stop == False:	
					track_flip_x = dict_event_tracks[track_index-1]['flip_x']
					track_flip_y = dict_event_tracks[track_index-1]['flip_y']
					
					flip_x_boolean = False
					flip_y_boolean = False
					if (track_flip_x == 1 and track_flip_y == 0):
						print(f"Is clip flipping enabled?")
						if flip_clip[note_channel]:
							print(f"Yes. Setting clip {len(resolve_timeline.GetItemListInTrack('video', track_index))} in track {track_index} to flipped x")
							flip_x_boolean = True				
					elif (track_flip_x == 0 and track_flip_y == 1):
						if flip_clip[note_channel]:
							flip_y_boolean = True		
					elif (track_flip_x == 1 and track_flip_y == 1):
						match flip_sequence_counter[note_channel]:
							case 1:
								pass
							case 2:
								flip_x_boolean = True
							case 3:
								flip_x_boolean = True
								flip_y_boolean = True
							case 4:
								flip_y_boolean = True
								
					print(f"     Earlier, I set clip {len(resolve_timeline.GetItemListInTrack('video', track_index))} in track {track_index} to flipped x (true). Now it is {flip_x_boolean}")

					
					
					#If the track is assigned the channel -1 ("None", deselected basically), ignore and continue
					if dict_event_tracks[track_index-1]['channel'] == -1:
						continue
					elif dict_event_tracks[track_index-1]['channel'] == note_channel:
						target_next_start_frame = (resolve_timeline.GetStartFrame() + float(next_legato_note_start * resolve_timeline_fps))
						#If legato enabled for this track, use legato duration
						if dict_event_tracks[track_index-1]['legato_video'] == 1:
							target_duration_frames = legato_duration_frames
							target_end_frame = target_start_frame + target_duration_frames
						else:	
							target_duration_frames = (float(note_duration * resolve_timeline_fps))
							target_end_frame = target_start_frame + target_duration_frames					
						try:
							original_items_in_track = dict_event_tracks[track_index-1]['clips']
							if original_items_in_track:
								#Find the clip that was in the timeline that is synced with the clip at this position
								matched_item = None
								for cache_item in reversed(original_items_in_track):
									if cache_item[1] <= target_start_frame:
										matched_item = cache_item
										break
										
								if not matched_item:
									matched_item = original_items_in_track[0]
								
								new_clip_mediapool_item = matched_item[0]
								new_clip_source_start_frame = matched_item[2]
								new_clip_linked_audio_bundle = matched_item[3]

								placement_track_index = track_index
								
								#Distribute overlapping duplicates to multiple tracks or avoid collisions as needed
								primary_items = resolve_timeline.GetItemListInTrack("video", track_index)
								has_overlap = False
								if primary_items:
									for timeline_item in primary_items:
										start = timeline_item.GetStart()
										end = start + timeline_item.GetDuration()
										if end > target_start_frame and start < target_end_frame:
											has_overlap = True
											break
								
								if has_overlap:
									placement_track_index = None
									#Try to find space in our previously created YTPMVD tracks
									
									for YTPMVD_track_index in YTPMVD_track_indexes:
										items_in_YTPMVD_track = resolve_timeline.GetItemListInTrack("video", YTPMVD_track_index)
										#Set a temporary placement track
										placement_track_index = YTPMVD_track_index								
										if items_in_YTPMVD_track:
											for YTPMVD_track_item in items_in_YTPMVD_track:
												start = YTPMVD_track_item.GetStart()
												end = start + YTPMVD_track_item.GetDuration()
												if end > target_start_frame and start < target_end_frame:
													placement_track_index = None
											if not placement_track_index is None:
												break
												#Don't bother continuing the search if a suitable track has been found
										else:
											print("no dynamic items in track " + str())
											#If there's nothing in here then I guess it's free space
											placement_track_index = YTPMVD_track_index
											break
									
									#If all created tracks are occupied, generate a fresh track
									if placement_track_index is None:
										new_track = resolve_timeline.AddTrack("video")
										#Refresh total count to get our new 1-based index
										track_quantity = resolve_timeline.GetTrackCount("video")
										resolve_timeline.SetTrackName("video", track_quantity, "YTPMVD_track")
										YTPMVD_track_indexes.add(track_quantity)
										placement_track_index = track_quantity
										

								#Create a new video clip
								if new_clip_mediapool_item:
									#note: endframe is not the ending frame on the timeline, but the end frame of the source clip, in the source video
									clip_info = {
										"mediaPoolItem": new_clip_mediapool_item, 
										"startFrame": int(new_clip_source_start_frame),
										"endFrame": int(new_clip_source_start_frame + target_duration_frames),
										"recordFrame": target_start_frame,
										"trackIndex": placement_track_index,
										"mediaType": 1 #Video only
									}
									if resolve_media_pool.AppendToTimeline([clip_info]):
										print(f"Success! Duplicated video to track {placement_track_index} at frame: {target_start_frame}")
										new_timeline_item = resolve_timeline.GetItemListInTrack("video", placement_track_index)[-1]
										print(f"     Earlier, I set clip {len(resolve_timeline.GetItemListInTrack('video', placement_track_index))} in track {placement_track_index} to flipped x (true). Now I am editing the clip to {flip_x_boolean}")
										#Apply flips if enabled									
										new_timeline_item.SetProperty("FlipX", flip_x_boolean)									
										new_timeline_item.SetProperty("FlipY", flip_y_boolean)
									else:
										print(f"Video append failed at frame {target_start_frame}.")
										
								#Create a new linked audio clip
								if new_clip_linked_audio_bundle:
									for audio_idx, linked_audio in enumerate(new_clip_linked_audio_bundle):
										clip_info_audio = {
											"mediaPoolItem": linked_audio["mediaPoolItem"],
											"startFrame": int(linked_audio["sourceStart"]),
											"endFrame": int(linked_audio["sourceStart"] + target_duration_frames),
											"recordFrame": int(target_start_frame),
											"trackIndex": int(placement_track_index + audio_idx), #Offset safely
											"mediaType": 2 #Audio only
										}
										resolve_media_pool.AppendToTimeline([clip_info_audio])
										print(f"Success! Duplicated matched audio to track {placement_track_index + audio_idx}")
						except KeyError:
							continue
			
	
def on_combo_box_event_track_select(event):
	if midi_file_imported:
		selected_event_track = combo_box_event_track.current()
		if selected_event_track not in dict_event_tracks:
			dict_event_tracks[selected_event_track] = {}
			dict_event_tracks[selected_event_track]['channel'] = 0  #Set default value for combo_box_MIDI_channel
			dict_event_tracks[selected_event_track]['flip_x'] = default_checkbox_flip_x_value  #Set default value for flip_x
			dict_event_tracks[selected_event_track]['flip_y'] = default_checkbox_flip_y_value  #Set default value for flip_y
			dict_event_tracks[selected_event_track]['legato_video'] = default_checkbox_legato_video_value  #Set default value for legato
			dict_event_tracks[selected_event_track]['legato_audio'] = default_checkbox_legato_audio_value  #Set default value for legato
		
		global dict_midi_channels	

		#Try to set the combobox value to the value specified in the event tracks dictionary, but if something invalid is set, then default to a default value
		try:
			#Set the combobox to the key in the midi channels dictionary that matches the value with an index of the event track dictionary's currently selected track's channel key's integer value in an ordered list of the midi channels dictionary
			#dict_midi_channels[list(dict_midi_channels.keys())[int(dict_event_tracks[selected_event_track]['channel'])]]
			combo_box_MIDI_channel.set(dict_midi_channels[int(dict_event_tracks[selected_event_track]['channel'])])
			on_combo_box_midi_channel_select("<<ComboboxSelected>>")
		except:
			combo_box_MIDI_channel.set(combo_values_MIDI_channel[0])
			on_combo_box_midi_channel_select("<<ComboboxSelected>>")
		checkbox_flip_x_value.set(dict_event_tracks[selected_event_track]['flip_x'])
		checkbox_flip_y_value.set(dict_event_tracks[selected_event_track]['flip_y'])
		checkbox_legato_video_value.set(dict_event_tracks[selected_event_track]['legato_video'])
		checkbox_legato_audio_value.set(dict_event_tracks[selected_event_track]['legato_audio'])

def on_combo_box_midi_channel_select(event):
	if midi_file_imported:
		selected_event_track = combo_box_event_track.current()
		if selected_event_track not in dict_event_tracks:
			dict_event_tracks[selected_event_track] = {}
			dict_event_tracks[selected_event_track]['channel'] = 0  #Set default value for combo_box_MIDI_channel
			dict_event_tracks[selected_event_track]['flip_x'] = default_checkbox_flip_x_value  #Set default value for flip_x
			dict_event_tracks[selected_event_track]['flip_y'] = default_checkbox_flip_y_value  #Set default value for flip_y
			dict_event_tracks[selected_event_track]['legato_video'] = default_checkbox_legato_video_value  #Set default value for legato
			dict_event_tracks[selected_event_track]['legato_audio'] = default_checkbox_legato_audio_value  #Set default value for legato

			
		MIDI_channel = array_midi_channel_indexes[combo_box_MIDI_channel.current()][0]
		print("I think that the index of the item you selected (" + str(combo_box_MIDI_channel.current()) + ") says that it is MIDI channel " + str(MIDI_channel))
		dict_event_tracks[selected_event_track]['channel'] = MIDI_channel
	
def checkbox_action(key, value):
	if midi_file_imported:
		print(dict_event_tracks)
		dict_event_tracks[combo_box_event_track.current()][key] = value.get()
	
def spin_box_action():
	global combo_values_event_track
	track_mode_update()
	combo_box_event_track.configure(values=combo_values_event_track)
	combo_box_event_track.set(combo_values_event_track[0])
	
def track_mode_update():
	global combo_values_event_track
	if spin_box_track_mode.get() == spin_values_track_mode[0]:
		combo_values_event_track = combo_values_event_track_linear
		label_event_track.configure(text="Resolve Video Track Only")
	elif spin_box_track_mode.get() == spin_values_track_mode[1]:
		combo_values_event_track = combo_values_event_track_grouped
		label_event_track.configure(text="Video Track & Linked Audio")	
	
class HoverButton(tk.Button):
	def __init__(self, master=None, pressed_color=bgcolor, released_color="SystemButtonFace", **kwargs):
		tk.Button.__init__(self, master, **kwargs)
		self.pressed_color = pressed_color
		self.released_color = released_color
		self.bind("<Enter>", self.on_enter)
		self.bind("<Leave>", self.on_leave)

	def on_enter(self, event):
		if self["state"] == "normal":
			self.config(bg=self.pressed_color)

	def on_leave(self, event):
		if self["state"] == "normal":
			self.config(bg=self.released_color)	
			
update_tracks_list()

frame_file_input = ttk.Frame(root)
frame_file_input.grid(row=0, column=1, columnspan=2, sticky=EW)

frame_master_options = ttk.Frame(root, borderwidth="2", relief="groove")
frame_master_options.grid(row=1, column=1, columnspan=2, sticky=N)

frame_body_container = ttk.Frame(root)
frame_body_container.grid(row=2, column=1, columnspan=2, pady=5, sticky=EW)

frame_body = ttk.Frame(frame_body_container, borderwidth="4", relief="groove")
frame_body.grid(row=1, column=1, columnspan=2, pady=5, sticky=EW)

frame_event_track = ttk.Frame(frame_body, borderwidth="2", relief="groove")
frame_event_track.grid(row=2, column=1, sticky=N)

frame_MIDI_channel = ttk.Frame(frame_body, borderwidth="2", relief="groove")
frame_MIDI_channel.grid(row=2, column=2, sticky=N)

frame_track_mode = ttk.Frame(frame_master_options, borderwidth="2", relief="groove")
frame_track_mode.grid(row=0, column=1, sticky=N)

frame_footer = ttk.Frame(root)
frame_footer.grid(row=3, column=1, columnspan=2, sticky=N, pady=5)

combo_box_event_track = ttk.Combobox(frame_event_track, font=font, textvariable=combo_box_event_track, values=combo_values_event_track)
combo_box_event_track.grid(row=1, pady=5)
combo_box_event_track.bind("<<ComboboxSelected>>", on_combo_box_event_track_select)
combo_box_event_track.set(combo_values_event_track[0])	

combo_box_MIDI_channel = ttk.Combobox(frame_MIDI_channel, font=font, textvariable=combo_box_MIDI_channel, values=combo_values_MIDI_channel)
combo_box_MIDI_channel.grid(row=1, pady=5)
combo_box_MIDI_channel.bind("<<ComboboxSelected>>", on_combo_box_midi_channel_select)

spin_box_track_mode = ttk.Spinbox(frame_track_mode, command=lambda: spin_box_action(), font=font, textvariable=spin_box_track_mode, values=spin_values_track_mode)
spin_box_track_mode.grid(row=1, column=0)

button_auto_map_outputs = HoverButton(frame_body, font=font, text="Auto map outputs", command = auto_map_outputs)
button_auto_map_outputs.grid(row=1, column=1, pady=5, columnspan=2, sticky="N")

button_select_MIDI_file = HoverButton(frame_file_input, font=font, text ="Select MIDI File", command = file_open_dialogue)
button_select_MIDI_file.grid(row=0, column=1, sticky=EW)

button_GO = HoverButton(frame_footer, background=bgcolor_GO_button, pressed_color=bgcolor_GO_button_pressed, released_color=bgcolor_GO_button, font=font_bold, text ="GO!", command = GO)
button_GO.grid(row=5, column=1)
button_GO.configure(state=DISABLED, disabledforeground=fgcolor_disabled, background=bgcolor_disabled)

#button_STOP = HoverButton(frame_footer, background=bgcolor_GO_button, pressed_color=bgcolor_STOP_button_pressed, released_color=bgcolor_STOP_button, font=font_bold, text ="STOP!", command = STOP)
#button_STOP.grid(row=5, column=2)
#button_STOP.configure(state=DISABLED, disabledforeground=fgcolor_disabled, background=bgcolor_disabled)

checkbox_legato_video = tk.Checkbutton(frame_event_track, anchor='w', background=bgcolor, command=lambda: checkbox_action("legato_video", checkbox_legato_video_value), font=font, text="Legato (Video)", variable=checkbox_legato_video_value)
checkbox_legato_video.grid(row=4, sticky = EW)

checkbox_legato_audio = tk.Checkbutton(frame_event_track, anchor='w', background=bgcolor, command=lambda: checkbox_action("legato_audio", checkbox_legato_audio_value), font=font, text="Legato (Audio)", variable=checkbox_legato_audio_value)
checkbox_legato_audio.grid(row=5, sticky = EW)

checkbox_flip_y = tk.Checkbutton(frame_event_track, anchor='w', background=bgcolor, command=lambda: checkbox_action("flip_y", checkbox_flip_y_value), font=font, text="Flip Y", variable=checkbox_flip_y_value)
checkbox_flip_y.grid(row=3, sticky = EW)

checkbox_flip_x = tk.Checkbutton(frame_event_track, anchor='w', background=bgcolor, command=lambda: checkbox_action("flip_x", checkbox_flip_x_value), font=font, text="Flip X", variable=checkbox_flip_x_value)
checkbox_flip_x.grid(row=2, sticky = EW)

label_event_track = tk.Label(frame_event_track, background=bgcolor, font=font_bold, text="Resolve Video Event Track")
label_event_track.grid(row=0, sticky=EW)

label_MIDI_channel = tk.Label(frame_MIDI_channel, background=bgcolor, font=font_bold, text="MIDI Channel")
label_MIDI_channel.grid(row=0, sticky=EW)

label_track_mode = tk.Label(frame_track_mode, background=bgcolor, font=font_bold, text="Track Mode")
label_track_mode.grid(row=0, sticky=EW)

MIDI_filename_entry = tk.Entry(frame_file_input, textvariable = MIDI_filename, font=font)
MIDI_filename_entry.grid(row=0, column=2, columnspan=2, sticky=EW)
	
#If there are no video tracks above a single audio track...	
if len(combo_values_event_track_grouped) > 0:
	#Default to grouped mode
	spin_box_track_mode.set(spin_values_track_mode[1])
else:
	#Default to linear mode mode
	spin_box_track_mode.set(spin_values_track_mode[0])

spin_box_action()
root.mainloop()