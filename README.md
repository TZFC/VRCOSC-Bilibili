# VRCOSC-Bilibili
Connect to Bilibili livestream and trigger OSC messages on events

# User guide
import OSC-Bilibili.unitypackage [release link here] into your avatar project

use Avatar Manager [vcc link here] to merge animation controller located in OSC-Bilibili/osc-bilibili.fx

Fill in config in Config.yaml

log into Bilibili with firefox browser

double click RUNME.bat

# Tech design

Avatar parameters:

gift_id int 8-bit | gift_price int 8-bit | gift_num float 8-bit

use gift_id and/pr gift_price to transition animation state

use gift_num to drive Blendtree

Animation should be set to play 1 second loop

Timeline fot every second:

 - set gift_id

 - set gift_price

 - set gift_num

 - Start new animation loop