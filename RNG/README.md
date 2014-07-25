Run Random Number Generator in YARN using Vagrant - Instructions
-------------

Firstly, we need to setup Vagrant (single-node) from [here][1]

After we have installed Vagrant, we do the following:

vagrant preparation
-------------

`cd vagrant-cascading-hadoop-cluster/single-node`  

`vagrant up`  

`vagrant ssh master`

 communicate with YARN without any extra setup
-------------

`cd /opt/hadoop-2.3.0/etc/hadoop/`  

`mkdir /vagrant/configs`  

`cp * /vagrant/configs`  

`cd /vagrant/openlab_ship_proto/RNG`

create jar file in target folder
-------------

`mvn package`  

`mvn dependency:copy-dependencies`

parameters to run the program
-------------
1. useless test argument (I will remove this)
2. minimum random number
3. maximum random number
4. number of Containers to be created
5. crowd numbers to be created in each container
6. output filename in /user/yarnuser/CernYarnApp/generatedNumbers/ path in HDFS

run the program
-------------

`java -cp "~/vagrant-cascading-hadoop-cluster/single-node/configs/:target/YarnTestClient-1.0.jar:target/dependency/*" ru.yandex.cern.yarntest.AppClient TestArgument 10 20 3 200 file`

Check results
-------------

`hadoop fs -ls /user/yarnuser/CernYarnApp/generatedNumbers`

Print results
-------------

`hadoop fs -cat /user/yarnuser/CernYarnApp/generatedNumbers/file0-200 | head`

[1]: https://github.com/Cascading/vagrant-cascading-hadoop-cluster
