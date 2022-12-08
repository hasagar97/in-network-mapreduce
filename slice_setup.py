import os

# Specify your project ID
os.environ['FABRIC_PROJECT_ID']='<project_id>'

# Set your Bastion username and private key
os.environ['FABRIC_BASTION_USERNAME']="<bastion_username>"
os.environ['FABRIC_BASTION_KEY_LOCATION']=os.environ['HOME']+'<bastion_key_location>'

# Set the keypair FABRIC will install in your slice. 
os.environ['FABRIC_SLICE_PRIVATE_KEY_FILE']=os.environ['HOME']+'<slice_key_location>'
os.environ['FABRIC_SLICE_PUBLIC_KEY_FILE']=os.environ['FABRIC_SLICE_PRIVATE_KEY_FILE']+'.pub'
# Bastion IPs
os.environ['FABRIC_BASTION_HOST'] = 'bastion-1.fabric-testbed.net'

# make sure the bastion key exists in that location!
# this cell should print True
os.path.exists(os.environ['FABRIC_BASTION_KEY_LOCATION'])

# prepare to share these with Bash so we can write the SSH config file
FABRIC_BASTION_USERNAME = os.environ['FABRIC_BASTION_USERNAME']
FABRIC_BASTION_KEY_LOCATION = os.environ['FABRIC_BASTION_KEY_LOCATION']
FABRIC_SLICE_PRIVATE_KEY_FILE = os.environ['FABRIC_SLICE_PRIVATE_KEY_FILE']
FABRIC_BASTION_HOST = os.environ['FABRIC_BASTION_HOST']



# %%bash -s "$FABRIC_BASTION_USERNAME" "$FABRIC_BASTION_KEY_LOCATION"
# 
# chmod 600 $2
# echo "Modified permissions of $2 to 600 "
# 
# export FABRIC_BASTION_SSH_CONFIG_FILE=${HOME}/work/fabric_config/ssh_config
# echo "not chainging ssh_config since it already exist"
# # echo "Host bastion-*.fabric-testbed.net"    >  ${FABRIC_BASTION_SSH_CONFIG_FILE}
# # echo "     User $1"                         >> ${FABRIC_BASTION_SSH_CONFIG_FILE}
# # echo "     IdentityFile $2"                 >> ${FABRIC_BASTION_SSH_CONFIG_FILE}
# # echo "     StrictHostKeyChecking no"        >> ${FABRIC_BASTION_SSH_CONFIG_FILE}
# # echo "     UserKnownHostsFile /dev/null"    >> ${FABRIC_BASTION_SSH_CONFIG_FILE}
# 
# cat ${FABRIC_BASTION_SSH_CONFIG_FILE}

SLICENAME=os.environ['FABRIC_BASTION_USERNAME'] + "-project-spark-setup_2"

# getting sites:
# currently using two sites because L2 network only supports 2 unique sites
# TODO find a way to set up network among multiple sites
# [master_site,slave_site]  = fablib.get_random_sites(count=2)
master_site="NCSA"
slave_site = "TACC"
print(f"Sites: {master_site}, {slave_site}")

import json
import traceback
from fabrictestbed_extensions.fablib.fablib import fablib



slice = fablib.new_slice(name=SLICENAME)


nodeSlave1  = slice.add_node(name="slave1", site = slave_site,  cores=1, ram=4, image='default_ubuntu_20')
nodeSlave2 = slice.add_node(name="slave2", site = slave_site,  cores=1, ram=4, image='default_ubuntu_20')
nodeMaster = slice.add_node(name="master", site = master_site,  image='default_ubuntu_20')

# # binding nodes to host using set site
# nodeSlave1.set_site(slave_site)
# nodeSlave2.set_site(slave_site)
# nodeMaster.set_site(master_site)

ifaceSlave1   = nodeSlave1.add_component(model="NIC_Basic", name="if_Slave1").get_interfaces()[0]
ifaceSlave2  = nodeSlave2.add_component(model="NIC_Basic", name="if_Slave2").get_interfaces()[0]
ifaceMasterR = nodeMaster.add_component(model="NIC_Basic", name="if_Master_r").get_interfaces()[0]
ifaceMasterJ = nodeMaster.add_component(model="NIC_Basic", name="if_Master_j").get_interfaces()[0]

netR = slice.add_l2network(name='net_r', interfaces=[ifaceSlave1,  ifaceMasterR])
netJ = slice.add_l2network(name='net_j', interfaces=[ ifaceSlave2, ifaceMasterJ])


slice.submit()

try:
    if fablib.get_slice(SLICENAME):
        print("You already have a slice named %s." % SLICENAME)
        slice = fablib.get_slice(name=SLICENAME)
        print(slice)
except:
    print("did not find any slice with name:",SLICENAME)



# increasing the lease end to allow more time for experiments
slice.renew("2022-12-09 21:36:54 +0000")
slice.update()
print(slice)

for node in slice.get_nodes():
    print(f"{node}")

from ipaddress import ip_address, IPv6Address
for node in slice.get_nodes():
    # print(f"{node}")
    node.upload_file('nat64.sh', 'nat64.sh')

    stdout, stderr = node.execute(f'chmod +x nat64.sh && ./nat64.sh')









"""# what ever comes next is just experimental"""

slice = fablib.new_slice(name=SLICENAME+"_exp")


nodeSlave1  = slice.add_node(name="slave1", site = slave_site,  cores=1, ram=4, image='default_ubuntu_20')
nodeSlave2 = slice.add_node(name="slave2", site = slave_site,  cores=1, ram=4, image='default_ubuntu_20')
nodeMaster = slice.add_node(name="master", site = master_site,  image='default_ubuntu_20')

# binding nodes to host using set site
nodeSalve1.set_site(slave_site)
nodeSalve2.set_site(slave_site)
nodeMaster.set_site(master_site)

ifaceSlave1   = nodeSlave1.add_component(model="NIC_Basic", name="if_Slave1").get_interfaces()[0]
ifaceSlave2  = nodeSlave2.add_component(model="NIC_Basic", name="if_Slave2").get_interfaces()[0]
ifaceMasterR = nodeMaster.add_component(model="NIC_Basic", name="if_Master_r").get_interfaces()[0]
ifaceMasterJ = nodeMaster.add_component(model="NIC_Basic", name="if_Master_j").get_interfaces()[0]

netR = slice.add_l2network(name='net_r', interfaces=[ifaceSlave1, ifaceSlave2,  ifaceMasterR])
#netJ = slice.add_l2network(name='net_j', type='L2Bridge', interfaces=[ifaceSlave1, ifaceSlave2, ifaceMasterJ])


slice.submit()

fablib.delete_slice(SLICENAME)

