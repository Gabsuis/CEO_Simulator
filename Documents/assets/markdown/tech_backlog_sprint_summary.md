# Mentalyc Engineering Status Report Sprints 1 2

*Source: Mentalyc_Engineering_Status_Report_Sprints_1_2.docx*

## 🛠️ Mentalyc Engineering Status Report – Sprints 1 & 2

📅 Timeframe Covered:
Sprint 1: Sept 1–Sept 15
Sprint 2: Sept 16–Sept 30

📍 Prepared by: Engineering Team
📬 To: Mentalyc CEO, Product Team, Design Partners

### ✅ Summary

Sprints 1 and 2 were focused on foundational capabilities for the MVP, including session capture, transcription, and dual-mode note generation. While early infrastructure and proof-of-concept pieces were validated, multiple core stories in Epic 1 and Epic 2 were either partially completed or missed, impacting short-term feature availability and MVP pilot timeline.

### ⚙️ Sprint Highlights

- ✅ What We Achieved
- Developed cross-platform session recording on web and mobile (Epic 1)

- Completed integration of Whisper STT engine with filler cleanup and diarization

- Built initial framework for bilingual UI shell (EN/HE toggle)

- Validated first version of per-patient notebook backend schema

- Completed setup of encrypted note storage (in line with HIPAA/GDPR)

- 🚧 What Was Missed or Delayed
- Only 2 of 4 user stories in Epic 1 were fully completed

- In Epic 2 (Dual-Mode Notes), 2 key features were partially implemented and need more UI/UX refinement

- Several missed stories were due to underestimated integration time and speech-to-text post-processing complexity

### 📊 Performance Metrics


🟡 Burndown shows +41 hrs of carryover into Sprint 3

### 📌 Risks & Blockers

- ❗ STT post-processing (punctuation, filler removal) slower than projected

- ❗ Custom note-format toggle (SOAP vs narrative) requires more flexible state handling

- ⚠️ Early UI interactions (notes editor, bilingual support) lack polish and need design attention

- ⚠️ Transcription quality with accented English needs tuning

### 🧪 Learnings & Improvements

- Estimation calibration needed: Engineering underestimated complexity of real-time audio processing

- Integration → Feature Delay: Need to stub external services sooner to parallelize work

- Design collaboration: UI expectations must be clarified earlier to prevent rework

### 🗺️ Next Steps (Sprint 3+ Recovery Plan)

- Carry over missed stories from Epics 1 and 2 into Sprint 3, prioritizing:
  - Note format toggle UI
  - Full dictation-to-final-note flow

- Increase test coverage for STT edge cases

- Begin Insight Extraction layer (Epic 3) in parallel to avoid further delay to MVP

### 📣 Ask for the Company

- 🧪 Design Team: Confirm final expected UX for dual-mode notes

- 🧑‍⚕️ Clinical Advisors: Help validate SOAP vs. narrative use cases in sessions

- 🧭 Product: Approve recovery story prioritization for Sprint 3


Prepared by:
Mentalyc Engineering Team
📍 Status as of Sprint 2 close (Sept 30)


## Tables

### Table 1

| Metric                 | Sprint 1   | Sprint 2   | Note   |
|:-----------------------|:-----------|:-----------|:-------|
| Planned Velocity (hrs) | 45         | 45         |        |
| Actual Velocity (hrs)  | 28.5       | 32.0       |        |
| Completion Rate (%)    | 63%        | 71%        |        |
| Key Stories Completed  | 4 / 7      | 5 / 7      |        |

