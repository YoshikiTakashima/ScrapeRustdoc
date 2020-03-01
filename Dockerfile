# Dockerfile: Container for 
# Author: Yoshiki Takashima
# Project: Rust Compiler Testing
# Org: Carnegie Mellon CyLab

FROM ubuntu:19.10

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    	    python3 \
	    python3-pip \
	    curl \
	    wget && \
    pip3 install \
    	 beautifulsoup4 \
	 requests && \
    curl https://sh.rustup.rs -sSf \
    	 | sh -s -- --default-toolchain nightly -y && \
    echo 'source $HOME/.cargo/env' >> /root/.bashrc && \
    rm -rf /var/lib/apt/lists/*

ADD . /root

CMD [ "/bin/bash" ]