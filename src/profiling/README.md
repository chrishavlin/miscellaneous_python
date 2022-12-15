just a test directory for trying out different profiling tools 


To try out `profilehooks` and `gprof2dot`: 

```
$ pip install -r requirements.txt 
$ python test_script.py ProjectionPlot 10
$ gprof2dot -f pstats ProjectionPlot_10.pstats | dot -Tpdf -o ProjectionPlot_10.pdf
$ flameprof ProjectionPlot_10.pstats > ProjectionPlot_10_flame.svg

```


`test_script.py` shows how to output profile stats to different files for different functions.
