with raw_json as (
    select
        * replace(unnest(freeze_frame) as freeze_frame)
    from
        read_json(
            $filename,
            format = 'array',
            columns = {event_uuid: varchar,
            freeze_frame: 'struct(teammate boolean, actor boolean, keeper boolean, location double[])[]'},
            filename = true
        )
)
select
    cast(split(split(filename, '/') [-1], '.') [1] as integer) as match_id,
    event_uuid,
    freeze_frame.teammate,
    freeze_frame.actor,
    freeze_frame.keeper,
    freeze_frame.location [1] as x,
    freeze_frame.location [2] as y,
from
    raw_json;