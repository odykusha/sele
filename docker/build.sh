#!/usr/bin/env bash

HASH_SUM=`./docker/check_enviroment_changes.sh`
SE_ENV_CONTAINER=odykusha/seledka:${HASH_SUM}


build_dir=$(mktemp -d)

cp -v docker/Dockerfile $build_dir
cp -v docker/selenium.txt $build_dir
cp -v requirements.txt $build_dir

cd $build_dir


docker build -f ./Dockerfile -t $SE_ENV_CONTAINER .

rm -r $build_dir
