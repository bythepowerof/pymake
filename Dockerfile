FROM python:3.7-alpine3.10 as base
FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY . .
RUN pip install --install-option="--prefix=/install" .
FROM base
COPY --from=builder /install /usr/local
COPY src /app
WORKDIR /app
ENV SHELL=/bin/ash
ENTRYPOINT ["pymake", "-s"]
