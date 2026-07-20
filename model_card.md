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

**Not intended for:** real listeners or a real music app, catalogs bigger than a
handful of songs (it re-scores every song on every request, so it won't scale),
decisions where a wrong or biased recommendation has real consequences, or as a
stand-in for how any actual commercial recommender works — this is a simplified
teaching model, not a reverse-engineering of Spotify or YouTube.

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

**Diversity/fairness step:** picking the top-k isn't just "take the 5 highest
scores" anymore. Songs are chosen one at a time, and after a song is picked, any
remaining song by that same artist gets a small penalty (0.15) before the next pick
is made. Without this, a catalog where one artist happens to have several
well-matching songs would let that one artist quietly take over someone's entire
recommendation list — a small-scale version of the "filter bubble" problem, where a
system keeps showing more of the same thing just because it scored well once. The
penalty gives other, slightly-lower-scoring artists a real chance to appear instead
of being crowded out, without changing how any individual song is judged. Genre is
deliberately left unpenalized, since discouraging genre repetition would work
against the user's own stated genre preference rather than improving fairness.

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
- **Discovered weakness — silent conflict resolution**: testing an adversarial
  profile (`genre=acoustic, mood=sad, energy=0.9`) showed that the system has no way
  to detect when a user's own stated preferences don't co-occur in the catalog. It
  recommended "Paper Boats," a song with actual energy 0.25, as the #1 result for a
  request for energy 0.9, purely because genre and mood together (60% of the score)
  outweighed a bad energy match. A production system that silently resolves internal
  contradictions like this, instead of surfacing them, risks confidently serving
  recommendations a user would call "wrong" even though the math never made an
  error. This also compounds with the popularity-bias limitation above: genres with
  only one or two songs (rock, jazz, folk) can't offer an alternative that resolves
  the conflict better, so the distortion is worse for underrepresented genres.

---

## 7. Evaluation

### Core profiles (see README for full output)

I tested three deliberately distinct profiles: a **Hip-Hop Fan**
(`genre=hip-hop, mood=confident, energy=0.75, likes_acoustic=False`), an **Acoustic /
Low-Energy Listener** (`genre=acoustic, mood=calm, energy=0.2, likes_acoustic=True`),
and a **High-Tempo EDM Listener** (`genre=edm, mood=energetic, energy=0.95,
likes_acoustic=False`).

I checked that each profile's top 3 were thematically consistent (all hip-hop songs
for the hip-hop fan, all quiet acoustic songs for the acoustic listener, all
high-energy EDM for the EDM listener), and that scores dropped off in an
interpretable way when a song matched genre but not mood, or matched genre and mood
but was farther from the target energy. What surprised me was how much a single
missing categorical match (mood, in "Basement Cypher"'s case) could drag a
same-genre song's score down relative to same-genre songs that matched everything —
confirming the weights are doing real work, not just genre alone.

**Cross-profile comparison:** the EDM listener's top picks are all high-energy,
non-acoustic tracks (energy ≥ 0.9, acousticness ≤ 0.08); the acoustic listener's top
picks are the near-opposite (energy ≤ 0.25, acousticness ≥ 0.88). The formula never
changes between runs — only the target values do — which is exactly why the two
lists land on opposite ends of the catalog.

### Stress test and adversarial profile

I ran four more profiles at `k=5` to probe edge cases (see terminal output below).

```text
=== High-Energy Pop ===
Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'likes_acoustic': False}
Sunrise City - Score: 0.95
Because: matches your preferred genre (pop); matches your preferred mood (happy); energy (0.82) close to your preference (0.9); non-acoustic sound fits your preference (acousticness 0.18)
Gym Hero - Score: 0.73
Because: matches your preferred genre (pop); energy (0.93) close to your preference (0.9); non-acoustic sound fits your preference (acousticness 0.05)
Rooftop Lights - Score: 0.56
Because: matches your preferred mood (happy); energy (0.76) close to your preference (0.9)
Neon Static - Score: 0.39
Pulse Overdrive - Score: 0.39

=== Chill Lofi ===
Preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}
Library Rain - Score: 0.98
Midnight Coding - Score: 0.94
Focus Flow - Score: 0.70
Spacewalk Thoughts - Score: 0.62
Basement Cypher - Score: 0.49

=== Deep Intense Rock ===
Preferences: {'genre': 'rock', 'mood': 'intense', 'energy': 0.9, 'likes_acoustic': False}
Storm Runner - Score: 0.98
Gym Hero - Score: 0.64
Neon Static - Score: 0.39
Pulse Overdrive - Score: 0.39
Voltage Youth - Score: 0.38

=== Adversarial: Acoustic+Sad but Energy 0.9 ===
Preferences: {'genre': 'acoustic', 'mood': 'sad', 'energy': 0.9, 'likes_acoustic': True}
Paper Boats - Score: 0.82
Bare Wire - Score: 0.81
Porchlight Sessions - Score: 0.56
Rooftop Lights - Score: 0.27
Storm Runner - Score: 0.26
```

**"Gym Hero" question, answered:** the assignment specifically asks why "Gym Hero"
(pop/intense, energy 0.93) might keep surfacing for a "Happy Pop" listener. In this
system it does **not** win — "Sunrise City" (pop/happy, energy 0.82) outranks it
0.95 to 0.73, because a matching mood (worth 25%) plus a slightly-off energy beats a
missing mood plus a near-perfect energy. In plain language: the system cares more
about "does this feel like the mood you asked for" than "is this exactly the energy
you asked for" — so a happy song that's a little too mellow still beats an intense
song that's almost exactly the right intensity.

**Adversarial result:** the profile deliberately asked for two things that don't
coexist in the catalog — "acoustic + sad" songs are all low-energy (~0.2), but the
profile also asked for energy 0.9. The system doesn't detect this contradiction; it
just quietly averages through it. "Paper Boats" wins anyway (0.82) because genre +
mood match (60% of the score) outweighs a bad energy score, even though its actual
energy (0.25) is nowhere near the requested 0.9. A user would likely feel this
recommendation is "wrong" even though the math is working exactly as designed — a
real gap between "mathematically top-ranked" and "actually satisfying."

**Single-representation genre:** "Deep Intense Rock" surfaces the catalog's rock
gap — only one song ("Storm Runner") is actually rock, so positions 2–5 are filled
by unrelated high-energy tracks (an EDM song, a pop song) that share no genre or
mood with the request at all, at noticeably lower and closely-bunched scores
(0.38–0.64). The gap between rank 1 and rank 2 (0.98 → 0.64) is a visible signal that
the "recommendation" past #1 is really "closest thing we have," not a confident
match.

### Weight-shift experiment

I temporarily halved the genre weight (0.35 → 0.175) and doubled the energy weight
(0.25 → 0.5) to test sensitivity, then reverted it — this was not kept in the final
code.

```text
--- ORIGINAL WEIGHTS (genre 0.35, energy 0.25) ---
High-Energy Pop:      Sunrise City 0.95, Gym Hero 0.73, Rooftop Lights 0.56
Adversarial profile:  Paper Boats 0.82, Bare Wire 0.81, Porchlight Sessions 0.56

--- EXPERIMENT (genre 0.175, energy 0.5) ---
High-Energy Pop:      Sunrise City 1.01, Gym Hero 0.80, Rooftop Lights 0.78
Adversarial profile:  Paper Boats 0.73, Bare Wire 0.70, Neon Static 0.51
```

The ranking order for High-Energy Pop didn't flip, but the gap between songs
narrowed a lot (Gym Hero and Rooftop Lights went from 0.17 apart to 0.02 apart) —
weighting energy more heavily makes near-energy-matches much more competitive with
mood matches. The adversarial profile's #3 slot *did* flip: "Porchlight Sessions"
(genre match, terrible energy fit) got pushed out by "Neon Static" (an EDM song with
zero genre/mood match but energy exactly 0.9). This confirms the recipe is
genuinely sensitive to its weights — the same catalog and same user profile produced
a different top-3 purely from reweighting, which is "more energy-accurate" but
arguably less "genre-faithful." Neither is objectively more correct; it's a
trade-off the weights encode.

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
- ~~Add a diversity/de-duplication step to the ranking rule so the top-k isn't
  dominated by near-identical songs from the same artist~~ — **done**: both
  `recommend_songs()` and `Recommender.recommend()` now apply a `-0.15` repeat-artist
  penalty during ranking (see README "Bonus: Diversity Penalty"). A natural next
  step would be a smarter penalty that scales with how many songs are already picked
  from that artist, instead of one flat number regardless of the repeat count.
- Let the model take feedback (skip/like) and adjust future scores, moving from a
  static formula toward something that actually learns per-user.

---

## 9. Personal Reflection

The biggest learning moment was seeing that a "recommendation" is just an
arithmetic decision wearing music vocabulary. The program doesn't know what
hip-hop or calm music sounds like — it compares a few tags and numbers using
weights I picked, and whichever song adds up to the highest number wins. Once I
saw that plainly, a lot of what feels mysterious about music apps stopped feeling
mysterious.

I had help writing and organizing the code, but I still had to check everything
myself: I ran the tests, read through the scoring math line by line to make sure
the weights actually added up the way I intended, and manually worked out a few
songs' scores by hand to confirm the numbers matched what the program printed.
The one place I had to be most careful was the adversarial test — it was tempting
to accept the first ranking that came out, but I had to sit with it and ask
whether the top result actually made sense for a real person, not just whether
the math ran without errors.

What surprised me most is how convincing a really simple system can feel. Watching
the acoustic listener's list and the EDM listener's list come out completely
different, just from changing four numbers, felt like the program "understood"
something about each listener — even though underneath it's just one formula
applied twice with different targets.

If I kept working on this, I'd want to add real listening feedback so the system
could improve instead of staying frozen, let it recognize genres or moods that are
similar but not identical (like "calm" and "chill"), and grow the song list enough
that every genre gets a fair, well-supported ranking instead of just one or two
songs standing in for a whole style of music.
