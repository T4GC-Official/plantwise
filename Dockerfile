FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY src /app/src
COPY generate_reports.py /app/generate_reports.py
COPY reports/index.html /app/reports/index.html
COPY reports/styles.css /app/reports/styles.css
COPY reports/viewer.js /app/reports/viewer.js
COPY reports/baseline/auc_and_contributions.csv /app/reports/baseline/auc_and_contributions.csv
COPY reports/20260318_104449/auc_and_contributions.csv /app/reports/20260318_104449/auc_and_contributions.csv
COPY reports/20260318_104449/report_summary.json /app/reports/20260318_104449/report_summary.json
COPY reports/20260330_095938/auc_and_contributions.csv /app/reports/20260330_095938/auc_and_contributions.csv
COPY reports/20260330_095938/report_summary.json /app/reports/20260330_095938/report_summary.json
COPY Final_Species.csv /app/Final_Species.csv
COPY maxent.jar /app/maxent.jar
COPY final_attributes /app/final_attributes
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 5050

ENTRYPOINT ["/app/docker-entrypoint.sh"]
