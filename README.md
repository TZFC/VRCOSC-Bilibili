# VRCOSC-Bilibili
Connect to Bilibili livestream and trigger OSC messages on events

# User guide
import OSC-Bilibili.unitypackage [release link here] into your avatar project

use Avatar Manager [vcc link here] to merge animation controller located in OSC-Bilibili/osc-bilibili.fx

Fill in config in Config.toml

log into Bilibili with firefox browser

double click RUNME.bat

# Tech design

Avatar parameters:

event_id int 8-bit | event_num float 8-bit | animation_num_name * n float 8-bit * n

use event_id to drive fx states

use event_num/animation_num_name to drive Blendtree animations

See Config.toml for more details
