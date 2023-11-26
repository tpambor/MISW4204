FROM node:20-bookworm

RUN apt -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update && \
  apt install --no-install-recommends --yes \
    gnuplot \
  && apt clean && \
  rm -rf /var/lib/apt/lists/*

COPY . /monitor

RUN cd /monitor && npm install

WORKDIR /monitor

CMD node index.js
