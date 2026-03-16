# 10 — Common Mistakes and Production Lessons

## Mistake 1: Choosing models without benchmarks
Always compare on your own query set.

## Mistake 2: Ignoring token limits
Truncated chunks quietly reduce retrieval quality.

## Mistake 3: No versioning for model/preprocessing
You cannot explain regressions without versions.

## Mistake 4: Embedding raw noisy text
PDF noise, headers, and OCR artifacts pollute vectors.

## Mistake 5: No metadata filters
Retrieval drifts across wrong domain/team/date.

## Mistake 6: Re-embedding everything every run
Use change detection and upsert strategy.

## Mistake 7: Evaluating only cosine examples
Real user queries and top-k metrics are mandatory.

## Mistake 8: Single global strategy for all corpora
Different corpora need different embedding profiles.

## Mistake 9: No fallback for API failures
Add retries, dead-letter queues, and failure manifests.

## Mistake 10: No operational observability
Without metrics, quality and cost issues stay invisible.
