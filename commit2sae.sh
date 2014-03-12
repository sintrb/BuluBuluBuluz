#!/bin/bash
curpath=`pwd`
locpath='/home/robin/git/BuluBuluBuluz'
tmppath='/tmp/_bulu'
echo 'localpath: ' $locpath
cd $locpath
git pull

echo 'temppath: ' $tmppath
rm -rf $tmppath

cp -rf $locpath  $tmppath
cd $tmppath
find | grep -i '.svn' | xargs rm -rf

echo 'curpath: ' $curpath
cd $curpath

cp -rf $tmppath/* $curpath
svn commit -m ''

