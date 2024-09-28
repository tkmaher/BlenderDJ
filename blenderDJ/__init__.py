from pip._internal import main
main(['install','pyaudio'])
import pyaudio

if "bpy" in locals():
    import importlib
    importlib.reload(main)
    importlib.reload(listener)
    from listener import *
else:
    import bpy
    from . import listener

bl_info = {
    "name": "BlenderDJ",
    "author": "otherseas1",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport",
    "description": "Binds audio inputs to Blender variables",
}

def addInputs(self, context):
    options = []
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        if (pa.get_device_info_by_index(i).get("maxInputChannels") > 0):
            options.append( ('OP' + str(i),  str(i) +' - '+ pa.get_device_info_by_index(i).get("name"), "") )
    return options
 
properties = []

def updateInput(self, context):
    print(int(context.scene.my_tool.input[2:]))
    listener.stream = listener.reformat(int(context.scene.my_tool.input[2:]))

def currentVars(self, context):
    param1 = int(context.scene.my_tool.params[2:])
    options = []
    for i in range(0, len(listener.VARATTR[param1])):
        options.append( ('OP' + str(i), str(listener.VARATTR[param1][i]), "") )
    return options

def setMult(self, context):
    param1 = int(context.scene.my_tool.params[2:])
    if (len(listener.VARATTR[param1]) > 0):
        param2 = int(context.scene.my_tool.vars[2:])
        context.scene.my_tool.mult = listener.VARMULT[param1][param2]

def updateMult(self, context):
    param1 = int(context.scene.my_tool.params[2:])
    if (len(listener.VARATTR[param1]) > 0):
        param2 = int(context.scene.my_tool.vars[2:])
        listener.VARMULT[param1][param2] = context.scene.my_tool.mult

def updateSmooth(self, context):
    listener.SMOOTHING = float(context.scene.my_tool.smooth)

def updateLowMid(self, context):
    listener.LOWMID = float(context.scene.my_tool.lowmid)
    if (float(context.scene.my_tool.lowmid) >= float(context.scene.my_tool.midhigh)):
        context.scene.my_tool.lowmid = context.scene.my_tool.midhigh
    
def updateMidHigh(self, context):
    listener.MIDHIGH = float(context.scene.my_tool.midhigh)
    if (float(context.scene.my_tool.lowmid) >= float(context.scene.my_tool.midhigh)):
        context.scene.my_tool.midhigh = context.scene.my_tool.lowmid

class varRemover(bpy.types.Operator):
    bl_idname = 'object.remove'
    bl_label = 'Remove variable'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        param1 = int(context.scene.my_tool.params[2:])
        if (len(listener.VARATTR[param1]) > 0):
            param2 = int(context.scene.my_tool.vars[2:])
            listener.remove(param1, param2)
            if len(listener.VARATTR[param1]) != 0:
                bpy.context.scene.my_tool.vars = 'OP' + str(len(listener.VARATTR[param1]) - 1)
        return {"FINISHED"}

class MyProperties(bpy.types.PropertyGroup):
    input : bpy.props.EnumProperty(
        name= "Input",
        description= "Select audio input.",
        items= addInputs,
        update = updateInput
    )
    
    lowmid : bpy.props.FloatProperty(name= "Low-mid cutoff", default= 1000, update = updateLowMid, max = 20000, min = 0)
    midhigh : bpy.props.FloatProperty(name= "Mid-high cutoff", default=6000, update = updateMidHigh, max = 20000, min = 0)
    
    params : bpy.props.EnumProperty(
        name= "Audio parameter",
        description= "Variables affected by audio level",
        items = [('OP0', "Level", "Affects variables according to the overall volume level."), 
                ('OP1', "Right levels", "Affects variables according to the right stereo peak."), 
                ('OP2', "Left levels", "Affects variables according to the left stereo peak."), 
                ('OP3', "Frequency peak", "Affects variables in accordance with the current loudest frequency.")],
                #('OP4', "Low levels", "Affects variables according to user-defined low-frequency levels."), 
                #('OP5', "Mid levels", "Affects variables according to user-defined middle-ranged frequency levels."), 
                #('OP6', "High levels", "Affects variables according to user-defined high-frequency levels.")],
        update = setMult
    )
    
    vars : bpy.props.EnumProperty(
        name= "Variable",
        description= "Variables affected by audio level",
        items =currentVars,
        update = setMult
    )
    
    mult : bpy.props.FloatProperty(name= "Multiplier", default= 1, update= updateMult)
    smooth : bpy.props.FloatProperty(name= "Smoothing", default= 0.5, update= updateSmooth, max=0.999, min=0)
 
