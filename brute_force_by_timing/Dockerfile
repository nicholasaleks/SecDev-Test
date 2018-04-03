FROM debian:stretch-20180312
RUN apt-get update && apt-get install -y \
      python3-numpy \
      python3 \
      make \
      clang
VOLUME /mnt/src
WORKDIR /mnt/src
CMD python3 attack.py
