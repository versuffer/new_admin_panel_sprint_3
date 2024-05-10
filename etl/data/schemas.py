from uuid import UUID

from pydantic import BaseModel


class PersonSchema(BaseModel):
    id: UUID
    name: str


class MovieDataSchema(BaseModel):
    id: str
    imdb_rating: float
    genres: list[str]
    title: str
    description: str | None = None
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[PersonSchema]
    actors: list[PersonSchema]
    writers: list[PersonSchema]


class GenreDataSchema(BaseModel):
    id: UUID
    name: str
    description: str | None = None


class PersonDataSchema(BaseModel):
    id: UUID
    full_name: str
