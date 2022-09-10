set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 1000, 1200
set output 'test.png'

set datafile separator ";"
set style arrow 1 head size 0.15,15 fixed filled linestyle 1

plot 'streamlines.dat' using 1:2 with line notitle, \
	'stream_arrows.dat' using 1:2:($3-$1):($4-$2) with vectors arrowstyle 1 notitle
