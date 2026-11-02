# Pinned base, standard library only, no network needed at run time.
FROM python:3.12-slim-bookworm
WORKDIR /specimen
COPY ledger.py graders.py attacks.py run.py test_suite.py task.md reproduce.sh ./
RUN chmod +x reproduce.sh
CMD ["./reproduce.sh"]
