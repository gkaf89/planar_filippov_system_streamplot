set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 500, 600
set output 'test.png'

set datafile separator ";"

plot 'test.dat' using 1:2 with line
