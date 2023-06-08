with raw_json as (
    select
        *
    from
        read_json(
            $filename,
            format = 'array',
            columns = {'competition_id': integer,
            'season_id': integer,
            'country_name': varchar,
            'competition_name': varchar,
            'competition_gender': varchar,
            'competition_youth': boolean,
            'competition_international': boolean,
            'season_name': varchar,
            'match_updated': varchar,
            'match_updated_360': varchar,
            'match_available_360': varchar,
            'match_available': varchar}
        )
),
final as (
    select
    * replace(case when match_updated is null then null else cast(left(concat(replace(match_updated, 'T', ' '), ':00'), 19) as timestamp) end as match_updated,
              case when match_available is null then null else cast(left(concat(replace(match_available, 'T', ' '), ':00'), 19) as timestamp) end as match_available,
              cast(match_available_360 as timestamp) as match_available_360, 
              cast(match_updated_360 as timestamp) as match_updated_360
    )  
    from
        raw_json)
select
    *
from
    final;