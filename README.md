# Multilingual Customer Feedback & Decision-Making Pipeline

A prototype AI decision platform built to demonstrate automated ingestion, cross-market normalization, and prioritization of customer feedback for automotive operations (VW Case Study).

---

## Overview

Global automotive platforms ingest customer voice across multiple languages and regional contexts. This project prototypes a pipeline that:
1. **Ingests multilingual feedback** (Modern Standard Arabic / Gulf dialects and English).
2. **Normalizes regional issues** into a standardized component taxonomy (`INFOTAINMENT_SOFTWARE`, `CLIMATE_HVAC`, `CHASSIS_SUSPENSION`).
3. **Applies safety-weighted prioritization** to rank engineering issues over raw complaint volume alone.
4. **Routes actionable recommendations** to appropriate operational teams (OTA patches, Dealer Technical Service Bulletins, or regional HVAC calibrations).

---

## How It Works

* **Stage 1: Parsing & Dialect Extraction**  
  Extracts specific component sentiment from colloquial feedback (e.g., Arabic CarPlay disconnections and English display reboot complaints).
* **Stage 2: Semantic Mapping**  
  Collapses regional synonyms into a single vehicle subsystem.
* **Stage 3: Decision Engine**  
  Uses a weighted scoring formula:
  $$\text{Score} = (\text{Volume} + |\text{Negative Sentiment}|) \times \text{Safety Multiplier}$$
  This ensures safety-critical items (like brake vibrations) trigger immediate review even with low volume.

---

## Quickstart

### Prerequisites
* Python 3.9+
* `pydantic`

### Installation & Run
```bash
pip install pydantic
python pipeline.py
