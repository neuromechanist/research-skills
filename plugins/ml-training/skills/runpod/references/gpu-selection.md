# GPU Selection, Stock, And The Scale Ladder

Pick the card from the workload's binding constraint, not from the top of the price list. Most
benchmark and evaluation work is bound by aggregate VRAM, not by tensor throughput, and that
distinction is worth several dollars an hour.

## Check stock before planning around a GPU type

Availability is per (GPU type, GPU count). A type with plenty of 1x stock may have no 2x
single-host capacity at all, and a create call against an unavailable combination fails with
`There are no instances currently available`.

The REST API has no `gputypes` path. Stock and price come from GraphQL:

```bash
curl -s https://api.runpod.io/graphql \
  -H "Authorization: Bearer $RUNPOD_API_KEY" -H 'Content-Type: application/json' \
  -d '{"query":"{ gpuTypes { id securePrice lowestPrice(input:{gpuCount:2, secureCloud:true}) { stockStatus uninterruptablePrice } } }"}'
```

Change `gpuCount` to the count actually wanted, and re-run before every session. `stockStatus`
is the field that decides whether the plan survives contact with the fleet.

## The pricing ladder

Observed on secure cloud, 2026-08-12. Prices move; re-query rather than trusting this table, and
treat it as a shape argument rather than a quote.

| Configuration | Aggregate VRAM | Hourly | Notes |
|---|---|---|---|
| 1x A40 | 48 GB | $0.44 | Budget pick for accuracy-only grids |
| 2x A40 | 96 GB | $0.88 | Layer-split a 30B model, measured 31 tok/s decode |
| 2x A100-SXM | 160 GB | $3.18 | More VRAM than an H100 **and** cheaper |
| 1x H100 | 80 GB | $3.29 | Half the VRAM of the 2x A100 pod, higher price |
| 1x H200 | 141 GB | $4.59 | Most VRAM on one card, zero sharding plumbing |

Two conclusions worth internalizing:

- **The pricing ladder is not monotonic in VRAM.** 2x A100-SXM at $3.18/hr beats 1x H100 at
  $3.29/hr on both aggregate VRAM (160 vs 80 GB) and price. If the workload can shard, the
  newest single card is often the wrong buy.
- **Accuracy-only work does not need a flagship.** When the metric is correctness rather than
  throughput, A40-class cards at $0.44/hr per 48 GB are the cheapest way to buy VRAM. Reserve
  H100/H200 rates for runs where wall-clock is the constraint.

## Choosing a configuration

1. Compute the memory the workload actually needs: weights, plus activation and cache overhead,
   plus a working margin. This is usually the binding number.
2. If the workload is accuracy-bound and latency-tolerant, buy VRAM at the cheapest rate per GB.
3. If it is wall-clock-bound, compare hourly rate against realized throughput, not against peak
   specification numbers. The 2x A40 measurement above (31 tok/s decode on a layer-split 30B
   model at $0.88/hr) is the kind of number worth collecting once and reusing.
4. Confirm stock at that exact (type, count) before writing any scripts around it.

## The scale ladder for training a large model

When a training or distillation run does not fit one card, climb this ladder one rung at a time
and stop at the first rung that works. Every rung above the first adds engineering surface, and
the higher rungs add more of it than they add capability.

1. **Shrink the problem so one card is enough.** Precompute teacher or reference logits to disk
   ahead of time, then train against the cached tensors. An 80 GB card carries the run with no
   distribution code at all. This rung is almost always underrated.
2. **Two GPUs in one pod, device sharding.** `gpuCount: 2` in the same create call, one host, one
   `ssh` target, no cluster networking. Device-map or layer-split sharding stays inside the
   framework.
3. **One bigger card.** An H200 at 141 GB buys zero plumbing at a higher hourly rate. When
   engineering time is the scarce resource, this is often cheaper than rung 2.
4. **Multi-node instant cluster.** Last resort. It adds collective-communication setup, launcher
   configuration, and a whole class of failure modes that do not exist below this line. Only
   climb here when a single host provably cannot hold the run.

Single-host multi-GPU (rung 2) is provisioned with `gpuCount: N` in the same pod create call
that a single-GPU pod uses. There is no separate cluster concept until rung 4.

## Sizing the rest of the pod

- `containerDiskInGb`: two copies of the model, plus caches, logs, and outputs. Peak usage runs
  well above the final artifact size because downloads are cached and then materialized.
- `allowedCudaVersions`: pin away from any host pool with a known container-start bug, and build
  the image on a base that runs across the whole filtered pool.
- `cloudType`: secure cloud for anything with a deadline or a result worth keeping.
- `ports`: `["22/tcp"]`, since the workflow drives everything over `ssh`.
