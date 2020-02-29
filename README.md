# Fine Outer Wall
Fine Outer-Wall, merging two gcode files of different layer height to create speed and outer-wall quality compromised gcode file for FDM 3D printing.

It merges outer-wall from finer layer-height(ex. 0.1mm) gcode with other portion that including infill, inner-wall from rough layer-height(ex. 0.3mm).

## Usage
1. Create two gcode files from slicer with rough(ex. 0.3mm) and fine(ex. 0.1mm) layer-height from exact same model. The slice setting shoud be exlactly same except layer-height.

`make_fow_gcode(gcode_file_rough, gcode_file_fine, gcode_file_new, layer_height_init, layer_height_rough, layer_height_fine)`

* gcode_file_rough: gcode file path of rough layer-height setting
* gcode_file_fine: gcode file path of fine layer-height setting
* gcode_file_new: gcode file path of output that created as the merge
* layer_height_init: a height of initial layer
* layer_height_rough: a layer height of rough setting (ex. 0.3mm)
* layer_height_fine: a layer height of fine setting (ex. 0.1mm)

2. For the slice, wall should be before infiil, and outer-wall should be before inner-wall.

## Limitations
As it is a proposal of concept, there are some limitations.
Some useless garbage travel of X,Y movement may remaining.
Gcode files with support are not tested.
Gcode files with skirt are only tested.
