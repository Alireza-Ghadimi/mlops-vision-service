# mlops-vision-service

Production-minded Python 3.11 skeleton (src layout, linting, typing, tests, pre-commit, CI, Docker).

## Quickstart

```bash
# one-time
make install

# quality gates
make fix && make type && make test

# container
make docker-build
make docker-run    # prints a startup message
