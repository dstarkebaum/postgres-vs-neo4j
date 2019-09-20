# Setting up Pegasus

Hopefully you have already completed the "19C AWS Insight Account Setup"
Specifically, you have created your own IAM User.
You will need the CSV file containing your AWS Access Keys for that IAM User

### Setting Envinronment variables:
In the Terminal, open up your .bashrc file
```
nano .bashrc
```
scroll down to the bottom, and add the following lines:

```
# Setup AWS environmental variables for pegasus
export AWS_ACCESS_KEY_ID=<copy the access key id here>
export AWS_SECRET_ACCESS_KEY=<copy your secret access key here>
export AWS_DEFAULT_REGION=us-west-2
export REM_USER=ubuntu
export PEGASUS_HOME=~/pegasus/
export PATH=$PEGASUS_HOME:$PATH
```


Note: While you are here in your .bashrc, I recommend the following changes:
Look for the variable HISTSIZE, and set it to some very large number
```
HISTSIZE=10000 (or -1 for infinite)
HISTFILESIZE=20000 (or -1 for infinite)
```
This will keep track of all commands that you enter into your terminal.
HISTSIZE refers to the log you can access by typing "history" in the terminal.
HISTFILESIZE refers to your ".bash_history" file.
This can be very useful to remember what you have done before!
You can also re-enter previous commands py pressing the up key

One more thing.  Add this line to your .bashrc too:
```
export HISTTIMEFORMAT="%d/%m/%y %T "
```
This also records the day/month/year hh:mm:ss when each command was accessed!




Once you have setup your envinronment variables, you can setup a pegasus ".yml" configuration file.
I used `pegasus/examples/spark/master.yml`
first copy to your own directory:
```
cp pegasus/examples/spark/master.yml pegasus/<your-name>/master.yml
```
Next, you need to find out which subnet_id and security_group_id to use:
```
peg aws subnets
```
Locate which subnet you will use (probably the one you setup already for your VPC (with IPv4: 10.0.0.0/28)
Make sure it says AZ: us-west-2a, 2c, or 2c (NOT 2d!)
Record its subnet_id and VPC_ID

Then find your security group ID:
```
peg aws security-groups
```
Locate the VPC_ID from your subnet, and record the SG_ID

Also, make sure you have a private/pulic SSH key.
(I keep my in .ssh/<my name>-IAM-keypair.pem)


Edit your .yml configuration file with:
```
nano pegasus/<your-name>/master.yml

purchase_type: on_demand
subnet_id:<put your subnet id here>
num_instances: 1
key_name:<your name>-IAM-keypair (NOTE: do not put .pem here)
security_group_ids:<put your security group id here>
instance_type: m4.large (NOTE: you can adjust the size as needed here)
tag_name:<your name>-spark
vol_size: 100
role: master
use_eips: true
```
Then try:
```
peg validate pegasus/<your-name>/master.yml
```
If that works, then try:
```
peg up pegasus/<your-name>/master.yml
```

it should load for a bit, then create your instance!  (Congrats!)

Make sure to login to your AWS console and terminate this instance if you are not going to continue using it!
