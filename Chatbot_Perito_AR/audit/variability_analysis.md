# Perito.AR v2.1 variability study

The official run was compared with three valid repetitions.
The evaluated pipeline, corpus and prompt were not modified.

## Aggregate results

| Run | Accuracy | Correct |
|---|---:|---:|
| Official | 90.0% | 36/40 |
| Run 01 | 90.0% | 36/40 |
| Run 02 | 90.0% | 36/40 |
| Run 03 | 90.0% | 36/40 |

## Case-level stability

- Same selected article in all four runs: 40/40.
- Cases with a variable selected article: 0/40.
- Cases whose correct/incorrect status changed: 0/40.


## Methodological notes

- The three valid repetitions reproduced the same aggregate metrics.
- Case-level stability is reported separately.
- Invalid runs created with an incorrect working directory are excluded.
- The official benchmark JSON remained preserved by SHA-256.