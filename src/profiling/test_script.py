import yt
from profilehooks import profile
import sys


def get_profiling_func(pstats_file):

    @profile(filename=pstats_file, profiler="cProfile")
    def make_a_plot(plot_func, ds, field):
        p = plot_func(ds, "x", field) 
        p.save()

    return make_a_plot 


if __name__ == "__main__":
    
    # get the projection function
    plot_type = sys.argv[1]
    N_runs = int(sys.argv[2])
    output_pstats_file = f"{plot_type}_{N_runs}.pstats" 

    # initialize outside so that we store all the iterations
    plot_caller = get_profiling_func(output_pstats_file)

    fld = ("enzo", "Density")
    yt_plot_func = getattr(yt, plot_type)
    for it in range(N_runs):
        # reload every time to make sure any caches are cleared
        ds = yt.load_sample("IsolatedGalaxy")
        # call it!
        plot_caller(yt_plot_func, ds, fld)



