from dataclasses import dataclass


@dataclass(slots=True)
class Target:
    title: str
    directors: list[str]
    year: int
    country: str
    entity: str  # "movie" | "show"
