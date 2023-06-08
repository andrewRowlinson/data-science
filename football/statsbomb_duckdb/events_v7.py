with raw_json as (
    select
        *
    from
        read_json(
            $filename,
            format = 'array',
            filename = true,
            -- columns from the StatsBomb docs, but excluding tactics, related_events, and shot.freeze_frame as many to one relationships
            -- these are instead handled seperately to create their own dataframes.
            columns = { 'id': varchar,
            index: integer,
            period: integer,
            timestamp: time,
            minute: integer,
            second: integer,
            type: 'struct(id ubigint, name varchar)',
            possession: integer,
            possession_team: 'struct(id ubigint, name varchar)',
            play_pattern: 'struct(id ubigint, name varchar)',
            team: 'struct(id ubigint, name varchar)',
            player: 'struct(id ubigint, name varchar)',
            position: 'struct(id ubigint, name varchar)',
            location: 'double[]',
            duration: double,
            under_pressure: boolean,
            off_camera: boolean,
            out: boolean,
            tactics: 'struct(formation varchar)',
            obv_for_after: double,
            obv_for_before: double,
            obv_for_net: double,
            obv_against_after: double,
            obv_against_before: double,
            obv_against_net: double,
            obv_total_net: double,
            -- in the docs counterpress is within the event type objects
            -- however, counterpress appears to be outside of these events, i.e. not within 50_50 event type ibject
            -- included this both inside the event type objects and outside just in case
            counterpress: boolean,
            '50_50': 'struct(
                outcome struct(id ubigint, name varchar),
                counterpress boolean
            )',
            bad_behaviour: 'struct(card struct(id ubigint, name varchar))',
            ball_receipt: 'struct(outcome struct(id ubigint, name varchar))',
            ball_recovery: 'struct(offensive boolean, recovery_failure boolean)',
            block: 'struct(
                deflection boolean,
                offensive boolean,
                save_block boolean,
                counterpress boolean
            )',
            carry: 'struct(end_location double[])',
            -- in the open-data there are some boolean columns left_foot, right_foot, head, other
            -- these are covered by body_part so ignored (columns are not in the docs)
            clearance: 'struct(
                aerial_won boolean,
                body_part struct(id ubigint, name varchar)
            )',
            dribble: 'struct(
                overrun boolean,
                nutmeg boolean,
                outcome struct(id ubigint, name varchar),
                no_touch boolean
            )',
            dribbled_past: 'struct(counterpress boolean)',
            duel: 'struct(
                counterpress boolean,
                type struct(id ubigint, name varchar),
                outcome struct(id ubigint, name varchar)
            )',
            foul_committed: 'struct(
                counterpress boolean,
                offensive boolean,
                type struct(id ubigint, name varchar),
                advantage boolean,
                penalty boolean,
                card struct(id ubigint, name varchar)
            )',
            foul_won: 'struct(
                defensive boolean,
                advantage boolean,
                penalty boolean
            )',
            -- open data also has the following boolean columns for goalkeeper
            -- shot_saved_to_post, shot_saved_off_target, punched_out, lost_out, success_out, lost_in_play, success_in_play, penalty_saved_to_post, saved_to_post
            -- ignored as not in the official spec and covered by type and outcome columns
            goalkeeper: 'struct(
                position struct(id ubigint, name varchar),
                technique struct(id ubigint, name varchar),
                body_part struct(id ubigint, name varchar),
                type struct(id ubigint, name varchar),
                outcome struct(id ubigint, name varchar),
                end_location double[] -- added but not in docs
            )',
            half_end: 'struct(
                early_video_end boolean,
                match_suspended boolean
            )',
            half_start: 'struct(late_video_start boolean)',
            injury_stoppage: 'struct(in_chain boolean)',
            interception: 'struct(outcome struct(id ubigint, name varchar))',
            miscontrol: 'struct(aerial_won boolean)',
            -- open data pass columns also has inswinging, outswinging, through_ball, straight
            -- ignored as not in the official spec and covered by technique column
            pass: 'struct(
                recipient struct(id ubigint, name varchar),
                length double,
                angle double,
                height struct(id ubigint, name varchar),
                end_location double[],
                assisted_shot_id varchar,
                backheel boolean,
                deflected boolean,
                miscommunication boolean,
                "cross" boolean,
                cut_back boolean,
                switch boolean,
                shot_assist boolean,
                goal_assist boolean,
                body_part struct(id ubigint, name varchar),
                type struct(id ubigint, name varchar),
                outcome struct(id ubigint, name varchar),
                technique struct(id ubigint, name varchar),
                aerial_won boolean, -- added but not in docs
                no_touch boolean -- added but not in docs
            )',
            player_off: 'struct(permanent boolean)',
            pressure: 'struct(counterpress boolean)',
            -- open data shot columns also has saved_off_target, saved_to_post, kick_off
            -- ignored as not in the official spec and covered by other columns (type/ outcome)
            shot: 'struct(
                key_pass_id varchar,
                end_location double[],
                aerial_won boolean,
                follows_dribble boolean,
                first_time boolean,
                open_goal boolean,
                one_on_one boolean,
                statsbomb_xg double,
                deflected boolean,
                technique struct(id ubigint, name varchar),
                shot_shot_assist boolean,
                shot_goal_assist boolean,
                body_part struct(id ubigint, name varchar),
                type struct(id ubigint, name varchar),
                outcome struct(id ubigint, name varchar),
                redirect boolean -- added but not in docs
            )',
            substitution: 'struct(replacement struct(id ubigint, name varchar), outcome struct(id ubigint, name varchar))' }
        )
),
final as (
    select
        cast(
            split(split(filename, '/') [-1], '.') [1] as integer
        ) as match_id,
        id as event_uuid,
        index,
        period,
        timestamp,
        minute,
        second,
        type.id as type_id,
        replace(type.name, '*', '') as type_name,
        coalesce(duel.type.id, foul_committed.type.id, goalkeeper.type.id, pass.type.id, shot.type.id) as event_type_id,
        coalesce(duel.type.name, foul_committed.type.name, goalkeeper.type.name, pass.type.name, shot.type.name) as event_type_name,
        coalesce("50_50".outcome.id, ball_receipt.outcome.id, dribble.outcome.id, duel.outcome.id, goalkeeper.outcome.id, interception.outcome.id, pass.outcome.id, shot.outcome.id, substitution.outcome.id) as outcome_id,
        coalesce("50_50".outcome.name, ball_receipt.outcome.name, dribble.outcome.name, duel.outcome.name, goalkeeper.outcome.name, interception.outcome.name, pass.outcome.name, shot.outcome.name, substitution.outcome.name) as outcome_name,
        possession,
        possession_team.id as possession_team_id,
        possession_team.name as possession_team_name,
        play_pattern.id as play_pattern_id,
        play_pattern.name as play_pattern_name,
        team.id as team_id,
        team.name as team_name,
        player.id as player_id,
        player.name as player_name,
        position.id as position_id,
        position.name as position_name,
        location [1] as x,
        location [2] as y,
        location [3] as z,
        coalesce(carry.end_location[1], goalkeeper.end_location[1], pass.end_location[1], shot.end_location[1]) as end_x,
        coalesce(carry.end_location[2], goalkeeper.end_location[2], pass.end_location[2], shot.end_location[2]) as end_y,
        shot.end_location [3] as end_z,
        duration,
        under_pressure,
        off_camera,
        out,
        tactics.formation as tactics_formation,
        obv_for_after,
        obv_for_before,
        obv_for_net,
        obv_against_after,
        obv_against_before,
        obv_against_net,
        obv_total_net,
        coalesce(counterpress, "50_50".counterpress, block.counterpress, dribbled_past.counterpress, duel.counterpress, foul_committed.counterpress, pressure.counterpress) as counterpress,
        coalesce(block.offensive, ball_recovery.offensive, foul_committed.offensive) as offensive,
        coalesce(clearance.aerial_won,  miscontrol.aerial_won, pass.aerial_won, shot.aerial_won) as aerial_won,
        coalesce(clearance.body_part.id, goalkeeper.body_part.id, pass.body_part.id, shot.body_part.id) as body_part_id,
        coalesce(clearance.body_part.name, goalkeeper.body_part.name, pass.body_part.name, shot.body_part.name) as body_part_name,
        coalesce(goalkeeper.technique.id, pass.technique.id, shot.technique.id) as technique_id,
        coalesce(goalkeeper.technique.name, pass.technique.name, shot.technique.name) as technique_name,
        coalesce(dribble.no_touch, pass.no_touch) as no_touch,
        coalesce(pass.deflected, shot.deflected) as deflected,
        bad_behaviour.card.id as bad_behaviour_card_id,
        bad_behaviour.card.name as bad_behaviour_card_name,
        ball_recovery.recovery_failure as ball_recovery_recovery_failure,
        block.deflection as block_deflection,
        block.save_block as block_save_block,
        dribble.overrun as dribble_overrun,
        dribble.nutmeg as dribble_nutmeg,
        coalesce(foul_committed.advantage, foul_won.advantage) as foul_advantage,
        coalesce(foul_committed.penalty, foul_won.penalty) as foul_penalty,
        foul_committed.card.id as foul_card_id,
        foul_committed.card.name as foul_card_name,
        foul_won.defensive as foul_defensive,
        goalkeeper.position.id as goalkeeper_position_id,
        goalkeeper.position.name as goalkeeper_position_name,
        half_end.early_video_end as half_end_early_video_end,
        half_end.match_suspended as half_end_match_suspended,
        half_start.late_video_start as half_start_late_video_start,
        injury_stoppage.in_chain as injury_stoppage_in_chain,
        pass.recipient.id as pass_recipient_id,
        pass.recipient.name as pass_recipient_name,
        pass.length as pass_length,
        pass.angle as pass_angle,
        pass.height.id as pass_height_id,
        pass.height.name as pass_height_name,
        pass.assisted_shot_id as pass_assisted_shot_id,
        pass.backheel as pass_backheel,
        pass.miscommunication as pass_miscommunication,
        pass."cross" as pass_cross,
        pass.cut_back as pass_cut_back,
        pass.switch as pass_switch,
        pass.shot_assist as pass_shot_assist,
        pass.goal_assist as pass_goal_assist,
        player_off.permanent as player_off_permanent,
        shot.key_pass_id as shot_key_pass_id,
        shot.follows_dribble as shot_follows_dribble,
        shot.first_time as shot_first_time,
        shot.open_goal as shot_open_goal,
        shot.one_on_one as shot_one_on_one,
        shot.statsbomb_xg as shot_statsbomb_xg,
        shot.shot_shot_assist,
        shot.shot_goal_assist,
        shot.redirect as shot_redirect,
        substitution.replacement.id as substitution_replacement_id,
        substitution.replacement.name as substitution_replacement_name
    from
        raw_json
)
select
    *
from
    final;