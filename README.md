# YTPMVD
YTP Midi Video for DaVinci Resolve (YTPMVD) generates YTPMV sequences in a Davinci Resolve timeline automatically from MIDI files.

## External Dependencies

* Python 3
* Mido

## Installation

1. Install Python and its dependencies as administrator and make sure they're on your system PATH.
2. Install mido pip install mido
3. Run install.bat

## Use

1. Create a timeline in Davinci Resolve
2. Add clips to the timeline
3. Execute Workspace > Scripts > YTPMVD > YTPMVD_UI
4. Configure options
* Click "Select MIDI File" and select a midi file
* Set the track mode to "grouped" to process video clips with linked audio as a single unit, or "linear" to process only video clips
* Click "Auto map outputs" to sequentially assign timeline tracks to MIDI channels
* Use the dropdown menus to assign specific channels to individual tracks
* Use the flipping checkboxes to enable flipping and the legato checkboxes to remove gaps between clips
5. Click "GO!"