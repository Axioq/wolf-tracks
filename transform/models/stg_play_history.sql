with source as (
    Select * From {{source('raw', 'raw_play_history')}}
),
cleaned as (
    Select
        play_id
        , started_at
        , stopped_at
        , song_duration_seconds
        , play_duration_seconds
        , paused_seconds
        , percent_complete
        , play_duration_seconds - paused_seconds as listen_duration_seconds
        , title as track_title
        , album as album_title
        , artist as artist_name
        , release_year
        , player
        , product
        , platform
        , media_type
        , transcode_decision
        , username
        , user_id
        , percent_complete >= 50 as is_completed
        , loaded_at
    From 
        source
    Where
        play_duration_seconds > 10
)
Select * From cleaned