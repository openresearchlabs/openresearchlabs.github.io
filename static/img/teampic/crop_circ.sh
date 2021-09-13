convert -size 200x200 xc:Black -fill White -draw 'circle 100 100 100 1' -alpha Copy mask.png

#for f in $(ls *.jpg)
for f in $(ls katariina_parnanen.jpg)
do
  convert $f -gravity Center mask.png -compose CopyOpacity -composite -trim ${f}_output.png
done


