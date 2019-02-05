sudo apt-get install imagemagick 
mkdir resized
find . -name "*.jpg" | xargs -i convert -scale 40% {} ./resized/{} 
find . -name "*.JPG" | xargs -i convert -scale 40% {} ./resized/{} 
ls resized 