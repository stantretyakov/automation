#!/usr/bin/env bash
set -euo pipefail

# Helper script to deploy the EKS environment CloudFormation stack
STACK_NAME=${1:-eks-environment}
shift || true

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."

# Load configuration variables
# Expected to define CFN_PACKAGE_BUCKET for packaging nested templates
source "$ROOT_DIR/config.env"

TEMPLATE="$ROOT_DIR/cloudformation/eks-environment.yml"
PACKAGED_TEMPLATE="$ROOT_DIR/cloudformation/eks-environment-packaged.yml"

aws cloudformation package \
  --template-file "$TEMPLATE" \
  --s3-bucket "$CFN_PACKAGE_BUCKET" \
  --output-template-file "$PACKAGED_TEMPLATE"

aws cloudformation deploy \
  --stack-name "$STACK_NAME" \
  --template-file "$PACKAGED_TEMPLATE" \
  --capabilities CAPABILITY_NAMED_IAM \
  "$@"
