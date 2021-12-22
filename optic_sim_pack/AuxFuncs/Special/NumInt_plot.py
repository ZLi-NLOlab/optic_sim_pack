from numpy.fft import fftshift

from ..Phase_matching import delta_g_calc, delta_phi_calc
from ..Misc_func import find_zero

__all__ = ['phase_info_plot']

def phase_info_plot(self, ax, pp_scale = 1, pg_scale = 1, vline = True) -> list:
    params = self.params_c
    npt = params.npt
    f_inter = params.f_plot[1] - params.f_plot[0]
    pg = delta_g_calc(params)
    pp = delta_phi_calc(params)
    lpp, = ax.plot(params.f_plot, pp/(max(pp) - min(pp))/pp_scale, c = 'C2')
    lpg, = ax.plot(params.f_plot, pg/(max(pg) - min(pg))/pg_scale, c = 'C1')
    out_temp = [lpp, lpg]
    if 'RR_f' in params:
        lR, = ax.plot(params.f_plot, fftshift(params.RR_f.imag)/max(params.RR_f.imag), c = 'red')
        out_temp.append(lR)

    if vline:
        pp_zc = (find_zero(pp) - npt//2) * f_inter
        pg_zc = (find_zero(pg) - npt//2) * f_inter 
        for n in pp_zc:
            ax.axvline(n, ls = '--', c = lpp.get_color())
        for n in pg_zc:
            ax.axvline(n, ls = '--', c = lpg.get_color())
        ax.axhline(0, ls = '--', c = 'black')
    return out_temp