# 09 — Cost, Latency, and Scaling Guide

## Cost Drivers

- number of chunks
- tokens per chunk
- embedding model pricing
- re-embedding frequency

## Latency Drivers

- model inference speed
- batch size strategy
- network round-trip (for APIs)
- vector store write/read latency

## Scaling Tactics

- batch embedding requests
- parallel ingestion workers
- queue-based ingestion pipeline
- cache already-embedded `chunk_id`s
- schedule full re-embeds off-peak

## Cost Control Best Practices

- deduplicate chunks before embedding
- avoid embedding boilerplate content
- maintain change detection to prevent unnecessary re-embeds
- keep separate dev/staging/prod indexes

## SLO-Oriented Monitoring

Track:

- embed throughput (chunks/min)
- failed embeds
- retry rate
- cost/day
- retrieval latency p95
