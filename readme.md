# golem-python-ai-benchmark

My first attempt at making a golem requestor. Runs an AI inference benchmark on the provider node using [ai-benchmark](https://pypi.org/project/ai-benchmark/)

## image
The container is a 926MB python:3.8-slim image with the required tensorflow packages on top. After packing with gvmkit-build, it is a 294MB gvmi image.

```
cd image
docker build -t python-ai-benchmark .
gvmkit-build python-ai-benchmark:latest
```

running with docker:
```
docker run --rm -it --entrypoint /run-bench.py - $(pwd)/out:/golem/output python-ai-benchmark
```

running with ya-runtime-dbg (use [debug.sh](./debug.sh))
```
docker build -t python-ai-benchmark image
IMG = $(gvmkit-build python-ai-benchmark:latest | grep "Output File" | cut -d" " -f5)

ya-runtime-dbg --runtime ~/.local/lib/yagna/plugins/ya-runtime-vm/ya-runtime-vm --task-package $IMG --workdir /tmp
```

## requestor
The requestor code currently is just code copied from the yapapi examples and does not do any calculations for the proper GLM budget. Make sure to adjust it before using.

```
cd requestor
python python-ai-benchmark.py --subnet-tag devnet-beta.2
```