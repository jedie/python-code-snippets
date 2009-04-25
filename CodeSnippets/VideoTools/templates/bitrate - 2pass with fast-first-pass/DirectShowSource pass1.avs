DirectShowSource("${video_filename}", audio=false)

## film crop:
#crop( 0, 140, 0, -140)

## testing:
#crop(768, 256, -768, -256)
#Trim(50000,55000)

## fast first pass with lower resolusion:
ReduceBy2()

