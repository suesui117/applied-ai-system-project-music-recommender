# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

**How real recommenders work:** Platforms like Spotify and YouTube mainly combine two
approaches. **Collaborative filtering** looks at behavior across many users — if
listeners who liked the same songs you did also liked song X, X gets recommended to
you, even if the system knows nothing about X's actual sound. **Content-based
filtering** (what this project simulates) instead looks at the attributes of the item
itself — genre, mood, tempo, energy — and matches those attributes against a profile
of what one user prefers. Real systems blend both, plus signals like skips, replays,
and playlist co-occurrence, but the core idea in each case is the same three-part
pipeline:

- **Input data**: raw attributes of each song (genre, mood, energy, tempo, valence,
  danceability, acousticness) — a fixed, unopinionated description of the item.
- **User preferences**: a taste profile (favorite genre/mood, target energy, whether
  the user likes acoustic sound) — this is what makes recommendations personal.
- **Ranking/selection**: a scoring function combines input data + preferences into a
  single number per song, and the top-scoring songs are selected and shown — this is
  the step that actually turns data into a decision.

**This system's design:**

- Each `Song` uses: `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`,
  `acousticness`.
- Each `UserProfile` stores: `favorite_genre`, `favorite_mood`, `target_energy`,
  `likes_acoustic`.
- The `Recommender` scores each song with a weighted sum: genre match (35%) + mood
  match (25%) + energy closeness (25%) + acoustic fit (15%). Genre/mood are exact
  matches (1.0 or 0.0); energy and acoustic fit are closeness scores
  (`1 - abs(difference)`) so a song doesn't need to be identical to score well, just
  close.
- Songs are ranked by sorting all scores descending and taking the top `k`.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



