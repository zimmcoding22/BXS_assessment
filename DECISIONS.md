# DECISIONS.md

## Overview
This document summarizes key technical decisions and trade-offs made during the BXS ETL project implementation.

---

## 1. Database Choice
- **Decision:** Used **MongoDB Atlas** instead of a local MongoDB installation.
- **Reasoning:** My local macOS setup had dependency issues with `brew` and outdated Xcode, so a managed cloud instance provided reliability and simplicity.
- **Trade-off:** Slightly slower local development due to network latency, but stable and portable for evaluators.

---

## 2. ETL Design
- **Decision:** Processed trades in **chunks (5,000 rows)** using Pandas.
- **Reasoning:** Ensures scalability and memory safety when handling large CSVs.
- **Trade-off:** Slightly higher I/O overhead versus loading a full DataFrame, but far more robust for real data volumes.

---

## 3. CI/CD and Linting
- **Decision:** Adopted GitHub Actions with **Ruff** for linting and `pytest` for testing.
- **Reasoning:** Aligns with modern Python standards and enforces code quality automatically.
- **Trade-off:** Strict lint rules required minor syntax refactoring but improved readability.

---

## 4. S3 Integration
- **Decision:** Added optional S3 upload after ETL completion using **boto3**.
- **Reasoning:** Demonstrates secure cloud integration while keeping AWS usage optional (skips if no credentials provided).
- **Trade-off:** Upload step only runs when AWS environment variables are defined — ensures safe local testing.

---

## 5. Front-End Scope
- **Decision:** Minimal **React** single-page app (no routing, no CSS framework).
- **Reasoning:** Meets the assignment’s “light version” goal — focuses on API interaction and state handling.
- **Trade-off:** No design polish, but clear logic and separation of concerns.

---

## 6. Security and Secrets
- **Decision:** All credentials are read from a `.env` file using `python-dotenv`.
- **Trade-off:** Local `.env` not committed; secure, but requires setup instructions for evaluators.
