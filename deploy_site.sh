git pull origin master
cp deploy_site.sh ../
rm -rf *
cp ../deploy_site.sh .
cp -r ~/tmp/_site/* .
git add *
git commit -a -m"site deployment"
git push origin master
