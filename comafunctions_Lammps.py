import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import math
import ipywidgets
import shutil
from ipywidgets import interact, fixed, interact_manual, widgets, Button, Layout, AppLayout, VBox
from IPython.display import display, HTML
import ovito as ov
from ovito.io import import_file
from ovito.modifiers import PolyhedralTemplateMatchingModifier, SelectTypeModifier, CommonNeighborAnalysisModifier, ComputePropertyModifier
from ovito.vis import *
from ovito.pipeline import *
from ovito.data import DataCollection
from ovito.data import *
from lammps import lammps

def preview_structure(file):
    pipeline_0 = import_file(f'{file}', multiple_frames=True)
    data = pipeline_0.compute()
    pipeline_0.add_to_scene()
    
    
    
    def modify_pipeline_input(frame: int, data: DataCollection):
        data.particles_.particle_types_.type_by_id_(1).radius = 0.5

    pipeline_0.modifiers.append(modify_pipeline_input)
    pipeline_0.modifiers.append(CommonNeighborAnalysisModifier())
    pipeline_0.modifiers.append(SelectTypeModifier(
    operate_on = "particles",
    property = "Structure Type",
    types = {CommonNeighborAnalysisModifier.Type.FCC,
            CommonNeighborAnalysisModifier.Type.BCC,
            CommonNeighborAnalysisModifier.Type.HCP}))


    data = pipeline_0.compute()
    print("Number of structured atoms: %i" % data.attributes['SelectType.num_selected'])
    

    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 2, -1))
    vp.zoom_all()
    window_1 = vp.create_jupyter_widget()
    window_tmp = vp.create_jupyter_widget()
    window_1.camera_params = window_tmp.camera_params
    window_1.orbit_center = vp.orbit_center
    window_1.layout = Layout(width='auto', height='auto')
    window_1.refresh()
    display(window_1)
    pipeline_0.remove_from_scene()

def animate(dump,thermo):
    pipeline = import_file(f'{dump}', multiple_frames=True)
    data_in = np.loadtxt(f'{thermo}')
    timestep = data_in[:,0]
    temperature = data_in[:,1]
    
    def modify_pipeline_input(frame: int, data: DataCollection):
        data.particles_.particle_types_.type_by_id_(1).radius = 0.5
    
    pipeline.modifiers.append(modify_pipeline_input)

    pipeline.modifiers.append(CommonNeighborAnalysisModifier())
    pipeline.modifiers.append(SelectTypeModifier(
    operate_on = "particles",
    property = "Structure Type",
    types = { CommonNeighborAnalysisModifier.Type.FCC,
            CommonNeighborAnalysisModifier.Type.BCC,
            CommonNeighborAnalysisModifier.Type.HCP}))


    data = pipeline.compute()
    print("Number of FCC atoms: %i" % data.attributes['SelectType.num_selected'])

    title_show = widgets.HTML(value="<h2>Animation of Results</h2>", layout=Layout(height='5px', width='100%'))

    pipeline.add_to_scene()
    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 2, -1))
    vp.zoom_all()
    

    max_frame = pipeline.source.num_frames
    play_image = widgets.Play(
        value=0,
        min=0,
        max=max_frame,
        step=1,
        description="Press play",
        disabled=False,
        layout=Layout(width='auto', height='50px')
    )

            
    slider = widgets.FloatProgress(
        value=0,
        min=0,
        max=max_frame -1,
        step=1,
        description='Progress:',
        bar_style='success',
        orientation='horizontal',
        layout=Layout(width='auto', height='50px')
    )

    control = widgets.IntSlider(
        value=0,
        min=0,
        max=max_frame-1,
        description = 'Frame:',
        disabled = False,
        orientation = 'horizontal',
        layout=Layout(width='auto', height='50px')
    )

    time_show = widgets.HTML(
        value=f"Time: {timestep[vp.dataset.anim.current_frame]/1000:5.0f} ps",
        min=0,
        max=max_frame-1,
        layout=Layout(width='auto', height='auto', fontsize=50),
        margin=('0px 0px 60px 0px')
    )

    temperature_show = widgets.HTML(
        value=f"<h3>Temperature: {temperature[vp.dataset.anim.current_frame]:4.0f} K</h3>",
        min=0,
        max=max_frame-1,
        layout=Layout(width='auto', height='auto'),
        margin=('0px 0px 50px 0px')
    )

    widgets.jslink((play_image, 'value'), (slider, 'value'))
    widgets.jslink((play_image, 'value'), (control, 'value'))

    def on_frame_change(change):
      temperature_show.value = f"<h3>Temperature: {temperature[vp.dataset.anim.current_frame]:4.0f} K</h3>"
      time_show.value = f"Time: {timestep[vp.dataset.anim.current_frame]/1000:5.0f} ps"
    
    play_image.observe(on_frame_change, "value")

    def play(vp, x, w):
        vp.dataset.anim.current_frame = x
        w.refresh()

    window = vp.create_jupyter_widget()
    window.layout = ipywidgets.Layout(width='auto', height='auto')
    widgets.interactive(play, x=play_image, vp=fixed(vp), w=fixed(window))
    
    close_button = widgets.Button(
        description='Close',
        layout=Layout(width='auto', height='50px', margin='355px 0px 0px 0px'),
        button_style='success'
    )
    
    def close_click(sender):
        pipeline.remove_from_scene()
        window.scene.clear()
        close_button.button_style='danger'

    # connect the function with the button
    close_button.on_click(close_click)
    
    Box = AppLayout(header=title_show,
                      center=window,
                      left_sidebar=None,
                      right_sidebar=VBox([play_image, control, slider, time_show, temperature_show, close_button]),
                      footer=None,
                      pane_widths=['0px', '700px', '250px'], #original: ['0px', '820px', '300px']
                      pane_heights=['65px', '600px', '00px'], #original: ['0px', '820px', '300px']
                      width="100%",
                      grid_gap="10px")
    display(Box)
