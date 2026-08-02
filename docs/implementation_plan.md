# Implementation Plan: Message Notification Router

## Goal
Build a modular Python pipeline that reads the provided dataset, understands message content and context, applies safety and personalization logic, and produces routing predictions for every message.

## Proposed architecture

### 1. Data Loader
Responsibilities:
- Load messages.csv
- Load users.csv
- Load groups.csv
- Load group_members.csv
- Load business_accounts.csv
- Load message_history.csv
- Load message_events.csv
- Load media metadata

Planned module:
- code/app/data/loader.py

### 2. Multimodal Processor
Responsibilities:
- Process text messages
- Run OCR or image understanding for image attachments
- Transcribe voice notes

Planned modules:
- code/app/multimodal/text_processor.py
- code/app/multimodal/image_processor.py
- code/app/multimodal/voice_processor.py

### 3. Language Understanding
Responsibilities:
- Detect the primary language of the message
- Handle mixed-language content
- Support multilingual reasoning for routing decisions

Planned module:
- code/app/language/language_processor.py

### 4. Safety Engine
Responsibilities:
- Detect phishing attempts
- Detect scams and fraud-like content
- Detect suspicious links or domains
- Flag unsafe, manipulative, or coercive content

Planned module:
- code/app/safety/safety_engine.py

### 5. Critical Event Detector
Responsibilities:
- Detect high-priority situations such as:
  - exam changes
  - interview changes
  - meeting changes
  - venue changes
  - deadlines
  - emergencies
  - payment reminders

These should receive high priority even when the sender is unknown.

Planned module:
- code/app/events/critical_event_detector.py

### 6. Personalization Engine
Responsibilities:
- Use user profile information
- Model user interests and preferences
- Consider important chats and strong relationships
- Use prior opens, replies, dismissals, and reports
- Use group relationship and business history

Planned module:
- code/app/personalization/personalization_engine.py

### 7. Decision Engine
Responsibilities:
- Produce the final routing action: notify, digest, or mute
- Generate message_type, reason, confidence, and evidence_message_ids

Planned module:
- code/app/decision/decision_engine.py

### 8. Evaluation Workflow
Responsibilities:
- Run the pipeline on sample rows
- Compare predictions to provided examples
- Track confidence and evidence quality
- Produce output.csv in the required format

Planned module:
- code/app/evaluation/evaluator.py

## Suggested execution flow
1. Load all raw datasets.
2. Enrich each incoming message with user, group, business, and history context.
3. Run multimodal and language processing.
4. Apply safety and critical-event rules.
5. Apply personalization logic.
6. Let the decision engine produce the final labels.
7. Write output.csv and review performance with the sample rows.

## Folder structure
- code/app/data/
- code/app/multimodal/
- code/app/language/
- code/app/safety/
- code/app/events/
- code/app/personalization/
- code/app/decision/
- code/app/evaluation/
- code/app/utils/

## Implementation order
1. Create the data loading layer.
2. Add the shared data model and utility helpers.
3. Implement text and media processing hooks.
4. Add safety and critical-event detection.
5. Add personalization and final routing logic.
6. Add evaluation and output generation.

## Notes
This document defines the architecture and structure only. The actual routing logic and model integration will be added in later steps.
