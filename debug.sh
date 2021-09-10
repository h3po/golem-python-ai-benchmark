#!/bin/sh

docker build -t python-ai-benchmark image
IMG = $(gvmkit-build python-ai-benchmark:latest | grep "Output File" | cut -d" " -f5)

ya-runtime-dbg --runtime ~/.local/lib/yagna/plugins/ya-runtime-vm/ya-runtime-vm --task-package $IMG --workdir /tmp
