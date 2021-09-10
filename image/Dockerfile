FROM python:3.8-slim

RUN \
  pip install --upgrade --no-cache-dir pip && \
  pip install --no-cache-dir tensorflow-cpu==2.2.0 ai-benchmark==0.1.2

COPY run-bench.py /

RUN \
  chmod +x /usr/local/bin/ai-benchmark /run-bench.py

VOLUME /golem/output

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/usr/local/bin/ai-benchmark"]
