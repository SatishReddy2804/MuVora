import re
from typing import List, Dict, Any, Optional
from backend.app.schemas.sentiment import AspectSentiment


class AspectAnalyzer:
    """
    Extracts aspect-based sentiments from movie reviews with exact supporting evidence quotes.
    Supports both explicit cinema aspects (Acting, Story, Direction, Screenplay, Music, Visuals)
    and implicit/holistic cinema execution & entertainment value when general appraisals are given.
    """

    ASPECT_DEFINITIONS = {
        "acting": {
            "keywords": [
                "acting", "actor", "actors", "actress", "performance", "performances", 
                "cast", "role", "roles", "lead", "hero", "heroine", "villain", "natana", 
                "abhinay", "star", "stars", "character", "characters", "presence", "portrayal"
            ],
            "label": "Acting & Cast Performance",
            "implicit_triggers": ["hero carried", "lead gave", "superb role", "great cast"]
        },
        "story": {
            "keywords": [
                "story", "plot", "storyline", "script", "concept", "theme", "premise", 
                "katha", "kahaani", "kahani", "twist", "twists", "narrative", "arc", 
                "writing", "depth", "climax", "ending"
            ],
            "label": "Story & Plot Narrative",
            "implicit_triggers": ["predictable", "gripping", "thrilling", "keeps you guessing", "mind bending"]
        },
        "direction": {
            "keywords": [
                "direction", "director", "filmmaker", "directing", "vision", "directorial", 
                "darsakudu", "nirdeshak", "helmed", "execution", "craft", "presentation", "handling"
            ],
            "label": "Direction & Filmmaking Craft",
            "implicit_triggers": ["well made", "poorly made", "masterful", "amateurish", "masterpiece"]
        },
        "screenplay": {
            "keywords": [
                "screenplay", "pacing", "pace", "first half", "second half", "scenes", 
                "lag", "drag", "boring parts", "rhythm", "slow", "fast paced", "runtime", 
                "length", "dragged"
            ],
            "label": "Screenplay & Pacing",
            "implicit_triggers": ["drags", "never gets boring", "edge of the seat", "slow burn", "laggy"]
        },
        "music": {
            "keywords": [
                "music", "song", "songs", "soundtrack", "bgm", "score", "audio", 
                "paatalu", "gaane", "sangeet", "background score", "theme song", "tracks"
            ],
            "label": "Music & Soundtrack (BGM)",
            "implicit_triggers": ["goosebumps bgm", "banging score", "melodious", "catchy songs"]
        },
        "visuals": {
            "keywords": [
                "visuals", "cinematography", "vfx", "cgi", "camera", "camerawork", 
                "visual", "shots", "lighting", "frames", "color palette", "aesthetic"
            ],
            "label": "Visuals & Cinematography",
            "implicit_triggers": ["eye candy", "visually stunning", "gorgeous frames", "spectacle"]
        },
        "entertainment": {
            "keywords": [
                "movie", "film", "cinema", "flick", "watch", "entertainment", "experience",
                "theatre", "hall", "ticket", "blockbuster", "fun", "comedy", "emotional"
            ],
            "label": "Overall Cinematic Experience",
            "implicit_triggers": ["awesome", "fantastic", "waste of time", "must watch", "worth watching", "chala bagundi", "bahut accha"]
        }
    }

    POSITIVE_WORDS = {
        "good", "great", "excellent", "superb", "brilliant", "awesome", "fantastic",
        "amazing", "loved", "enjoyed", "unforgettable", "emotional", "touching",
        "top notch", "masterpiece", "flawless", "wonder", "wonderful", "bagundi",
        "bagundhi", "super", "accha", "achha", "achi", "mast", "badiya", "nachindi",
        "entertaining", "solid", "gripping", "stellar", "impressive", "remarkable",
        "pleasurable", "engaging", "fascinating", "terrific", "phenomenal"
    }

    NEGATIVE_WORDS = {
        "bad", "terrible", "horrible", "awful", "trash", "boring", "worst", "weak",
        "poor", "predictable", "dull", "annoying", "pathetic", "waste", "disappointing",
        "unwatchable", "flat", "cliché", "kharab", "bekaar", "rod", "daridram",
        "tedious", "forgettable", "pointless", "shallow", "sloppy", "mess", "crap"
    }

    def analyze_aspects(self, text: str) -> List[AspectSentiment]:
        if not text or not text.strip():
            return []

        # Split text into sentences for localized evidence extraction
        raw_sentences = re.split(r"[.!?\n]+", text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        if not sentences:
            sentences = [text.strip()]

        results = []

        for aspect_key, aspect_info in self.ASPECT_DEFINITIONS.items():
            keywords = aspect_info["keywords"]
            implicit_triggers = aspect_info.get("implicit_triggers", [])
            label = aspect_info["label"]

            # Find matching sentences
            matching_sentences = []
            for s in sentences:
                s_lower = s.lower()
                tokens = re.findall(r"\b\w+\b", s_lower)
                has_kw = any(kw in tokens or kw in s_lower for kw in keywords)
                has_implicit = any(trig in s_lower for trig in implicit_triggers)
                if has_kw or has_implicit:
                    matching_sentences.append(s)

            if not matching_sentences:
                # Omit generic entertainment card if not triggered
                if aspect_key == "entertainment":
                    continue

                results.append(AspectSentiment(
                    aspect=aspect_key,
                    aspect_label=label,
                    sentiment="not_mentioned",
                    confidence=1.0,
                    evidence=None
                ))
                continue

            # Evaluate sentiment within the evidence sentences
            evidence_text = " ".join(matching_sentences[:2])
            tokens = re.findall(r"\b\w+\b", evidence_text.lower())

            pos_count = sum(1 for t in tokens if t in self.POSITIVE_WORDS)
            neg_count = sum(1 for t in tokens if t in self.NEGATIVE_WORDS)

            ev_lower = evidence_text.lower()
            if any(p in ev_lower for p in ["top notch", "must watch", "master piece", "masterpiece", "mind blowing"]):
                pos_count += 2
            if any(p in ev_lower for p in ["waste of time", "disaster", "painful to watch", "not worth"]):
                neg_count += 2

            # Check negations (e.g. "not good", "never boring")
            for i in range(len(tokens) - 1):
                if tokens[i] in {"not", "never", "no", "hardly", "barely"}:
                    if tokens[i+1] in self.POSITIVE_WORDS:
                        pos_count = max(0, pos_count - 1)
                        neg_count += 1
                    elif tokens[i+1] in self.NEGATIVE_WORDS:
                        neg_count = max(0, neg_count - 1)
                        pos_count += 1

            if pos_count > neg_count:
                sentiment = "positive"
                conf = min(0.98, 0.75 + 0.05 * pos_count)
            elif neg_count > pos_count:
                sentiment = "negative"
                conf = min(0.98, 0.75 + 0.05 * neg_count)
            else:
                sentiment = "neutral"
                conf = 0.70

            results.append(AspectSentiment(
                aspect=aspect_key,
                aspect_label=label,
                sentiment=sentiment,
                confidence=round(conf, 2),
                evidence=evidence_text[:200]
            ))

        return results


aspect_analyzer = AspectAnalyzer()
