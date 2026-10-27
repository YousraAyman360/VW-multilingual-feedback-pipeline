# Multilingual Customer Feedback & Decision-Making Pipeline

A prototype AI decision platform built to demonstrate automated ingestion, cross-market normalization, and prioritization of customer feedback for automotive operations (Case Study inspired by Volkswagen).

---

## Overview

Global automotive platforms ingest customer voice across multiple languages and regional contexts. This project prototypes a pipeline that:
1. **Ingests multilingual feedback** (Modern Standard Arabic / regional dialects and English).
2. **Normalizes regional issues** into a standardized Volkswagen component taxonomy (`INFOTAINMENT_MIB_SOFTWARE`, `CLIMATE_HVAC`, `CHASSIS_SUSPENSION`).
3. **Applies safety-weighted prioritization** to rank engineering issues over raw complaint volume alone.
4. **Routes actionable recommendations** directly to operational channels (OTA patches for MIB/ID.Software, Dealer Technical Service Bulletins, or Climatronic regional thermal calibrations).

---

## How It Works

* **Stage 1: Parsing & Dialect Extraction**  
  Extracts specific component sentiment from colloquial feedback (e.g., Arabic CarPlay disconnections and English MIB screen reboot complaints).
* **Stage 2: Semantic Mapping**  
  Collapses regional phrasing into standardized Volkswagen subsystems.
* **Stage 3: Decision Engine**  
  Uses a weighted scoring formula:
  $$\text{Score} = (\text{Volume} + |\text{Negative Sentiment}|) \times \text{Safety Multiplier}$$
  This ensures safety-critical items (like brake vibrations) trigger immediate review even with low volume.

---

## Quickstart

### Prerequisites
* Python 3.9+
* `openai` and `pydantic`

### Installation & Run
```bash
pip install openai pydantic
export OPENAI_API_KEY="your-api-key-here"
python pipeline.py
