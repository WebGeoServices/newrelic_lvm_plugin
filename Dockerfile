FROM ubuntu:xenial
RUN apt-get update && apt-get install --yes --no-install-recommends build-essential devscripts python2.7 python3 debhelper\
	 python-setuptools python3-setuptools dh-python dh-systemd
RUN mkdir -p /build/package
RUN mkdir -p /packages
COPY ./ /build/package
WORKDIR /build/package
CMD dpkg-buildpackage && mv ../*.deb /packages
 