class BlenderDJ_main_panel(bpy.types.Panel):
    bl_label = "BlenderDJ"
    bl_idname = "BlenderDJ_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI' 
    bl_category = "BlenderDJ"
    #bl_context = "scene"
 
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        layout.prop(mytool, "input")
        layout.prop(mytool, "smooth")
        #layout.prop(mytool, "lowmid")
        #layout.prop(mytool, "midhigh")
        
        layout.separator()
        
        layout.prop(mytool, "params")
        layout.prop(mytool, "vars")
        
        layout.prop(mytool, "mult")
        
        layout.operator("object.remove", icon='X', text="Remove Variable")

#Selector

class WM_MT_dropdown_context(bpy.types.Menu):
    bl_idname = "wm.button_context_test"
    bl_label= "init"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        pass

def draw_self(self, context):
    layout = self.layout
    layout.separator()
     # call the second custom menu
    layout.menu("OBJECT_MT_sub_menu", icon="COLLAPSEMENU")


class OBJECT_MT_subMenu(bpy.types.Menu):
    bl_label = "BlenderDJ"
    bl_idname = "OBJECT_MT_sub_menu"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.area.type == 'PROPERTIES'
    
    def draw(self, context):
        layout = self.layout

        layout.label(text="button")
        layout.operator("wm.lev", text="Bind to 'Level'")
        layout.operator("wm.r", text="Bind to 'Right level'")
        layout.operator("wm.l", text="Bind to 'Left level'")
        layout.operator("wm.freq", text="Bind to 'Frequency peak'")
    

class lev(bpy.types.Operator):
    bl_idname = "wm.lev"
    bl_label= "lev"
    
    def execute(self, context):
        listener.update("lev")
        bpy.context.scene.my_tool.params = 'OP0'
        bpy.context.scene.my_tool.vars = 'OP' + str(len(listener.VARATTR[0]) - 1)
        return {'FINISHED'}
    
class r(bpy.types.Operator):
    bl_idname = "wm.r"
    bl_label= "r"
    
    def execute(self, context):
        listener.update("r")
        bpy.context.scene.my_tool.params = 'OP1'
        bpy.context.scene.my_tool.vars = 'OP' + str(len(listener.VARATTR[1]) - 1)
        return {'FINISHED'}
    
class l(bpy.types.Operator):
    bl_idname = "wm.l"
    bl_label= "l"
    
    def execute(self, context):
        listener.update("l")
        bpy.context.scene.my_tool.params = 'OP2'
        bpy.context.scene.my_tool.vars = 'OP' + str(len(listener.VARATTR[2]) - 1)
        return {'FINISHED'}
    
class freq(bpy.types.Operator):
    bl_idname = "wm.freq"
    bl_label= "freq"
    
    def execute(self, context):
        listener.update("freq")
        bpy.context.scene.my_tool.params = 'OP3'
        bpy.context.scene.my_tool.vars = 'OP' + str(len(listener.VARATTR[3]) - 1)
        return {'FINISHED'}

#End selector

classes = [MyProperties, BlenderDJ_main_panel, WM_MT_dropdown_context, OBJECT_MT_subMenu, lev,r,l,freq, varRemover] #low,mid,high

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type= MyProperties)
    bpy.types.UI_MT_button_context_menu.append(draw_self)
 
def unregister():
    #FIND OUT HOW TO RELOAD VECTORS ON QUIT AND REOPEN
    for cls in classes:
         bpy.utils.unregister_class(cls)
    #del bpy.types.Scene.my_tool
    bpy.types.UI_MT_button_context_menu.remove(draw_menu)
 
 
 
if __name__ == "__main__":
    register()