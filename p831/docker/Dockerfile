# Computer algebra for the exact Case A decision (caseA_exact.py).
# Official Ubuntu image, packages from Ubuntu's own archive only.
#
#   docker build -t erdos831-cas docker
#   docker run -d --name cas831 --cpus 7 -v "<path to p831>:/work" erdos831-cas sleep infinity
FROM ubuntu:24.04
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends singular msolve \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
