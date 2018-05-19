# Push _site (subtree) to gh-pages

git pull origin devel
rm -rf _site
# jekyll serve # Watch the site
jekyll build
git commit -a -m"Site store"
#git push origin 'git subtree split --prefix _site devel':master --force
git subtree push --prefix _site origin master
git push origin devel


