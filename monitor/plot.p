set terminal png size 600
set output "reporte.png"
set title "5 peticiones, 5 peticiones concurrentes"
set size ratio 0.6
set grid y
set xlabel "Nro Peticiones"
set ylabel "Tiempo de respuesta (ms)"
set datafile separator ","
plot "output.csv" using 6 smooth sbezier