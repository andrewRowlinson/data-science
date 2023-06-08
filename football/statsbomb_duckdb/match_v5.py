with raw_json as (
    select
        *
    from
        read_json(
            $filename,
            format = 'array',
            columns = {match_id: integer,
            match_date: date,
            kick_off: time,
            competition: 'struct(competition_id integer, country_name varchar, competition_name varchar)',
            season: 'struct(season_id integer, season_name varchar)',
            home_team: 'struct(home_team_id integer, home_team_name varchar, home_team_gender varchar, home_team_group varchar, country struct(id integer, name varchar),
                   managers struct(id varchar, name varchar, nickname varchar, dob date, country struct(id integer, name varchar))[])',
            away_team: 'struct(away_team_id integer, away_team_name varchar, away_team_gender varchar, away_team_group varchar, country struct(id integer, name varchar),
                   managers struct(id varchar, name varchar, nickname varchar, dob date, country struct(id integer, name varchar))[])',
            home_score: integer,
            away_score: integer,
            match_status: varchar,
            match_status_360: varchar,
            last_updated: varchar,
            last_updated_360: varchar,
            metadata: 'struct(data_version varchar)',
            match_week: integer,
            competition_stage: 'struct(id integer, name varchar)',
            stadium: 'struct(id integer, name varchar, country struct(id integer, name varchar))',
            referee: 'struct(id integer, name varchar, country struct(id integer, name varchar))'}
        )
),
final as (
    select
        match_id,
        match_date,
        kick_off,
        competition.competition_id,
        competition.country_name as competition_country_name,
        competition.competition_name,
        season.season_id,
        season.season_name,
        home_team.home_team_id,
        home_team.home_team_name,
        home_team.home_team_gender,
        home_team.home_team_group,
        home_team.country.id as home_team_country_id,
        home_team.country.name as home_team_country_name,
        home_team.managers [1].id as home_team_manager_id,
        home_team.managers [1].name as home_team_manager_name,
        home_team.managers [1].nickname as home_team_manager_nickname,
        home_team.managers [1].dob as home_team_manager_dob,
        home_team.managers [1].country.id as home_team_manager_country_id,
        home_team.managers [1].country.name as home_team_manager_country_name,
        away_team.away_team_id,
        away_team.away_team_name,
        away_team.away_team_gender,
        away_team.away_team_group,
        away_team.country.id as away_team_country_id,
        away_team.country.name as away_team_country_name,
        away_team.managers [1].id as away_team_manager_id,
        away_team.managers [1].name as away_team_manager_name,
        away_team.managers [1].nickname as away_team_manager_nickname,
        away_team.managers [1].dob as away_team_manager_dob,
        away_team.managers [1].country.id as away_team_manager_country_id,
        away_team.managers [1].country.name as away_team_manager_country_name,
        home_score,
        away_score,
        match_status,
        match_status_360,
        case when last_updated is null then null else cast(left(concat(replace(last_updated, 'T', ' '), ':00'), 19) as timestamp) end as last_updated,
        case when last_updated_360 is null then null else cast(left(concat(replace(last_updated_360, 'T', ' '), ':00'), 19) as timestamp) end as last_updated_360,
        metadata.data_version as metadata_data_version,
        match_week,
        competition_stage.id as competition_stage_id,
        competition_stage.name as competition_stage_name,
        stadium.id as stadium_id,
        stadium.name as stadium_name,
        stadium.country.id as country_id,
        stadium.country.name as country_name,
        referee.id as referee_id,
        referee.name as referee_name,
        referee.country.id as referee_country_id,
        referee.country.name as referee_country_name
    from
        raw_json
)
select
    *
from
    final;