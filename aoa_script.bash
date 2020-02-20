python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 10 -r 0 -d 200912  -n 'Age of air (uniform source) tracer' -k Tracers.GEOS.list -f aoa
python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 50 -r 0 -d 200912  -n 'Age of air (uniform source) tracer' -k Tracers.GEOS.list -f aoa
python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 500 -r 0 -d 200912  -n 'Age of air (uniform source) tracer' -k Tracers.GEOS.list -f aoa
python PlotTracerZM.py -g TR_GOCART.tracers_avg.monthly.200912.nc4 -r 0 -d 200912  -k Tracers.GEOS.list -f aoa
python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 200 -r 0 -d 200912  -n  'Age of air above boundary layer' -k Tracers.GEOS.list -f aoa_bl
python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 500 -r 0 -d 200912  -n 'Age of air above boundary layer'  -k Tracers.GEOS.list -f aoa_bl
python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 850 -r 0 -d 200912  -n 'Age of air above boundary layer' -k Tracers.GEOS.list -f aoa_bl
python PlotTracerZM.py -g TR_GOCART.tracers_avg.monthly.200912.nc4 -r 0 -d 200912  -k Tracers.GEOS.list -f aoa_bl
python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 200 -r 0 -d 200912  -n  'Age of air northern hemisphere tracer' -k Tracers.GEOS.list -f aoa_nh
python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 500 -r 0 -d 200912  -n 'Age of air northern hemisphere tracer'  -k Tracers.GEOS.list -f aoa_nh
python PlotTracerSlice.py -c TR_GOCART.tracers_avg.monthly.200912.nc4 -l 1000 -r 0 -d 200912  -n 'Age of air northern hemisphere tracer' -k Tracers.GEOS.list -f aoa_nh
python PlotTracerZM.py -g TR_GOCART.tracers_avg.monthly.200912.nc4 -r 0 -d 200912  -k Tracers.GEOS.list -f aoa_nh

