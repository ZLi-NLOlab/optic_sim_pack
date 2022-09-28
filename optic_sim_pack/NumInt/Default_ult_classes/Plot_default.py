import matplotlib.pyplot as plt
import numpy as np

from matplotlib.gridspec import GridSpec
from ...AuxFuncs.Misc_func import cw_return
from matplotlib import rcParams, use

rcParams['lines.linewidth'] = .8
rcParams['font.size'] = 8
rcParams['xtick.direction'] = 'in'
rcParams['ytick.direction'] = 'in'
rcParams['xtick.top'] = True
rcParams['ytick.right'] = True
rcParams['legend.fancybox'] = False
rcParams['legend.edgecolor'] = 'black'
rcParams['legend.framealpha'] = 1
rcParams['legend.handlelength'] = 1.5
rcParams['legend.fontsize'] = 8


def get_num_base(val):
    return int(np.floor(np.log10(val)))

# """Default figure mod, used if no other are provided, can be overwritten by custom module"""

class plot_class_default():
    default_status_list = ['saving', 'plotting', 'save_started', 'plot_started', 'force_proc', 'NumInt_method']
    
    @staticmethod
    def defualt_plot_text_func(cls):   
        text = "rt_counter = {}\nP_max = {:.2f}\nRaman_mode = {}"
        text = text.format(
            cls.params_c.rt_counter, 
            max(abs(cls.params_c.E))**2,
            cls.params_c.RR_method
        )
        return text

    def __init__(self, params_c, status_c):
        
        # TkAgg backend is used instead of Qt5Agg as the latter create strange issue with error catching
        try:
            use('TkAgg') 
        except ImportError:
            print('Import Error in Plot_defualt, TkAgg passed')
        
        self.config = self._fig_vars_container()
        self.params_c = params_c 
        self.status_c = status_c

        if 'LLE' in status_c.NumInt_method:
            try:
                CW_min, self.config.reference = cw_return(params_c.del0, params_c.alpha, params_c.P_in, params_c.gamma, params_c.L, params_c.theta1)
            except ZeroDivisionError:
                print('Error in calculating CW, 10 W used as reference')
                self.config.reference = 10
        elif 'NLSE' in status_c.NumInt_method:
            self.config.reference = params_c.P_in
        else: 
            self.config.reference = 10

        self.config.t_xlim = (params_c.t_sample[0], params_c.t_sample[-1])
        self.config.t_ylim = (-.05, 10)
        self.config.f_xlim = (params_c.f_plot[0], params_c.f_plot[-1])
        self.config.f_ylim = (-350, 10)
        
        self._status_check()
        
    def plot_start(self):
        """default figure constructor"""

        params = self.params_c
        config = self.config

        fig = plt.figure('ssf_sim_update', figsize = (12, 8))
        gs = GridSpec(nrows = 2, ncols = 2, left = .05, right = .95,
                    top = .98, bottom = .05, wspace = .1)

        ax1 = fig.add_subplot(gs[0,:])
        ax1_twinx = ax1.twinx(); ax1_twinx.set_zorder(0)
        ax2 = fig.add_subplot(gs[1, :])

        lt, = ax1.plot(params.t_sample, [np.nan] * params.npt, lw = .8)
        lf, = ax2.plot(params.f_plot, [np.nan] * params.npt, lw = .8)
        
        ax1_twinx.plot(params.t_sample, params.E_in_prof, c = 'red')

        ax1.set_xlim(config.t_xlim)
        ax1.set_ylim(config.t_ylim)
        
        ax2.set_xlim(config.f_xlim)
        ax2.set_ylim(config.f_ylim)

        ax2_twinx = ax2.twinx(); ax2_twinx.set_zorder(0)
        ax2_twinx.set_ylim(-1.2,1.2)

        ax2.set_facecolor('none')
        status_text = ax1.annotate('', xy = (.005, .99), xycoords = 'axes fraction', va = 'top', ha = 'left', fontsize = 6)
        params_text = ax1.annotate('', xy = (.99, .99), xycoords = 'axes fraction', va = 'top', ha = 'right', fontsize = 6)
        ax1.annotate('y-scale referene = {:.3f} W'.format(config.reference), 
            xy = (.01, .025), xycoords = 'axes fraction', va = 'bottom', ha = 'left', fontsize = 6)
        
        # """create wavelength grid if driving wavelength is available"""
        if 'lam_grid' in params:
            ax2_2 = ax2.twiny()
            ax2.set_zorder(ax2_2.get_zorder() + 2)
            # """find closes single int base"""
            upper = 3e8/(params.f_plot[0] + 3e8/params.wl_pump)* 1e9; lower = 3e8/(params.f_plot[-1] + 3e8/params.wl_pump)* 1e9
            interval = abs(upper - lower)/5; base = get_num_base(interval)
            interval = int(interval/10**base) * 10**base
            lam_grid = params.lam_grid
            
            # """construct and add lam_grid to figure, at the moment if fspan is too big the higher wavelength is crammped"""
            lam_grid_ticks = np.arange(lower , upper, interval); lam_grid_ticks = np.round( lam_grid_ticks, decimals = -min(base, get_num_base(min(lam_grid_ticks))))
            freq_grid = 3e8/(lam_grid_ticks*1e-9) - 3e8/params.wl_pump

            ax2_2.set_xticks(freq_grid)
            ax2_2.set_xticklabels(lam_grid_ticks)
            ax2_2.set_xlim(ax2.get_xlim())

        else:
            pass
        
        plt.pause(.01)
        
        lt.set_animated(True)
        lf.set_animated(True)
        status_text.set_animated(True)
        params_text.set_animated(True)
        fig.canvas.draw()

        bg1 = fig.canvas.copy_from_bbox(ax1.bbox)
        bg2 = fig.canvas.copy_from_bbox(ax2.bbox)

        fig.canvas.flush_events()
        
        config.ax1 = ax1 
        config.ax2 = ax2 
        config.twins = (ax1_twinx, ax2_twinx)
        config.lt = lt
        config.lf = lf
        config.status_text = status_text
        config.params_text = params_text
        config.animated_list = [
            (config.ax1, lt), (config.ax1, status_text), (config.ax1, params_text),
            (config.ax2, lf)]
        config.bg1 = bg1
        config.bg2 = bg2
        config.figure = fig 
        config.canvas = fig.canvas

        self.status_c.plot_started = True
        
    def plot_update(self):
        """default figure updator"""

        params = self.params_c
        status = self.status_c
        config = self.config

        abs_E = np.abs(params.E)**2
        E_f = np.abs(np.fft.fftshift(np.fft.ifft(params.E)))**2
        E_f = 10 * np.log10(E_f)

        config.lt.set_ydata(abs_E/self.config.reference)
        config.lf.set_ydata(E_f)
        config.status_text.set_text(status.print_status(status.status_plot_list))
        config.params_text.set_text(status.plot_text_func(self))

        config.canvas.restore_region(config.bg1)
        config.canvas.restore_region(config.bg2)

        for tup_temp in config.animated_list:
            tup_temp[0].draw_artist(tup_temp[1])

        config.canvas.blit(config.ax1.bbox)
        config.canvas.blit(config.ax2.bbox)
        config.canvas.flush_events()

    def canvas_update(self):
        
        config = self.config
        config.figure.canvas.draw()
        config.canvas.flush_events()
        config.bg1 = config.canvas.copy_from_bbox(config.ax1.bbox)
        config.bg2 = config.canvas.copy_from_bbox(config.ax2.bbox)
        config.canvas.flush_events()

    def _status_check(self):
        status_c = self.status_c
        status_c.plot_started = False

        if 'status_plot_list' not in status_c:
            status_c.status_plot_list = self.default_status_list
        else: pass 

        if 'plot_text_func' not in status_c:
            status_c.plot_text_func = self.defualt_plot_text_func
        else: pass 
        
    class _fig_vars_container():
        pass 
