# In network computation using map reduce and apache spark


## House keeping
-Add this to your jupyterlab .bashrc file to make it easier to ssh into fabric nodes and chameleon VM.

```bash
# adding the bastion key to ssh according to the abovev troubleshooting link
chmod 600 <Slice_key_location>
chmod 600 /home/fabric/work/fabric_config/hrishi_bastion_key
chmod 600 ~/work/project/chameleon_key_1.pem

eval "$(ssh-agent -s)"
ssh-add ~/work/fabric_config/hrishi_bastion_key
ssh-add  ~/work/project/chameleon_key_1.pem

# the permissions were not private enough for the slice key

```
## SSH Introduction
Run the following command for part 1
```bash 
# Now you should be able to ssh into the machine
# This next command completes Excercise 1 part 1
ssh -i <Slice_key_location> -J <fabric_username>@bastion-1.fabric-testbed.net rocky@2620:0:c80:1001:f816:3eff:fe15:7e81


```



## Installations

In all of the nodes install net-tools

```bash
sudo apt install net-tools

# get ipv6 address

 /sbin/ip -6 addr | grep inet6 | awk -F '[ \t]+|/' '{print $3}' | grep -v ^::1 | grep -v ^fe80
```


### Slave 1 - romeo
ssh -i <Slice_key_location> -J <fabric_username>@bastion-1.fabric-testbed.net ubuntu@129.114.110.119


is on ens8 of master

```bash
if1=ens7

sudo ip addr add 192.168.0.2/24 dev $if1
sudo ip route add 192.168.1.0/24 via 192.168.0.1 dev $if1 
# the anything meant for 192.168.1.[1-255] send it to $if1 via 192.168.0.1

ip addr show dev $if1
ip route show
```


### Slave 2 - juliet
ssh -i <Slice_key_location> -J <fabric_username>@bastion-1.fabric-testbed.net ubuntu@129.114.110.112


is on ens7 of master

```bash
if1=ens7
sudo ip addr add 192.168.1.2/24 dev $if1
sudo ip route add 192.168.0.0/24 via 192.168.1.1 dev $if1 
# the anything meant for 192.168.0.[1-255] send it to $if1 via 192.168.1.1.

ip addr show dev $if1
ip route show
```


### Master

ssh -i <Slice_key_location> -J <fabric_username>@bastion-1.fabric-testbed.net ubuntu@129.114.110.109


$if1 is interface of romeo - slave 1 - ens8 
$if2 is interface of juleit - slave 2 - ens7

```bash
if1=ens8
if2=ens7
sudo ip addr add 192.168.0.1/24 dev $if1
sudo ip addr add 192.168.1.1/24 dev $if2 
sudo sysctl -w net.ipv4.ip_forward=1

ip addr show dev $if1
ip addr show dev $if2
ip route show
```


### Ping from slave 2 to slave 1

```bash
ping -c 5 192.168.1.2
```


### Ping from slave 1 to slave 2

```bash
ping -c 5 192.168.0.2
```

### Enabling passwordless ssh

```

```


## Networking

- Create a slice with an interface among all  combinations of node and assign an ip to each node using the following command

```bash
ip addr add 192.168.0.2 dev eth1

```

- where ip for slave 1 can always be 192.168.1.2





# Spark Setup real one

- following this link for general setup: https://phoenixnap.com/kb/install-spark-on-ubuntu

## common for all
```bash
sudo apt update
sudo apt install default-jdk scala git -y
# Verification
java -version; javac -version; scala -version; git --version

# Download spark tar

wget https://downloads.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop2.tgz
tar xvf spark-*
sudo mv spark-3.3.1-bin-hadoop2 /opt/spark/

# setting up spark home

export SPARK_HOME=/opt/spark
echo "export SPARK_HOME=/opt/spark" >> ~/.profile
echo "export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin" >> ~/.profile
echo "export PYSPARK_PYTHON=/usr/bin/python3" >> ~/.profile

source ~/.profile
cd $SPARK_HOME
sbin/start-master.sh


```

- using the following link for cluster setup: https://aws.plainenglish.io/how-to-setup-install-an-apache-spark-3-1-1-cluster-on-ubuntu-817598b8e198

