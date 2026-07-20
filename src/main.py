"""
Command line runner for the Music Recommender Simulation.

Runs the recommender for three distinct user profiles so their outputs
can be compared side by side.
"""

from src.recommender import load_songs, recommend_songs


PROFILES = {
    "Hip-Hop Fan": {"genre": "hip-hop", "mood": "confident", "energy": 0.75, "likes_acoustic": False},
    "Acoustic / Low-Energy Listener": {"genre": "acoustic", "mood": "calm", "energy": 0.2, "likes_acoustic": True},
    "High-Tempo EDM Listener": {"genre": "edm", "mood": "energetic", "energy": 0.95, "likes_acoustic": False},
}


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile_name, user_prefs in PROFILES.items():
        print(f"=== {profile_name} ===")
        print(f"Preferences: {user_prefs}\n")

        recommendations = recommend_songs(user_prefs, songs, k=3)
        for rec in recommendations:
            song, score, explanation = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()
        print()


if __name__ == "__main__":
    main()
