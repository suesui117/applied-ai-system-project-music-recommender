import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Weighted scoring recipe: genre and mood are exact matches, energy and
# acoustic fit are "closeness" scores so near-matches still score well.
GENRE_WEIGHT = 0.35
MOOD_WEIGHT = 0.25
ENERGY_WEIGHT = 0.25
ACOUSTIC_WEIGHT = 0.15


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = [(song, self._score(user, song)) for song in self.songs]
        scored.sort(key=lambda pair: pair[1][0], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = self._score(user, song)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
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
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs keys (all optional): genre, mood, energy (0-1), likes_acoustic (bool)
    """
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

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
