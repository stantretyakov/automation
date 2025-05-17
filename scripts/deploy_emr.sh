#!/usr/bin/env bash
set -euo pipefail

# Simple helper script to deploy the EMR CloudFormation stack

STACK_NAME=${1:-emr-cluster}
shift || true

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../iac/cloudformation/emr-cluster.yml"

aws cloudformation deploy \
  --stack-name "$STACK_NAME" \
  --template-file "$TEMPLATE" \
  --capabilities CAPABILITY_NAMED_IAM \
  "$@"

