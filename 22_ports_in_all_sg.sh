#!/bin/bash

# Specify the region
REGION="us-east-1"

# Output file
OUTPUT_FILE="22ports.txt"

# Clear the output file if it already exists
> $OUTPUT_FILE

# Get the list of all security groups with their IpPermissions
SECURITY_GROUPS=$(aws ec2 describe-security-groups --region $REGION --query 'SecurityGroups[*]' --output json)

# Process the security groups to find port 22 permissions and format the output
echo "$SECURITY_GROUPS" | jq -r '
  .[] |
  . as $sg |
  .IpPermissions[]? |
  select(.FromPort == 22 and .ToPort == 22) |
  .IpRanges[]? |
  "\($sg.GroupName) - \($sg.GroupId) - port (22) - \(.CidrIp) - \(.Description // "null")"
' | while read -r line; do
  OUTPUT="$REGION - $line"
  echo "$OUTPUT" | tee -a $OUTPUT_FILE
done
