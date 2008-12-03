AVISource("${video_filename}")

#crop( 0, 140, 0, -140)

#Trim(87850,90000)
#Trim(87690,88000)
#ReduceBy2()

#fft3dfilter(sigma=2.0, plane=4, sharpen=1, ncpu=4)
#TemporalSoften(1, 4, 6)