from numpy.fft import fftshift

from ..Phase_matching import delta_g_calc, delta_phi_calc
from ..Misc_func import find_zero

__all__ = ['phase_info_plot']

def phase_info_plot(self, ax, pp_scale = 1, pg_scale = 1, vline = True, p_plot = True, g_plot = True, r_plot = True) -> list:
    """add phase_matching, group-delay matching and Raman gain curves to given axis"""
    params = self.params_c
    npt = params.npt
    f_inter = params.f_plot[1] - params.f_plot[0]
    pg = delta_g_calc(params)
    pp = delta_phi_calc(params)

    out_temp = []
    if p_plot:
        lpp, = ax.plot(params.f_plot, pp/(max(pp) - min(pp))/pp_scale, c = 'C2')
        out_temp.append(lpp)
    if g_plot:
        lpg, = ax.plot(params.f_plot, pg/(max(pg) - min(pg))/pg_scale, c = 'C1')
        out_temp.append(lpg)

    if vline:
        for line_temp in out_temp:
            y_data = line_temp.get_ydata()
            zero_cross = (find_zero(y_data) - npt//2) * f_inter
            for zc_temp in zero_cross:
                ax.axvline(zc_temp, ls = '--', c = line_temp.get_color())
        ax.axhline(0, ls = '--', c = 'black')

    if r_plot:
        if 'RR_f' in params:
            lR, = ax.plot(params.f_plot, fftshift(params.RR_f.imag)/max(params.RR_f.imag), c = 'red')
            out_temp.append(lR)

    return out_temp

def save_final_roundtrips(self, N_rt):
    if not self.status_c.saving:
        if self.params_c.rt_counter == (self.params_c._M - N_rt * self.params_c._S_intv):
            if not self.status_c.save_started:
                self.save_control.save_start()
