import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Weighted scoring recipe: genre and mood are exact matches, energy and
# acoustic fit are "closeness" scores so near-matches still score well.
GENRE_WEIGHT = 0.35
MOOD_WEIGHT = 0.25
ENERGY_WEIGHT = 0.25
ACOUSTIC_WEIGHT = 0.15

# Diversity penalty: applied at ranking time (not to the base score) so a
# song's raw fit to the user never changes, only its competitiveness once its
# artist already has a slot in the results. Only artist is penalized, not
# genre: penalizing repeat genre would fight the user's own genre preference,
# since matching genre is the whole point of that part of the score.
DIVERSITY_ARTIST_PENALTY = 0.15


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """OOP implementation of the recommendation logic."""
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score one song against a user profile; return (score, reasons)."""
        genre_score = 1.0 if user.favorite_genre == song.genre else 0.0
        mood_score = 1.0 if user.favorite_mood == song.mood else 0.0
        energy_score = 1.0 - abs(user.target_energy - song.energy)

        target_acousticness = 1.0 if user.likes_acoustic else 0.0
        acoustic_score = 1.0 - abs(target_acousticness - song.acousticness)

        total = (
            GENRE_WEIGHT * genre_score
            + MOOD_WEIGHT * mood_score
            + ENERGY_WEIGHT * energy_score
            + ACOUSTIC_WEIGHT * acoustic_score
        )

        reasons = []
        if genre_score == 1.0:
            reasons.append(f"matches your favorite genre ({song.genre})")
        if mood_score == 1.0:
            reasons.append(f"matches your favorite mood ({song.mood})")
        if energy_score >= 0.8:
            reasons.append(f"energy ({song.energy}) close to your target ({user.target_energy})")
        if acoustic_score >= 0.8:
            style = "acoustic" if user.likes_acoustic else "non-acoustic"
            reasons.append(f"{style} sound fits your preference (acousticness {song.acousticness})")
        if not reasons:
            reasons.append("closest overall match available in the catalog")

        return round(total, 4), reasons

    def recommend(self, user: UserProfile, k: int = 5, diversify: bool = True) -> List[Song]:
        """Return the top-k songs, greedily re-ranked to penalize repeat artists."""
        candidates = sorted(
            ((song, self._score(user, song)[0]) for song in self.songs),
            key=lambda pair: pair[1],
            reverse=True,
        )
        if not diversify:
            return [song for song, _ in candidates[:k]]

        selected: List[Song] = []
        seen_artists = set()
        remaining = list(candidates)
        while remaining and len(selected) < k:
            best_song, best_adjusted = None, None
            for song, base_score in remaining:
                penalty = DIVERSITY_ARTIST_PENALTY if song.artist in seen_artists else 0.0
                adjusted = base_score - penalty
                if best_adjusted is None or adjusted > best_adjusted:
                    best_song, best_adjusted = song, adjusted
            remaining = [(s, sc) for s, sc in remaining if s is not best_song]
            selected.append(best_song)
            seen_artists.add(best_song.artist)
        return selected

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song scored as it did."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dicts with numeric fields converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song dict against a user preference dict; return (score, reasons)."""
    genre_score = 1.0 if user_prefs.get("genre") == song["genre"] else 0.0
    mood_score = 1.0 if user_prefs.get("mood") == song["mood"] else 0.0

    if "energy" in user_prefs:
        energy_score = 1.0 - abs(user_prefs["energy"] - song["energy"])
    else:
        energy_score = 0.5

    target_acousticness = 1.0 if user_prefs.get("likes_acoustic") else 0.0
    acoustic_score = 1.0 - abs(target_acousticness - song["acousticness"])

    total = (
        GENRE_WEIGHT * genre_score
        + MOOD_WEIGHT * mood_score
        + ENERGY_WEIGHT * energy_score
        + ACOUSTIC_WEIGHT * acoustic_score
    )

    reasons = []
    if genre_score == 1.0 and "genre" in user_prefs:
        reasons.append(f"matches your preferred genre ({song['genre']})")
    if mood_score == 1.0 and "mood" in user_prefs:
        reasons.append(f"matches your preferred mood ({song['mood']})")
    if "energy" in user_prefs and energy_score >= 0.8:
        reasons.append(f"energy ({song['energy']}) close to your preference ({user_prefs['energy']})")
    if acoustic_score >= 0.8:
        style = "acoustic" if user_prefs.get("likes_acoustic") else "non-acoustic"
        reasons.append(f"{style} sound fits your preference (acousticness {song['acousticness']})")
    if not reasons:
        reasons.append("closest overall match available in the catalog")

    return round(total, 4), reasons

def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, diversify: bool = True
) -> List[Tuple[Dict, float, str]]:
    """Score every song, then greedily pick the top k, penalizing repeat artists."""
    candidates = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        candidates.append({"song": song, "score": score, "reasons": reasons})
    candidates.sort(key=lambda c: c["score"], reverse=True)

    if not diversify:
        return [(c["song"], c["score"], "; ".join(c["reasons"])) for c in candidates[:k]]

    selected = []
    seen_artists = set()
    remaining = list(candidates)
    while remaining and len(selected) < k:
        best, best_adjusted, best_penalty_notes = None, None, []
        for c in remaining:
            if c["song"]["artist"] in seen_artists:
                penalty = DIVERSITY_ARTIST_PENALTY
                notes = [f"-{DIVERSITY_ARTIST_PENALTY} repeat artist"]
            else:
                penalty = 0.0
                notes = []
            adjusted = round(c["score"] - penalty, 4)
            if best_adjusted is None or adjusted > best_adjusted:
                best, best_adjusted, best_penalty_notes = c, adjusted, notes
        remaining = [c for c in remaining if c is not best]
        selected.append((best, best_adjusted, best_penalty_notes))
        seen_artists.add(best["song"]["artist"])

    results = []
    for c, adjusted, penalty_notes in selected:
        reasons = list(c["reasons"])
        if penalty_notes:
            reasons.append(f"diversity penalty applied ({'; '.join(penalty_notes)})")
        results.append((c["song"], adjusted, "; ".join(reasons)))
    return results
