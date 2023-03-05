# Stage 1
FROM python:3.10-buster AS compiler
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./dactylomancy /opt/venv


#Stage 2
FROM python:3.10-alpine
WORKDIR /opt/venv

COPY --from=compiler /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

# Adjust this based on where you have placed your resources folder
CMD [ "python", "main.py", "/res/config.toml"]