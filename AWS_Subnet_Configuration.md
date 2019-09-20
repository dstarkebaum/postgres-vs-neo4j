# Troubleshooting AWS Subnet configuration

I tried to use pegasus to setup a spark cluster, and I got this error:

```
An error occurred (Unsupported) when calling the RunInstances operation: Your requested instance type (m4.large) is not supported in your requested Availability Zone (us-west-2d). Please retry your request by not specifying an Availability Zone or choosing us-west-2a, us-west-2b, us-west-2c."
```

I spent a couple hours with Upendrad trying to troubleshoot, but we were not able to solve it...

Eventually, I arrived at the following solution:

Unfortunately, when I configured my VPC subnet (see "Setting up the Network Sandbox"), I did not specify which Availability Zone to use (I chose "No Preference").  However, apparently some types of instances are only available in certain Availability Zones.

You can check which Availability Zone's hold the instance type you would like to use with this command (after `pip install --user -U awscli`):
```
aws ec2 describe-spot-price-history --region us-west-2 --instance-types m4.large --query "SpotPriceHistory[*].AvailabilityZone" --output text | tr '\t' '\n' | sort | uniq
```
This gave me `us-west-2a us-west-2b us-west-2c" but NOT "us-west-2d`
(Hooray for reddit!)
https://www.reddit.com/r/aws/comments/ar02v1/m5_availability_in_eseast1/egjuizd/



So this is how to fix it (if you run into the same problem):

Open AWS Console -> Services -> VPC
VPC Dashboard (Left side) -> Virtual Private Cloud -> Subnets

If you already went through "Setting up the Network Sandbox",
you should have a subnet with a IPv4 CIDR Block of:
`10.0.0.0/28` (Available IPv4: 11)

Check the Availability Zone.
If it says `us-west-2d`, you will need to re-create this subnet.

Make note of the VPC, route-table, and Network ACL associated with this subnet

Make sure this subnet is selected then go to Actions -> Delete Subnet

Then click on Create Subnet:
Name tag: Something descriptive, such as `<my-name>-private-subnet`
VPC: same as before
Availability Zone: Make sure to select us-west-2a, 2b, or 2c here (not "No preference")
`IPv4 CIDR block: 10.0.0.0/28` (You won't be able to assign this if you haven't deleted your previous subnet)

Click Create in the bottom right corner

Go to the VPC Dashboard -> Subnets
Click on your newly created subnet
Click on the Route Table tab -> Edit route table association
Make note of the current route table associated with this subnet (you will delete this in a moment)
Open the dropdwn menu, and choose the route table from your previous subnet

Go to the VPC Dashboard -> Route Tables
You may see several route tables.
Select the route table that is now associated with your new subnet
Click Actions -> Set Main Route Table

Click the route table that was automatically created with your new subnet
Click Actions -> Delete Route Table

Confirm that your Route Table is associated with the same VPC ID as before
It should show 10.0.0.0/26 (local) and 0.0.0.0/0 (igw-xxxxxxxxxxxx)
