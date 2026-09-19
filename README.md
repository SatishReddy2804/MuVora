# MuVora: Multilingual Cinema Review Intelligence & Translation Platform

<div align="center">

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![React 18](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5.1-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Vercel Ready](https://img.shields.io/badge/Vercel-SPA_Ready-000000?style=for-the-badge&logo=vercel&logoColor=white)

**An intelligent, production-quality multilingual cinema review intelligence platform featuring Bidirectional LSTM neural classification, dynamic cinema aspect sentiment analysis, and Google-Translate-style multilingual translation with voice input and audio pronunciation.**

</div>

---

## 📑 Table of Contents

- [Overview](#overview)
- [Why MuVora](#why-muvora)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Model Training](#2-model-training)
  - [3. Frontend Setup](#3-frontend-setup)
- [Configuration & Environment Variables](#configuration--environment-variables)
- [Usage Workflows](#usage-workflows)
- [API Reference](#api-reference)
- [Vercel Deployment Guide](#vercel-deployment-guide)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Overview

Modern film audiences express opinions across native scripts (Telugu, Hindi, Tamil) and Romanized transliterations (e.g., *“cinema chala bagundhi”*, *“movie bahut accha hai”*). Conventional sentiment demos typically exhibit two core weaknesses:
1. **Categorical Word ID Feeding (~50% Accuracy)**: Passing raw integer word indices directly into dense layers without learned embeddings treats arbitrary token IDs as numerical features, resulting in unstable predictions.
2. **Monolingual Limitation**: Models trained on English benchmarks fail on Indic languages or code-mixed Romanized reviews without script and language representation separation.

**MuVora** solves both challenges by combining:
- A **Bidirectional LSTM neural network** with a learned dense Embedding layer ({,}000 \to 128$) trained on the Stanford IMDB benchmark (achieving **86.5% accuracy**).
- A **multi-stage Unicode script and transliteration detection engine** that separates physical writing script from semantic language.
- A **resilient multi-provider translation pipeline** (Google GTX + MyMemory lawful public fallback + clean offline dictionary fallback) that eliminates mock prefix tags.
- A **meaning-based cinema intelligence engine** providing evidence-backed aspect-level sentiment (Acting, Story, Direction, Screenplay, Music, Visuals, Overall Experience) and multi-part narrative synthesis.

---

## Why MuVora

| Traditional Sentiment Demos | MuVora Intelligence Platform |
| :--- | :--- |
| Feeds raw word IDs into linear layers (~50% accuracy) | Learned Dense Embedding ({,}000 \to 128$) + BiLSTM (86.5% accuracy) |
| Fails on Romanized Telugu/Hindi | Multi-stage script, transliteration & code-mixing detector |
| Forces arbitrary binary label on keyboard smash (sdfghjk) | Shannon entropy & consonant cluster Input Quality Guard |
| Binary positive/negative output only | Aspect-based sentiment with direct quoted evidence |
| Monolingual English only | 17 supported languages with voice input & TTS pronunciation |
| Crashes on translation rate limits | Multi-provider cascade (Google GTX + MyMemory + offline) |

---

## Key Features

### 1. Cinema Review Intelligence & Aspect Analysis
- **BiLSTM Neural Classifier**: Deep recurrent architecture capturing long-range syntactic dependencies and negation handling (*\"not good\"*, *\"never boring\"*).
- **Dynamic Aspect Extraction**: Identifies sentiments and extracts direct quotes across:
  - Acting & Cast Performance
  - Story & Plot Narrative
  - Direction & Filmmaking Craft
  - Screenplay & Pacing
  - Music & Soundtrack (BGM)
  - Visuals & Cinematography
  - Overall Cinematic Experience
- **Multi-Part Narrative Synthesis**:
  - **Executive Summary**: Localized summary in the user's selected display language.
  - **Evidence-Backed Narrative**: Attributing specific expressive phrases and neural probabilities.
  - **Reviewer Tone & Nuance**: Tone intensity detection (*Enthusiastic*, *Critical*, *Balanced*).
  - **Theatrical Recommendation Badge**: Visual guidance (*Highly Recommended*, *Skip*, *Mixed Appeal*).
- **Input Quality Guard**: Shannon entropy and consonant cluster filters reject random strings and gibberish with status: insufficient_input.

### 2. Google-Translate-Style Translation Workspace
- **Zero Mock Prefixes**: Clean, pure translations without debug labels or dummy tags.
- **Voice Dictation (Speech-to-Text)**: Browser Web Speech API mic button for hands-free review input in English, Telugu, Hindi, and Tamil.
- **Audio Pronunciation (Text-to-Speech)**: Audio listen button for original text and translated output.
- **Multi-Target Translations**: Simultaneous translation into multiple target languages with one-click copy.
- **One-Click Export**: Download translations as .txt files.
- **Interactive Language Swapping & Live Character Counters**.

---

## System Architecture

`mermaid
flowchart TD
    User([User / Browser]) <--> FE[React 18 + Vite SPA]
    FE <--> API[FastAPI Gateway /api]
    
    subgraph Backend_Services [Inference & NLP Pipeline]
        API --> QD[Input Quality Guard]
        API --> LD[Multi-Stage Script & Transliteration Detector]
        API --> TS[Multi-Provider Translation Cascade]
        API --> AA[Aspect Sentiment Engine]
        API --> BiLSTM[BiLSTM Neural Classifier]
    end

    TS --> GTX[Direct Google GTX API]
    TS --> MM[MyMemory Public API]
    TS --> Dict[Clean Offline Dictionary]
`

---

## Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18.2, TypeScript 5.2, Vite 5.1 | Responsive SPA user interface |
| **Styling** | TailwindCSS 3.4, Lucide React, Framer Motion | Glassmorphism UI & animated widgets |
| **Backend** | FastAPI 0.110+, Uvicorn ASGI, Pydantic v2 | High-performance asynchronous API gateway |
| **Machine Learning** | TensorFlow 2.15+, Keras 3.0, NumPy, Scikit-learn | BiLSTM neural classifier & preprocessing |
| **Multilingual NLP** | Custom Script Detector, Regex phonetic normalizer | Unicode script, transliteration & code-mixing |
| **Translation** | Google GTX, MyMemory, deep-translator | High-resilience multilingual translation cascade |
| **Deployment** | Vercel (Frontend SPA) + Docker / Uvicorn (Backend) | Production hosting & cloud execution |
| **Testing** | PyTest (31 tests), TypeScript compiler (	sc) | Automated verification & type safety |

---

## Getting Started

### Prerequisites
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **Python**: 3.11 (via Conda or virtualenv)
- **Git**: 2.30+

---

### 1. Backend Setup

`ash
# Navigate to project root
cd MuVora

# Create and activate Python 3.11 environment
conda create -n muvora python=3.11 -y
conda activate muvora

# Install backend dependencies
pip install -r backend/requirements.txt
`

---

### 2. Model Training

The repository includes pre-trained weights (models/sentiment_bilstm.keras @ 16.7MB) and vocabulary (models/vocab.json). To retrain or inspect training:

`ash
# Train BiLSTM classifier on 50,000 IMDB samples
python backend/ml/train.py --epochs 3 --batch-size 64
`

To start the FastAPI backend:
`ash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
`
API Documentation will be live at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 3. Frontend Setup

`ash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
`
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Configuration & Environment Variables

### Backend Configuration (.env)

Copy .env.example to .env in the project root:

| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| PROJECT_NAME | No | MuVora | Name of the platform |
| DEBUG | No | False | Enable debug logging |
| CORS_ORIGINS | No | [\"http://localhost:5173\"] | Allowed origins for CORS requests |
| MODEL_PATH | No | models/sentiment_bilstm.keras | Path to trained BiLSTM model weights |
| VOCAB_PATH | No | models/vocab.json | Path to serialized vocabulary map |
| TRANSLATION_TIMEOUT_SECONDS | No | 8 | Timeout for external translation requests |
| MOCK_TRANSLATION | No | False | If True, forces offline dictionary provider |

### Frontend Configuration (rontend/.env)

Copy rontend/.env.example to rontend/.env:

| Variable | Required | Scope | Description |
| :--- | :---: | :--- | :--- |
| VITE_API_BASE_URL | Optional | Client | Base URL for deployed FastAPI backend (leave blank for local Vite proxy /api) |

---

## Usage Workflows

### 1. Analyzing a Review
1. Open the **Film Sentiment Analysis** tab.
2. Enter a movie title (optional) and paste review text in English, Telugu, Hindi, or Romanized script.
3. Select an optional language hint and preferred analysis display language.
4. Click **Analyze Review**.
5. View neural confidence, calibrated probability distribution, multi-part narrative synthesis, and aspect-based sentiment cards with direct quotes.

### 2. Translating Reviews & Dialogue
1. Open the **Real-time Translator** tab.
2. Select source language (or **Auto Detect**).
3. Select one or more target languages (English, Telugu, Hindi, Tamil, Spanish, etc.).
4. Type or use the **Mic (Voice Input)** button to speak your review.
5. Click **Translate Review**.
6. Use the **Speaker (TTS)** button to hear the translation or click **Export Translation** to download.

---

## API Reference

### POST /api/analyze
Analyzes review quality, language, sentiment, narrative synthesis, and aspect ratings.

**Request:**
`json
{
  \"movie_title\": \"Interstellar\",
  \"review\": \"I loved this movie. The acting was excellent, the story was emotional, and the ending was unforgettable.\",
  \"analysis_language\": \"en\"
}
`

**Response:**
`json
{
  \"status\": \"success\",
  \"sentiment\": \"positive\",
  \"confidence\": 0.98,
  \"positive_probability\": 0.99,
  \"negative_probability\": 0.01,
  \"summary\": \"The review expresses an overwhelmingly positive sentiment with enthusiastic appreciation for the movie.\",
  \"analysis\": {
    \"overall_tone\": \"positive\",
    \"strength\": \"strong\",
    \"synthesis\": {
      \"executive_summary\": \"The review expresses an overwhelmingly positive sentiment...\",
      \"detailed_narrative\": \"The evaluation of 'Interstellar' reveals a positive perspective...\",
      \"reviewer_tone\": \"Enthusiastic and admiring (strong intensity).\",
      \"recommendation\": \"Highly Recommended for theatrical viewing.\"
    }
  },
  \"aspects\": [
    {
      \"aspect\": \"acting\",
      \"aspect_label\": \"Acting & Cast Performance\",
      \"sentiment\": \"positive\",
      \"confidence\": 0.85,
      \"evidence\": \"The acting was excellent\"
    }
  ]
}
`

### POST /api/translate
Translates text into multiple target languages simultaneously.

**Request:**
`json
{
  \"text\": \"The movie is awesome\",
  \"source_language\": \"en\",
  \"target_languages\": [\"te\", \"hi\"]
}
`

**Response:**
`json
{
  \"original_text\": \"The movie is awesome\",
  \"detected_source\": \"en\",
  \"translations\": {
    \"te\": \"సినిమా అద్భుతంగా ఉంది\",
    \"hi\": \"फिल्म कमाल की है\"
  }
}
`

### GET /api/health
Checks backend and neural model status.

---

## Vercel Deployment Guide

The frontend is fully configured for zero-configuration Vercel deployment:

### Deploying the Frontend on Vercel:
1. Push the repository to GitHub: SatishReddy2804/MuVora.
2. Open your [Vercel Dashboard](https://vercel.com) and click **Add New Project**.
3. Import the SatishReddy2804/MuVora repository.
4. In Project Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: rontend
   - **Build Command**: 
pm run build
   - **Output Directory**: dist
   - **Install Command**: 
pm install
5. In **Environment Variables**, add:
   - VITE_API_BASE_URL: The URL of your deployed FastAPI backend (e.g. on Railway, Render, or cloud server).
6. Click **Deploy**. The included rontend/vercel.json ensures direct URL routing without 404 errors.

---

## Testing & Quality Assurance

### Automated Backend Tests (PyTest)
`ash
python -m pytest backend/tests -v
`
**Results: 31 passed in 45.9s**:
- Health & Model Info APIs
- Neural Inference (Positive, Negative, Mixed)
- Keyboard smash and character repetition rejection
- Native Telugu, Native Hindi, Romanized Telugu, Romanized Hindi
- Code-mixed Telugu-English and Hindi-English
- Aspect evidence extraction and quote attribution
- Multi-target translation pipeline

### Frontend Production Verification
`ash
cd frontend
npm run typecheck
npm run build
`
**Results: 0 errors, compiled in 6.59s**.

---

## Troubleshooting

- **CORS Error in Production**: Ensure your frontend Vercel URL (e.g., https://mu-vora.vercel.app) is added to CORS_ORIGINS in the backend environment.
- **Translation Provider Quota / 429**: MuVora automatically cascades from Google GTX to MyMemory public API and clean offline dictionary fallback.
- **TensorFlow GPU Warning on Windows**: TensorFlow 2.15 on Windows runs in optimized CPU mode by default; this is expected and does not affect accuracy or inference.

---

## Known Limitations

- **Probabilistic Domain**: Predictions represent statistical neural inferences and should not replace human judgment.
- **Dialectal Nuance**: Sarcasm or highly localized regional slang may not always be reflected in standardized translations.
- **Microphone Support**: Web Speech API voice input requires a supported browser (Google Chrome, Microsoft Edge, Safari) and microphone permissions.

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch: git checkout -b feat/your-feature.
3. Ensure typecheck and tests pass (
pm run typecheck, pytest backend/tests -v).
4. Commit your changes using conventional commit messages.
5. Open a Pull Request.

---

## License

This project is open source and available under the **MIT License**.

---

## Acknowledgements

- **Stanford University**: IMDB Large Movie Review Dataset.
- **FastAPI & Uvicorn**: Modern asynchronous web framework.
- **TensorFlow & Keras**: Deep learning ecosystem.
- **Vite & React Teams**: Modern frontend development toolchain.
