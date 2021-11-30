import matplotlib.pyplot as plt
import numpy as np

from matplotlib.gridspec import GridSpec
from .ssf_sim_aux import CW_return

def get_num_base(val):
    return int(np.floor(np.log10(val)))

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
    
    ax2.set_xlim(class_obj.f_plot[0], class_obj.f_plot[-1])
    ax2.set_facecolor('none')
    
    """create wavelength grid if driving wavelength is available"""
    if 'wl_pump' in class_obj.params:
        ax2_2 = ax2.twiny()
        ax2.set_zorder(ax2_2.get_zorder() + 2)
        """find closes single int base"""
        upper = 3e8/(class_obj.f_plot[0] + 3e8/class_obj.params['wl_pump'])* 1e9; lower = 3e8/(class_obj.f_plot[-1] + 3e8/class_obj.params['wl_pump'])* 1e9
        interval = abs(upper - lower)/5; base = get_num_base(interval)
        interval = int(interval/10**base) * 10**base
        
        """construct and add lam_grid to figure, at the moment if fspan is too big the higher wavelength is crammped"""
        lam_grid = np.arange(lower , upper, interval); lam_grid = np.round( lam_grid, decimals = -min(base, get_num_base(min(lam_grid))))
        freq_grid = 3e8/(lam_grid*1e-9) - 3e8/class_obj.params['wl_pump']

        ax2_2.set_xticks(freq_grid)
        ax2_2.set_xticklabels(lam_grid)
        ax2_2.set_xlim(ax2.get_xlim())

    else:
        pass
    
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
    class_obj.lf.set_data([class_obj.f_plot, E_f])

    class_obj.canvas.restore_region(class_obj.bg1)
    class_obj.canvas.restore_region(class_obj.bg2)

    for tup_temp in class_obj.animated_list:
        tup_temp[0].draw_artist(tup_temp[1])

    class_obj.canvas.blit(class_obj.ax1.bbox)
    class_obj.canvas.blit(class_obj.ax2.bbox)
    class_obj.canvas.flush_events()

