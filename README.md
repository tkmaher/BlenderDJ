---Pre-alpha for BlenderDJ, a live audio visualization addon for Blender 4.0---

Currently only tested on OSX.

Setup (MacOS):

  0. Open Blender from the terminal (necessary for the addon to access your computer's audio input)
  1. Drag blenderDJ.zip into Blender, or import it manually from "Edit -> Preferences -> Add-ons -> 'Install From Disk...'"
  2. Click "Ok"
  3. Done!

Features:

  -Variables in the "Properties" section (typically lower right panel) can be bound to audio inputs by right-clicking and selecting the BlenderDJ menu.
  
  <img width="751" alt="Screenshot 2024-09-28 at 7 36 42 PM" src="https://github.com/user-attachments/assets/82507498-0862-444a-991b-a46c9ded62a9">
  
  -The "BlenderDJ" tab in the 3D viewport controls the bindings of each variable. Variables can be bound to four audio parameters: volume peak, left channel volume peak, right channel volume peak, and frequency peak.
  
  <img width="566" alt="Screenshot 2024-09-28 at 7 37 15 PM" src="https://github.com/user-attachments/assets/9192d9d6-f784-4303-84f4-74c536bc4519">

Limitations:

  -BlenderDJ currently does not support user variable saving between sessions.
  -Blender must be run through the Terminal to detect audio input.
