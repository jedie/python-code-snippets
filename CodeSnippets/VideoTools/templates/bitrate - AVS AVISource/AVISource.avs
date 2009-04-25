AVISource("${video_filename}", audio=false)

## film crop:
#crop( 0, 140, 0, -140)

## testing:
#crop(768, 256, -768, -256)
#Trim(50000,55000)

## normal (long film):
fft3dfilter(sigma=2.0, plane=4, sharpen=1, ncpu=4)
TemporalSoften(1, 4, 6)

## fine (short film):
#fft3dfilter(sigma=1.0, plane=4, sharpen=1, ncpu=4)
#TemporalSoften(1, 2, 3)