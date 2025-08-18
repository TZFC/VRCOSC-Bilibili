# VRCOSC-Bilibili

Connect to Bilibili livestream and trigger OSC messages on events

链接Bilibili直播间弹幕信息流，根据弹幕事件，依照用户设置，发送OSC参数更新与聊天框消息到VRChat

使用说明见 [最新 Release](https://github.com/TZFC/VRCOSC-Bilibili/releases/latest)


# Tech design 技术设计

Avatar parameters: 角色参数（根据开启的功能，可选）

event_id int 8-bit | event_num float 8-bit | animation_num_name * n float 8-bit * n

8位1个int + 8位1个float为通用事件使用的参数，每个独立动画占8位1个float

For general event, use event_id to drive fx states 通用动画里用 event_id 推进fx状态机

use event_num to drive Blendtree animations 用 event_num 控制动画

See Config.toml for more details 详见 [Config.tomle](https://github.com/TZFC/VRCOSC-Bilibili/blob/main/Config.toml)
