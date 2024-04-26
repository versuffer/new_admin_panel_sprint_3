# flake8: noqa

_base_sql = f"""
SELECT "content"."film_work"."id",
       "content"."film_work"."title",
       "content"."film_work"."description",
       "content"."film_work"."rating" as imdb_rating,
       "content"."film_work"."type",
       COALESCE (JSON_AGG(DISTINCT "content"."genre"."name"), '[]') AS "genres",
       COALESCE (JSON_AGG(DISTINCT "content"."person"."full_name") FILTER (WHERE "content"."person_film_work"."role" = 'actor'), '[]') AS "actors_names",
       COALESCE (JSON_AGG(DISTINCT "content"."person"."full_name" ) FILTER (WHERE "content"."person_film_work"."role" = 'director'), '[]') AS "directors_names",
       COALESCE (JSON_AGG(DISTINCT "content"."person"."full_name" ) FILTER (WHERE "content"."person_film_work"."role" = 'writer'), '[]') AS "writers_names",
	   COALESCE (JSON_AGG(DISTINCT jsonb_build_object('id', "content"."person"."id", 'name', "content"."person"."full_name")) FILTER (WHERE "content"."person_film_work"."role" = 'actor'), '[]') AS "actors",
	   COALESCE (JSON_AGG(DISTINCT jsonb_build_object('id', "content"."person"."id", 'name', "content"."person"."full_name")) FILTER (WHERE "content"."person_film_work"."role" = 'director'), '[]') AS "directors",
	   COALESCE (JSON_AGG(DISTINCT jsonb_build_object('id', "content"."person"."id", 'name', "content"."person"."full_name")) FILTER (WHERE "content"."person_film_work"."role" = 'writer'), '[]') AS "writers"
  FROM "content"."film_work"
  LEFT OUTER JOIN "content"."genre_film_work"
    ON ("content"."film_work"."id" = "content"."genre_film_work"."film_work_id")
  LEFT OUTER JOIN "content"."genre"
    ON ("content"."genre_film_work"."genre_id" = "content"."genre"."id")
  LEFT OUTER JOIN "content"."person_film_work"
    ON ("content"."film_work"."id" = "content"."person_film_work"."film_work_id")
  LEFT OUTER JOIN "content"."person"
    ON ("content"."person_film_work"."person_id" = "content"."person"."id")
  """
_updated_at_filter_sql = 'WHERE "content"."film_work"."updated_at" > %s OR "content"."person"."updated_at" > %s OR "content"."genre"."updated_at" > %s'
_group_by_sql = 'GROUP BY "content"."film_work"."id"'

get_last_modified_sql = _base_sql + _updated_at_filter_sql + _group_by_sql
get_all_sql = _base_sql + _group_by_sql
