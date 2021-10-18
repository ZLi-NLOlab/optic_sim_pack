import matplotlib.pyplot as plt
import numpy as np

from matplotlib.gridspec import GridSpec
from .ssf_sim_aux import CW_return

"""Default figure mod, used if no other are provided, can be overwritten by custom module"""

def fig_constructor(class_obj):
    fig = plt.figure('ssf_sim_update', figsize = (12, 8))
    gs = GridSpec(nrows = 2, ncols = 2, left = .05, right = .95,
                top = .98, bottom = .05, wspace = .1)

    ax1 = fig.add_subplot(gs[0,:])
    ax2 = fig.add_subplot(gs[1, :])

    lt, = ax1.plot([],[], lw = .8)
    lf, = ax2.plot([], [], lw = .8)
    
    ax1.set_xlim(class_obj.t_sample[0], class_obj.t_sample[-1])
    ax1.set_ylim(-.05, 5)
    
    if class_obj.lam_grid is None:
        ax2.set_xlim(class_obj.f_plot[0], class_obj.f_plot[-1])
    else:
        ax2.set_xlim(class_obj.lam_grid[-1], class_obj.lam_grid[0])
    ax2.set_ylim(-350, 10)
    plt.pause(.01)
    
    lt.set_animated(True)
    lf.set_animated(True)
    fig.canvas.draw()

    bg1 = fig.canvas.copy_from_bbox(ax1.bbox)
    bg2 = fig.canvas.copy_from_bbox(ax2.bbox)

    fig.canvas.flush_events()
    
    class_obj.ax1 = ax1 
    class_obj.ax2 = ax2 
    class_obj.lt = lt
    class_obj.lf = lf
    class_obj.animated_list = [(class_obj.ax1, lt), (class_obj.ax2, lf)]
    class_obj.bg1 = bg1
    class_obj.bg2 = bg2
    class_obj.figure = fig 
    class_obj.canvas = fig.canvas
    class_obj.fig_started = True

def fig_update(class_obj):
    abs_E = np.abs(class_obj.E)**2
    E_f = np.abs(np.fft.fftshift(np.fft.ifft(class_obj.E)))**2
    E_f = 10 * np.log10(E_f/np.max(E_f))

    CW_min, CW_max = CW_return(class_obj.params['del0'],
                               class_obj.params['alpha'],
                               class_obj.params['P_in'],
                               class_obj.params['gamma'],
                               class_obj.params['L'],
                               class_obj.params['theta1'])

    class_obj.lt.set_data([class_obj.t_sample, abs_E/CW_max])
    class_obj.lf.set_data([class_obj.lam_grid, E_f])

    class_obj.canvas.restore_region(class_obj.bg1)
    class_obj.canvas.restore_region(class_obj.bg2)

    for tup_temp in class_obj.animated_list:
        tup_temp[0].draw_artist(tup_temp[1])

    class_obj.canvas.blit(class_obj.ax1.bbox)
    class_obj.canvas.blit(class_obj.ax2.bbox)
    class_obj.canvas.flush_events()

