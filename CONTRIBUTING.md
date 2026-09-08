# Contributing

FunBall is developed publicly through [issues](https://github.com/mikolaj92/FunBall/issues), reproducible experiments and small changes. Maintainer development happens on `main`; external contributions may use pull requests.

## Before proposing a model or optimization

- State the hypothesis and acceptance criteria in an issue.
- Separate upstream claims, local measurements and speculation.
- Record model/runtime revisions, hardware, preprocessing and input provenance.
- Report false positives and missing observations, not only throughput or lock occupancy.
- Validate numerical and temporal behavior against the reference before calling an export successful.
- Do not upload private footage, credentials, model weights or datasets without redistribution permission. Use links and reproducible download instructions when appropriate.

## Tests

```sh
uv sync --locked
uv run python -m unittest discover -s tests
```

The default suite uses synthetic fixtures and OpenCV, without model downloads or GPU requirements. Keep heavyweight optional model environments isolated. Add a regression test before fixing behavior. Integration experiments requiring weights/hardware must be documented separately and must not run implicitly in default CI.

Keep programs small, queues bounded and timestamps explicit. Preserve the blue → green → yellow → red trail. Prefer no observation over an invented current position.
