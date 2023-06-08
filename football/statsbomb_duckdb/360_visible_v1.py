with raw_json as (
    select
        *
    from
        read_json(
            $filename,
            format = 'array',
            columns = {event_uuid: varchar,
            visible_area: 'double[]'},
            filename = true
        )
)
select
    cast(split(split(filename, '/') [-1], '.') [1] as integer) as match_id,
    event_uuid,
    visible_area
from
    raw_json;