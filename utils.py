from sc3.all import *
import ipywidgets as widgets
import mido

def boot():
    if not s.status.server_running:
        s.boot(on_complete=lambda: main.resume(), on_failure= lambda: main.resume())
        main.wait();
        
def nodewidgets(node, gui_conf, midiin=None):
    def f(**kwargs):
        try:
            for k,v in kwargs.items():
                node.set(k, v)
        except:
            pass
    return guiwidgets(gui_conf, f, midiin=midiin)

def guiwidgets(gui_conf, func, midiin=None):
    wgts = {}
    for k,v in gui_conf.items():
        wgt = None
        if 'scale' in v:
            if v['scale']=='log':
                wgt = widgets.FloatLogSlider(min=v['min'], max=v['max'], step=v['step'], value=v['value'])
        else:
            wgt = widgets.FloatSlider(min=v['min'], max=v['max'], step=v['step'], value=v['value'])
        if wgt is not None:
            wgts[k] = wgt           
    wi = widgets.interact(func,**wgts)
    sliders = {w.get_state()['description']:w for w in wi.widget.children[:-1]}
    
    
    
    if midiin is not None:
        def callback(w,v):
            def func(x):
                w.value = x/127*(v['max']-v['min'])+v['min']
            return func
        
        for k,slider in sliders.items():
            v = gui_conf[k]
            if 'cc' in gui_conf[k]:
                midiin.subscribe('control_change',v['cc'], callback(slider,v) )
    return wi

class MidiInput():
    def return_midi_callback(self):
        def midi_callback(msg):
            for callback in self.callbacks:
                if callback['type']==msg.type and callback['control']==msg.control:
                    callback['call'](msg.value)
        return midi_callback
    
    def __init__(self, port):
        self.inport = mido.open_input(port)
        self.callbacks = []
        self.inport.callback = self.return_midi_callback()    
    def subscribe(self, type_, control, func):
        self.callbacks.append({'type':type_, 'control': control, 'call' :func})

def button(label, func):
    b = widgets.Button(description=label)
    b.on_click(func)
    return b   

def toolbar():
    b = button('CMD PERIOD',lambda x: CmdPeriod.run() )
    vol = widgets.FloatSlider(min=-60, max=0, step=1, value=-0, description='volume')
    vol.observe(lambda x: setattr(s.volume,'gain',x['new']), names='value')
    return widgets.HBox([b,vol])