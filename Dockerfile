FROM python:3.12-alpine AS build
WORKDIR /src
COPY tools/ tools/
COPY data/ data/
RUN python tools/build_report.py

FROM build AS test
COPY tests/ tests/
RUN python -m unittest discover -s tests -v

FROM python:3.12-alpine
WORKDIR /koktobe-lift
ENV BRANCH="Kok-Tobe" TOP="2"
EXPOSE 8080
COPY app/server.py .
COPY --from=test /src/out/report.json .
CMD ["python", "server.py"]
