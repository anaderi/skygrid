YARN Approach
=============

In this folder there are some files, which implement the «[YARN](http://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/YARN.html) approach». The code is mostly based on the HortonWorks labs [sources](https://github.com/HortonworksUniversity/YARN_Rev1/tree/master/labs/solutions).

Building a JAR
--------------
Clone this repository to `REPO_DIR`.

    $ cd REPO_DIR/YARN
    $ mvn package

As a result you have a JAR created at `REPO_DIR/YARN/target/YarnTestClient-1.0.jar`.

Running the Application
----------------------
The [vagrant](http://www.vagrantup.com/)-based virtual machine from [here](https://github.com/Cascading/vagrant-cascading-hadoop-cluster#single-node-setup) was used for Yarn . After you start a virtual machine, you need to make YarnConfigs visible to a client. As I start my client on my host machine, I execute the following:

    $ cd ~/vagrant-cascading-hadoop-cluster/single-node
    $ vagrant ssh
    $ cd /opt/hadoop-2.3.0/etc/hadoop/
    $ mkdir /vagrant/configs
    $ cp * /vagrant/configs
    $ exit

 Now you are able to communicate with YARN without any extra setup, just by appending `~/vagrant-cascading-hadoop-cluster/single-node/configs` to `CLASSPATH`.

The next step is providing all of the required JARs for Hadoop client. My solution is:

    $ cd REPO_DIR/YARN
    $ mvn dependency:copy-dependencies

You can ensure, that all dependencies are copied to `REPO_DIR/YARN/target/dependency`.

Then run the application:

    $ cd REPO_DIR/YARN
    $ java -cp "~/vagrant-cascading-hadoop-cluster/single-node/configs/:target/YarnTestClient-1.0.jar:target/dependency/*" ru.yandex.cern.yarntest.AppClient TestArgument
    2014-07-13 13:25:33.086 java[8678:f07] Unable to load realm mapping info from SCDynamicStore
    14/07/13 13:25:33 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    14/07/13 13:25:33 INFO client.RMProxy: Connecting to ResourceManager at master.local/192.168.7.10:8032
    14/07/13 13:25:34 INFO yarntest.AppClient: Applicatoin ID = application_1405190480286_0004
    14/07/13 13:25:34 INFO yarntest.AppClient: Max memory = 8192 and max vcores = 32
    14/07/13 13:25:34 INFO yarntest.AppClient: Number of NodeManagers = 1
    14/07/13 13:25:34 INFO yarntest.AppClient: Node ID = master.local:34277, address = master.local:8042, containers = 0
    14/07/13 13:25:34 INFO yarntest.AppClient: Available queue: default with capacity 1.0 to 1.0
    14/07/13 13:25:34 INFO yarntest.AppClient: AMJAR environment variable is set to hdfs://master.local:9000/user/stromsund/CernYarnApp/4/app.jar
    14/07/13 13:25:34 INFO yarntest.AppClient: Command to execute ApplicationMaster = $JAVA_HOME/bin/java ru.yandex.cern.yarntest.ApplicationMaster TestArgument 1><LOG_DIR>/AM.stdout 2><LOG_DIR>/AM.stderr 
    14/07/13 13:25:34 INFO impl.YarnClientImpl: Submitted application application_1405190480286_0004

You may check the status of your task execution at (http://master.local:8088/cluster). When the task is completed, you will see 5 files containing prime numbers each in HDFS.

    $ cd ~/vagrant-cascading-hadoop-cluster/single-node
    $ vagrant ssh
    $ vagrant@master:~$ hadoop fs -ls /user/YOUR_USER/CernYarnApp/results/
    14/07/13 09:35:04 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    Found 5 items
    -rw-r--r--   1 yarn supergroup       2857 2014-07-13 09:25 /user/stromsund/CernYarnApp/results/Res0-1000
    -rw-r--r--   1 yarn supergroup       2430 2014-07-13 09:25 /user/stromsund/CernYarnApp/results/Res1000-2000
    -rw-r--r--   1 yarn supergroup       2286 2014-07-13 09:25 /user/stromsund/CernYarnApp/results/Res2000-3000
    -rw-r--r--   1 yarn supergroup       2160 2014-07-13 09:25 /user/stromsund/CernYarnApp/results/Res3000-4000
    -rw-r--r--   1 yarn supergroup       2142 2014-07-13 09:25 /user/stromsund/CernYarnApp/results/Res4000-5000
    $ hadoop fs -cat /user/YOUR_USER/CernYarnApp/results/Res3000-4000 | head
    14/07/13 09:36:40 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    Found prime: 3001
    Found prime: 3011
    Found prime: 3019
    Found prime: 3023
    Found prime: 3037
    Found prime: 3041
    Found prime: 3049
    Found prime: 3061
    Found prime: 3067
    Found prime: 3079
    $ exit

