_base_sql = """
SELECT "content"."genre"."id",
       "content"."genre"."name",
       "content"."genre"."description"
  FROM "content"."genre"
  """

_updated_at_filter_sql = 'WHERE "content"."genre"."updated_at" > {last_sync_time}'

get_last_modified_genres_sql = _base_sql + _updated_at_filter_sql
get_all_genres_sql = _base_sql
