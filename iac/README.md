# Infrastructure as Code

This directory contains infrastructure templates used to deploy the platform.

## EMR Cluster with Delta Lake

The `cloudformation/emr-cluster.yml` template provisions an Amazon EMR 6.x
cluster preconfigured for Delta Lake. Refer to the [AWS documentation](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/emr-serverless-delta.html) for details on using Delta Lake on EMR.

### Deploying with AWS CLI

You can deploy the EMR stack manually with the AWS CLI:

```bash
aws cloudformation deploy \
  --stack-name my-emr \
  --template-file iac/cloudformation/emr-cluster.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \ 
    ClusterName=my-emr \ 
    EMRReleaseLabel=emr-6.10.0 \ 
    Ec2SubnetId=subnet-123456 \ 
    JobFlowRole=EMR_EC2_DefaultRole \ 
    ServiceRole=EMR_DefaultRole
```

Alternatively, run the helper script:

```bash
bash scripts/deploy_emr.sh --parameter-overrides ClusterName=my-emr ...
```
