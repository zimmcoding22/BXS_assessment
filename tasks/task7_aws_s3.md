# Task 7 — AWS S3 Integration

**Goal:** Demonstrate ability to interact with Amazon S3 for results storage.

**Requirements:**
- Add `s3_utils.py` using **boto3** that can:
  - Upload an ETL output (e.g., `orders_summary.csv`) to a bucket/prefix.
  - List objects in a bucket/prefix.
- Integrate into ETL or API flow (e.g., upload after ETL completes).
- Read credentials from environment variables; include a sample IAM policy in comments.

**Evaluation:** correct boto3 usage, secure handling (no hard-coded creds), and clear setup notes.
