# Technical Analysis Signal Scanner

A personal-use technical analysis (TA) signal scanner that assists a casual long-hold retail investor in making portfolio allocation posture decisions across a small watchlist of tickers. The application computes daily-close-based indicators (SMA-50/200, RSI-14, HV-20, 52-week range), scores each ticker on a -5 to +5 posture scale, and surfaces results through a local browser-based UI.

Stack: Python 3.12, FastAPI, SQLAlchemy, SQLite, Jinja2, vanilla JS, Tailwind CSS, Plotly.js. Designed for low-friction future migration to AWS serverless.

## Status

Setting up v1. Repository scaffolding, dependency configuration, and architecture documentation are in place; application code is being added incrementally. See `docs/architecture-design.md` for the full system design.

## Prerequisites

- Python 3.12
- Anaconda or Miniconda
- Git

## Setup
git clone git@github.com:jpnittanyhoosier/ta-signal-scanner.git
cd ta-signal-scanner
conda create -n ta-scanner python=3.12
conda activate ta-scanner
pip install -e ".[dev]"

## Development

Once the environment is set up and activated:

- `pytest` - run the test suite
- `ruff check .` - lint
- `ruff format .` - format
- `mypy` - type-check

## Documentation

- `docs/architecture-design.md` - system design, indicator specifications, posture scoring rules, AWS future-state mapping
- `docs/repository-structure.md` - annotated repository layout
- `docs/decisions/` - Architecture Decision Records (ADRs)

## License

See [LICENSE](LICENSE).