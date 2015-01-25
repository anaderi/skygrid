#!/bin/sh

BUILD_DIR=/tmp/build-jar-dir
PROJECT_DIR=/Users/stromsund/Development/skygrid/executors/YARN
RESULT_JAR=YarnExecutorWithDeps-1.0.jar

cd $PROJECT_DIR
mvn package

rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

cp $PROJECT_DIR/target/YarnTestClient-1.0.jar $BUILD_DIR
cd $BUILD_DIR
jar -xf YarnTestClient-1.0.jar
rm -rf META-INF

for dep_jar in ws-commons-util-1.0.2.jar  xmlrpc-client-3.1.3.jar  xmlrpc-common-3.1.3.jar
do
  cp $PROJECT_DIR/target/dependency/$dep_jar $BUILD_DIR
  jar -xf $dep_jar
  rm -rf META-INF
done

cp /Users/stromsund/Development/skygrid/splitter/splitter/target/splitter-1.0-SNAPSHOT.jar $BUILD_DIR
jar -xf splitter-1.0-SNAPSHOT.jar
rm -rf META-INF


for dep_jar in $(find /Users/stromsund/Development/skygrid/splitter/splitter/target/dependency -type f)
do
  cp $dep_jar $BUILD_DIR
  jar -xf $(basename $dep_jar)
  rm -rf META-INF
done

rm $BUILD_DIR/*.jar
jar -cf $RESULT_JAR *

cd $PROJECT_DIR
cp $BUILD_DIR/$RESULT_JAR target/
