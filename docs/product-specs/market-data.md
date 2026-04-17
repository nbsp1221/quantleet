# Market Data Spec

## Status

- Status: `implemented`
- Role: English current implemented-scope entry for shipped market-data utilities and their adjacent ingestion surface
- Canonical ingestion baseline: [data-ingestion.md](data-ingestion.md)

## Purpose

Provide typed market-data access and collection utilities for crypto and equity workflows.

## Current Implemented Surface

The current implemented `data` surface now includes:

- exchange-backed OHLCV utilities through the current `quantcraft.integrations.venues.ccxt` API
- the historical ingestion surface documented in [data-ingestion.md](data-ingestion.md)

## Safety

This is not a Tier A domain, but it must remain reproducible and explicit about external data contracts.
