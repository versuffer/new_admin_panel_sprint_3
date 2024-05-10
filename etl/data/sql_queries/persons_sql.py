_base_sql = """
SELECT "content"."person"."id",
       "content"."person"."full_name"
  FROM "content"."person"
  """

_updated_at_filter_sql = 'WHERE "content"."person"."updated_at" > {last_sync_time}'

get_last_modified_persons_sql = _base_sql + _updated_at_filter_sql
get_all_persons_sql = _base_sql