- Your installation is in `/opt/spark` the above link refers to `/usr/local/spark` as installation directory


- Slave 1 IP `192.168.0.2`
	- master IP 192.168.0.1
- Slave 2 IP `192.168.1.2`



### ip setup

```bash
sudo nano /etc/hosts
```

```bash
192.168.0.1 sp-master
192.168.0.2 sp-slave1
192.168.1.2 sp-slave2

ping -c2 sp-master 
ping -c2 sp-slave1
ping -c2 sp-slave2
```

#### on Master

```bash
sudo apt install cmdtest
sudo apt-get install openssh-server openssh-client
ssh-keygen -t rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys


# copy master key to slaves

echo ssh-rsa <The public key of master node> >> ~/.ssh/authorized_keys
```

## Making the setup a clusters

```bash
cd /opt/spark/conf
cp spark-env.sh.template spark-env.sh


sudo nano spark-env.sh

export SPARK_MASTER_HOST=192.168.0.1 export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

```

### Add slaves

```bash
sudo nano /opt/spark/conf/slaves


sp-master
sp-slave1
sp-slave2
```

### Launch cluster

```bash
/opt/spark/sbin/start-all.sh


## Stopping 
/opt/spark/sbin/stop-all.sh

```

### Chameleon

https://chameleoncloud.readthedocs.io/en/latest/

```bash
# adding the bastion key to ssh according to the abovev troubleshooting link
eval "$(ssh-agent -s)"
ssh-add  chameleon_key.pem
```



### Spark experiments

```bash
spark-shell --driver-cores 2 --driver-memory 512M  --executor-memory 512M --num-executors 3 --executor-cores 1 --conf "spark.dynamicAllocation.enabled=false"
spark-shell --driver-cores 2 --driver-memory 512M  --executor-memory 5G --num-executors 3 --executor-cores 3 --conf "spark.dynamicAllocation.enabled=false"
```

### pulling spark ui

```bash
mkdir spark-ui-pulls
cd spark-ui-pulls
wget -p localhost:8080 
zip -r spark-ui_no_job.zip localhost\:8080/

sftp -i <Slice_key_location> -J <fabric_username>@bastion-1.fabric-testbed.net ubuntu@129.114.110.109

rm -r localhost\:8080/
wget -p localhost:8080
zip -r spark-ui_one_job.zip localhost\:8080/
sftp -i <Slice_key_location> -J <fabric_username>@bastion-1.fabric-testbed.net ubuntu@129.114.110.109

```




# Chameleon spark setup

## SSH

- in your jupyter lab add the pem key using `ssh-add`

```bash
chmod 600 ~/work/project/chameleon_key_1.pem
eval "$(ssh-agent -s)"
ssh-add  ~/work/project/chameleon_key_1.pem
```

- ssh into chameleon instance `ssh cc@129.114.109.175`


## Experiments creation

```python
range_name = [[10,"10"],
[100,"100"],
[1000,"1k"],
[10000,"10k"],
[100000,"100k"],
[1000000,"1mil"]]

for i,name in range_name:
	print("""perl -E 'for($i=0;$i<{i};$i++) [say "Line $i,field2,field3,",int rand 100]' > BigBoy_{i}.csv""".format(i=i).replace("[","{").replace("]","}"))
```


```bash
perl -E 'for($i=0;$i<10;$i++) {say "Line $i,field2,field3,",int rand 100}' > BigBoy_10.csv
perl -E 'for($i=0;$i<100;$i++) {say "Line $i,field2,field3,",int rand 100}' > BigBoy_100.csv
perl -E 'for($i=0;$i<1000;$i++) {say "Line $i,field2,field3,",int rand 100}' > BigBoy_1000.csv
perl -E 'for($i=0;$i<10000;$i++) {say "Line $i,field2,field3,",int rand 100}' > BigBoy_10000.csv
perl -E 'for($i=0;$i<100000;$i++) {say "Line $i,field2,field3,",int rand 100}' > BigBoy_100000.csv
perl -E 'for($i=0;$i<1000000;$i++) {say "Line $i,field2,field3,",int rand 100}' > BigBoy_1000000.csv


# database 
wget https://www.contextures.com/SampleData.zip
```
