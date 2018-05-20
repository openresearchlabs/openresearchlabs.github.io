git pull origin build
rm -rf _site
# jekyll serve # Watch the site
jekyll build
git commit -a -m"Site store"
# Run the next line the first time when setting up all
# git push origin 'git subtree split --prefix _site devel':master --force
#git subtree push --prefix _site origin master
rm -rf ~/tmp/_site
cp -r _site/* ~/tmp/  
git commit -a -m"site deployment"
git push origin build

