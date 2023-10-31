FROM python:3.11-alpine3.18

ENV GITHUB_ACCESS_TOKEN=github_access_token
ENV BACKUP_DIR=/github-backup/backup

COPY /github_backup /github-backup/github_backup
COPY requirements.txt /github-backup/requirements.txt
COPY backup.sh /github-backup/backup.sh
RUN chmod +x /github-backup/backup.sh

WORKDIR /github-backup
RUN apk add --no-cache git;\
    pip install --upgrade pip \
    && pip install -r requirements.txt; \
    chmod -R 777 /github-backup;

CMD ["sh", "/github-backup/backup.sh"]

