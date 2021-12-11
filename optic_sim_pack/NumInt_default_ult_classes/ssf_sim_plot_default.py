import matplotlib.pyplot as plt
import numpy as np

from matplotlib.gridspec import GridSpec
from ..ssf_sim_useful_func import CW_return

def get_num_base(val):
    return int(np.floor(np.log10(val)))

# """Default figure mod, used if no other are provided, can be overwritten by custom module"""

class plot_class_default():

    def __init__(self, params_c, status_c):
        self.fig_vars = self._fig_vars_container()
        self.params_c = params_c 
        self.status_c = status_c
        CW_min, self.CW_max = CW_return(params_c.del0, params_c.alpha, params_c.P_in, params_c.gamma, params_c.L, params_c.theta1)

    def plot_start(self):
        """default figure constructor"""

        params = self.params_c
        fig_vars = self.fig_vars

        fig = plt.figure('ssf_sim_update', figsize = (12, 8))
        gs = GridSpec(nrows = 2, ncols = 2, left = .05, right = .95,
                    top = .98, bottom = .05, wspace = .1)

        ax1 = fig.add_subplot(gs[0,:])
        ax2 = fig.add_subplot(gs[1, :])

        lt, = ax1.plot(params.t_sample, [np.nan] * params.npt, lw = .8)
        lf, = ax2.plot(params.f_plot, [np.nan] * params.npt, lw = .8)
        
        ax1.set_xlim(params.t_sample[0], params.t_sample[-1])
        ax1.set_ylim(-.05, 5)
        
        ax2.set_xlim(params.f_plot[0], params.f_plot[-1])
        ax2.set_facecolor('none')
        status_text = ax1.annotate('', xy = (.005, .99), xycoords = 'axes fraction', va = 'top', ha = 'left', fontsize = 6)

        # """create wavelength grid if driving wavelength is available"""
        if 'lam_grid' in params:
            ax2_2 = ax2.twiny()
            ax2.set_zorder(ax2_2.get_zorder() + 2)
            # """find closes single int base"""
            upper = 3e8/(params.f_plot[0] + 3e8/params.npt)* 1e9; lower = 3e8/(params.f_plot[-1] + 3e8/params.npt)* 1e9
            interval = abs(upper - lower)/5; base = get_num_base(interval)
            interval = int(interval/10**base) * 10**base
            lam_grid = params.lam_grid
            
            # """construct and add lam_grid to figure, at the moment if fspan is too big the higher wavelength is crammped"""
            lam_grid_ticks = np.arange(lower , upper, interval); lam_grid = np.round( lam_grid, decimals = -min(base, get_num_base(min(lam_grid))))
            freq_grid = 3e8/(lam_grid_ticks*1e-9) - 3e8/params.npt

            ax2_2.set_xticks(freq_grid)
            ax2_2.set_xticklabels(lam_grid_ticks)
            ax2_2.set_xlim(ax2.get_xlim())

        else:
            pass
        
        ax2.set_ylim(-350, 10)
        plt.pause(.01)
        
        lt.set_animated(True)
        lf.set_animated(True)
        status_text.set_animated(True)
        fig.canvas.draw()

        bg1 = fig.canvas.copy_from_bbox(ax1.bbox)
        bg2 = fig.canvas.copy_from_bbox(ax2.bbox)

        fig.canvas.flush_events()
        
        fig_vars.ax1 = ax1 
        fig_vars.ax2 = ax2 
        fig_vars.lt = lt
        fig_vars.lf = lf
        fig_vars.status_text = status_text
        fig_vars.animated_list = [(fig_vars.ax1, lt), (fig_vars.ax1, status_text), (fig_vars.ax2, lf)]
        fig_vars.bg1 = bg1
        fig_vars.bg2 = bg2
        fig_vars.figure = fig 
        fig_vars.canvas = fig.canvas

        self.status_c.plot_started = True
        

    def plot_update(self):
        """default figure updator"""

        params = self.params_c
        fig_vars = self.fig_vars

        abs_E = np.abs(params.E)**2
        E_f = np.abs(np.fft.fftshift(np.fft.ifft(params.E)))**2
        E_f = 10 * np.log10(E_f/np.max(E_f))

        fig_vars.lt.set_ydata(abs_E/self.CW_max)
        fig_vars.lf.set_ydata(E_f)
        fig_vars.status_text.set_text(self.status_c.print_status(self.status_c.status_plot_list))

        fig_vars.canvas.restore_region(fig_vars.bg1)
        fig_vars.canvas.restore_region(fig_vars.bg2)

        for tup_temp in fig_vars.animated_list:
            tup_temp[0].draw_artist(tup_temp[1])

        fig_vars.canvas.blit(fig_vars.ax1.bbox)
        fig_vars.canvas.blit(fig_vars.ax2.bbox)
        fig_vars.canvas.flush_events()

    def canvas_update(self):
        
        fig_vars = self.fig_vars
        fig_vars.fig.canvas.draw()
        fig_vars.canvas.copy_from_bbox(fig_vars.ax1.bbox)
        fig_vars.canvas.copy_from_bbox(fig_vars.ax2.bbox)
        fig_vars.canvas.flush_events()

    class _fig_vars_container():
        pass 
