FROM python:3.11-slim

# HF Spaces requires user with UID 1000
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app
COPY --chown=user . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

CMD ["voila", "--no-browser", "--port=7860", "--Voila.ip=0.0.0.0", "notebooks/"]
