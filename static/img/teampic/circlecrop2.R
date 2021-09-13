library(magick)
path <- "katariina_parnanen.jpg"
im <- magick::image_read(path)

# get height, width and crop longer side to match shorter side
ii <- magick::image_info(im)
ii_min <- min(ii$width, ii$height)
#im1 <- magick::image_crop(im, geometry=paste0(ii_min, "x", ii_min, "+0+0"), repage=TRUE)
im1 <- magick::image_crop(im, geometry=paste0("320x213", "+0+0"), repage=TRUE)

# create a new image with white background and black circle
fig <- magick::image_draw(image_blank(500, 500))
#symbols(ii_min/2, ii_min/2, circles=(ii_min/2)-3, bg='black', inches=FALSE, add=TRUE)
symbols(160,100, circles=100, bg='black', inches=FALSE, add=TRUE)
dev.off()

# create an image composite using both images
im2 <- magick::image_composite(im1, fig, operator='copyopacity')

# set background as white
im3 <- magick::image_background(im2, 'white')

jpeg("katariina_parnanen_crop.jpg")
plot(im3)
dev.off()

