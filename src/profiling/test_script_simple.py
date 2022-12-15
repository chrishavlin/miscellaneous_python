import yt
from profilehooks import profile
import sys

@profile(filename="ProjectionPlot.pstats", profiler="cProfile")
def make_projection_plot(ds, field):
    p = yt.ProjectionPlot(ds, "x", field) 
    p.save()


if __name__ == "__main__":
    
    ds = yt.load_sample("IsolatedGalaxy")
    fld = ("gas", "density")
    make_projection_plot(ds, fld)


