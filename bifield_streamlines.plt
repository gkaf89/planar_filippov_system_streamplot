set terminal svg #transparent enhanced font "arial,10" fontscale 1.0 size 1000, 1200
set output 'test.svg'

set datafile separator ";"

set style arrow 1 head size 0.15,15 fixed filled linestyle 1
set style line 2 lc rgb 'black' pt 7   # circle

$point_data << EOD
4.5;36.0
EOD

plot 'streamplot/streamlines_0.dat' using 1:2 with line linestyle 1 notitle, \
	'streamplot/streamlines_1.dat' using 1:2 with line linestyle 1 notitle, \
	'streamplot/streamarrows_0.dat' using 1:2:($5-$1):($6-$2) with vectors arrowstyle 1 notitle, \
	'streamplot/streamarrows_1.dat' using 1:2:($5-$1):($6-$2) with vectors arrowstyle 1 notitle, \
	'streamplot/switching_manifold.dat' using 1:2 with line linestyle 2 notitle, \
	$point_data using 1:2 w p ls 2
