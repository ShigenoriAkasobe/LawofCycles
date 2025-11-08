#!/bin/bash

SCRIPT_DIR=$(cd $(dirname $0); pwd)
ROOT_DIR=${SCRIPT_DIR}/..
MAIN_DIR=${ROOT_DIR}/loc

pushd ${MAIN_DIR} > /dev/null

uv run --project ${ROOT_DIR} app.py --debug

popd > /dev/null
