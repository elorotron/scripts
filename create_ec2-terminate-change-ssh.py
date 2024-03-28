import boto3
import paramiko
import sys
import os
#------------variables-----------------------
#for ubuntu
#export AWS_ACCESS_KEY_ID="access_key"
#export AWS_SECRET_ACCESS_KEY="secret_key"

#----------for windows---------------
#set AWS_ACCESS_KEY_ID="access_key"
#set AWS_SECRET_ACCESS_KEY="secret_key"
#-------------------------------------------------

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

aws_region = 'eu-central-1'
public_key_path = 'C:\\Users\\Susel\\.ssh\\id_rsa.pub'
private_key_path = 'C:\\Users\\Susel\\.ssh\\id_rsa'

#-------------------------------------------------
with open(public_key_path, 'r') as file:
    public_key_content = file.read().strip()

ec2 = boto3.client('ec2', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)

instance_id = None
public_ip = None


def create_instance():
    response = ec2.run_instances(
        ImageId='ami-06dd92ecc74fdfb36',  # ubuntu frankfurt
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=key_name, #ssh key
        SecurityGroupIds=['sg-02ce89342b7fa7534'], #default SG
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'susel'
                    }
                ]
            }
        ]
    )

    global instance_id
    instance_id = response['Instances'][0]['InstanceId']
    ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])

    instance_details = ec2.describe_instances(InstanceIds=[instance_id])
    global public_ip
    public_ip = instance_details['Reservations'][0]['Instances'][0].get('PublicIpAddress', 'N/A')

    instance_type = instance_details['Reservations'][0]['Instances'][0]['InstanceType']
    private_ip = instance_details['Reservations'][0]['Instances'][0]['PrivateIpAddress']
    os_type = instance_details['Reservations'][0]['Instances'][0].get('PlatformDetails', 'Linux')

    print(f'Launched EC2 instance with ID: {instance_id}')
    print(f'Instance Type: {instance_type}')
    print(f'Public IP: {public_ip}')
    print(f'Private IP: {private_ip}')
    print(f'Operating System: {os_type}')

def ssh_connect():
    key = paramiko.RSAKey.from_private_key_file(private_key_path)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(public_ip, username='ubuntu', pkey=key)
        print("SSH connection established.")
        ssh.close()
    except Exception as e:
        print(f"SSH connection failed: {str(e)}")

def terminate_instance():
    global instance_id
    if instance_id:
        ec2.terminate_instances(InstanceIds=[instance_id])
        print(f'Instance {instance_id} terminated successfully.')
        if public_ip:
            print(f'Public IP: {public_ip}')
        ec2.delete_key_pair(KeyName=key_name)
        print(f'Key pair {key_name} deleted.')
    else:
        print('No instance running to terminate.')

while True:
    print("Choose an option:")
    print("1 - Create instance and output IP, OS, etc.")
    print("2 - Try to connect via SSH to the instance.")
    print("3 - Terminate the instance.")
    print("4 - Exit the script.")
    choice = input("Enter your choice: ")

    if choice == '1':
        key_name = 'susel'
        ec2.import_key_pair(KeyName=key_name, PublicKeyMaterial=public_key_content)
        print(f'SSH key imported with name: {key_name}')
        create_instance()
    elif choice == '2':
        if public_ip:
            ssh_connect()
        else:
            print('No instance available to connect.')
    elif choice == '3':
        terminate_instance()
    elif choice == '4':
        print("Exiting the script.")
        sys.exit()
    else:
        print("Invalid choice. Please try again.")
