# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Intended Use

VibeMatch generates a ranked top-k list of songs from a small fixed catalog, given a
user's stated taste profile (favorite genre, favorite mood, target energy, and
whether they like acoustic sound). It assumes the user's stated preferences are a
reasonable stand-in for their actual taste, and that a song's catalog attributes
(genre, mood, energy, acousticness) are enough to judge fit. This is a **classroom
simulation**, not a production system — it is meant to demonstrate the
input-data → scoring → ranking pipeline behind real recommenders, not to serve real
listeners.

---

## 3. How the Model Works

Every song has a few tags and numbers attached to it: a genre, a mood, an energy
level from 0 to 1, and an "acousticness" level from 0 to 1. A user profile has the
same shape: a favorite genre, a favorite mood, a target energy, and whether they
like acoustic-sounding music.

To score a song, the model checks how well it matches the profile on each of those
features, then combines the checks into one number using fixed weights: genre match
matters most (35%), then mood match (25%), then how close the song's energy is to
the user's target energy (25%), then how well the song's acoustic/non-acoustic
character fits what the user said they like (15%). Genre and mood are all-or-nothing
matches — either the song is that genre or it isn't. Energy and acoustic fit are
"closeness" matches — a song doesn't have to be exactly the target energy, just
close to it, and it still gets partial credit the closer it is.

Once every song in the catalog has a score, they're sorted from highest to lowest,
and the top few are returned along with a short explanation listing which specific
features drove the match (e.g., "matches your preferred genre; energy close to your
preference"). This is the starter project's intended design — I implemented the
scoring/ranking logic and explanation generator, which were left as TODOs, and
expanded the catalog from 10 to 20 songs.

---

## 4. Data

The catalog (`data/songs.csv`) has **20 songs** with columns: `id`, `title`,
`artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`,
`acousticness`. Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie
pop, hip-hop (3 songs), edm (3 songs), acoustic (3 songs), and folk (1 song). I added
10 songs to the original 10-song starter set specifically to give the hip-hop, EDM,
and acoustic/low-energy profiles enough same-genre tracks to produce a meaningful
top-3, rather than falling back to unrelated songs.

Musical taste is much richer than what's captured here: there's no data on lyrics,
vocal style, instrumentation, cultural/regional origin, or release popularity, and
`tempo_bpm`, `valence`, and `danceability` are loaded but not currently used by the
scoring function at all.

---

## 5. Strengths

- Profiles whose favorite genre has 3+ catalog entries (hip-hop, EDM, acoustic, pop,
  lofi) get well-differentiated, sensible top-3 lists — see the three profiles run
  in the README, each of which produced songs clearly on-theme for that listener.
- The closeness scoring for energy correctly rewards "near misses": in the Hip-Hop
  Fan run, a song at energy 0.78 scored nearly as well as one at 0.72 against a
  target of 0.75, rather than requiring an exact match.
- Because genre is weighted highest, the system reliably keeps a user "in their
  lane" even when mood or energy targets are only loosely specified.

---

## 6. Limitations and Bias

- **Small catalog, uneven genre counts**: folk and ambient have only one song each,
  so a profile favoring those genres has no real ranking to do — whatever exists is
  "recommended" by default. This mirrors real-world **popularity bias**, where
  well-represented genres get better recommendations simply because there's more
  data to rank within.
- **Exact-match categorical scoring**: "hip-hop" vs. a hypothetical "rap" tag, or
  "chill" vs. "calm," would be scored as a complete mismatch (0.0) even though a
  person might consider them close. The model has no concept of similar-but-not-
  identical labels.
- **No personalization over time**: every run is a cold start. There's no use of
  listening history, skips, or feedback, so the model can't improve or adapt — it
  always reflects a snapshot of directly stated preferences.
- **Unused features**: `tempo_bpm`, `valence`, and `danceability` are loaded from
  the CSV but never factored into the score, so two songs that differ a lot on those
  axes but match on genre/mood/energy are treated as equally good.
- **Weight choices are arbitrary and mine**: genre at 35% vs. mood at 25% was a
  design decision, not something learned from data. A different set of weights
  would systematically favor different users' tastes, which is exactly how bias can
  get built into a "neutral-looking" formula.

---

## 7. Evaluation

I tested three deliberately distinct profiles: a **Hip-Hop Fan**
(`genre=hip-hop, mood=confident, energy=0.75, likes_acoustic=False`), an **Acoustic /
Low-Energy Listener** (`genre=acoustic, mood=calm, energy=0.2, likes_acoustic=True`),
and a **High-Tempo EDM Listener** (`genre=edm, mood=energetic, energy=0.95,
likes_acoustic=False`). Full output is in the README's "Sample Recommendation
Output" and "Experiments You Tried" sections.

I checked that each profile's top 3 were thematically consistent (all hip-hop songs
for the hip-hop fan, all quiet acoustic songs for the acoustic listener, all
high-energy EDM for the EDM listener), and that scores dropped off in an
interpretable way when a song matched genre but not mood, or matched genre and mood
but was farther from the target energy. What surprised me was how much a single
missing categorical match (mood, in "Basement Cypher"'s case) could drag a
same-genre song's score down relative to same-genre songs that matched everything —
confirming the weights are doing real work, not just genre alone.

---

## 8. Future Work

- Add tempo, valence, and danceability into the weighted score instead of loading
  them unused, so tempo-driven preferences (e.g. "high-tempo EDM") are scored
  directly rather than only via genre/mood/energy as a proxy.
- Replace exact-match genre/mood scoring with a similarity mapping (e.g. a small
  genre-adjacency table) so related-but-not-identical tags aren't scored as a total
  mismatch.
- Grow the catalog and balance it across genres so low-representation genres
  (folk, ambient) get a real ranking instead of a default.
- Add a diversity/de-duplication step to the ranking rule so the top-k isn't
  dominated by near-identical songs from the same artist (e.g. both "Ferric" rock
  tracks appearing together).
- Let the model take feedback (skip/like) and adjust future scores, moving from a
  static formula toward something that actually learns per-user.

---

## 9. Personal Reflection

Implementing the scoring function made it obvious that a "recommendation" is really
just an arithmetic decision dressed up in music vocabulary — the model doesn't know
what hip-hop or calm music *sounds* like, it just compares tags and numbers I chose
to weight in a particular order. The most interesting discovery was how much the
choice of *which* features to include (and which, like tempo and valence, to leave
unused) quietly shapes results just as much as the weights themselves. It changed
how I think about real recommendation apps: what feels like the algorithm "getting"
my taste is often just a well-tuned formula over a handful of catalog attributes,
and the boundaries of that formula (what data it has, what it ignores) are exactly
where its blind spots and biases live.
