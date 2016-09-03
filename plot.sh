#!/bin/bash

FILE=hist.txt

echo "Plotting Histogram as PNG"

gnuplot -persist << PLOT
  set xlabel "Latency in us"
  set ylabel "Number of latency samples"
  set logscale y
  set title "Latency Histogram Plot"
#  set terminal png
#  set output "hist.png"
  plot "$FILE" using 1:2 with steps ls 1 title "CPU0"
  quit
PLOT

echo "Done."
