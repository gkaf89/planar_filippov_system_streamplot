set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 1000, 1200
set output 'test.png'

set datafile separator ";"

set style arrow 1 head size 0.15,15 fixed filled linestyle 1

plot 'streamplot/streamlines_0.dat' using 1:2 with line linestyle 1 notitle, \
	'streamplot/streamlines_1.dat' using 1:2 with line linestyle 1 notitle, \
	'streamplot/streamarrows_0.dat' using 1:2:($5-$1):($6-$2) with vectors arrowstyle 1 notitle, \
	'streamplot/streamarrows_1.dat' using 1:2:($5-$1):($6-$2) with vectors arrowstyle 1 notitle, \
	'streamplot/switching_manifold.dat' using 1:2 with line linestyle 2 notitle
