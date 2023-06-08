with raw_json as (
    select
        *
    from
        read_json(
            $filename,
            format = 'array',
            filename = true,
            columns = {team_id: integer,
            team_name: varchar,
            lineup: 'STRUCT(
                        player_id UBIGINT,
                        player_name VARCHAR,
                        jersey_number UBIGINT,
                        country STRUCT(id UBIGINT, "name" VARCHAR),
                        player_nickname VARCHAR
                        )[]'}
        )
),
final as (
    select
        cast(split(split(filename, '/') [-1], '.') [1] as integer) as match_id,
        team_id,
        team_name,
        unnest(lineup).player_id as player_id,
        unnest(lineup).player_name as player_name,
        unnest(lineup).jersey_number as jersey_number,
        unnest(lineup).player_nickname as player_nickname,
        unnest(lineup).country.id as country_id,
        unnest(lineup).country.name as country_name,
    from
        raw_json
)
select
    *
from
    final;