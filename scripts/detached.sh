#!/bin/bash

branch='master'
tempbranch='recover'

##########
git checkout -b $tempbranch
git branch -f $tempbranch $branch
git checkout $branch
git branch -d $tempbranch
git push origin $branch
