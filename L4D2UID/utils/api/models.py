from typing import TypedDict


class UserSearch(TypedDict):
    rank: str
    name: str
    scoce: str
    play_time: str
    last_time: str
    steamid: str


class AnnePlayer(TypedDict):
    mode: str
    name: str
    source: str
    playtime: str


class AllServer(TypedDict):
    command: str
    active_server: int
    max_server: int
    active_player: int
    max_player: int


class AnneSearch(TypedDict):
    steamid: str
    rank: str
    name: str
    score: str
    play_time: str
    last_time: str


class AnnePlayerDetail(TypedDict):
    rank: int
    source: str
    avg_source: float
    kills: str
    kills_people: str
    headshots: str
    avg_headshots: float
    map_play: str


class AnnePlayerError(TypedDict):
    mistake_shout: str
    kill_friend: str
    down_friend: str
    abandon_friend: str
    put_into: str
    agitate_witch: str


class AnnePlayerInfAvg(TypedDict):
    avg_smoker: float
    avg_boomer: float
    avg_hunter: float
    avg_charger: float
    avg_spitter: float
    avg_jockey: float
    avg_tank: float


class AnnePlayerSur(TypedDict):
    map_clear: str
    prefect_into: str
    get_oil: str
    ammo_arrange: str
    adrenaline_give: str
    pills_give: str
    first_aid_give: str
    friend_up: str
    diss_friend: str
    save_friend: str
    protect_friend: str
    pro_from_smoker: str
    pro_from_hunter: str
    pro_from_charger: str
    pro_from_jockey: str
    melee_charge: str
    tank_kill: str
    witch_instantly_kill: str


class AnnePlayerInf(TypedDict):
    sur_ace: str
    sur_down: str
    boommer_hit: str
    hunter_prefect: str
    hunter_success: str
    tank_damage: str
    charger_multiple: str


class AnnePlayerInfo(TypedDict):
    name: str
    avatar: str
    steamid: str
    playtime: str
    lasttime: str
    quarter_scope: str


class AnnePlayer2(TypedDict):
    kill_msg: str
    info: AnnePlayerInfo
    detail: AnnePlayerDetail
    error: AnnePlayerError
    inf_avg: AnnePlayerInfAvg
    sur: AnnePlayerSur
    inf: AnnePlayerInf


class AnneStatus(TypedDict):
    total_players: str
    total_kills: str
    total_headshots: str
    online_now: str
    today_online: str
    active_30d: str


class AnneOnlinePlayer(TypedDict):
    rank: str
    name: str
    steamid: str
    mode: str
    server: str
    score: str
    playtime: str


class AnneAward(TypedDict):
    category: str
    icon: str
    title: str
    desc: str
    winner: str
    steamid: str
    score: str


class AnneStatistics(TypedDict):
    total_zombie_kills: str
    total_headshots: str
    total_melee_kills: str
    avg_headshot_rate: str
    smoker: str
    boomer: str
    hunter: str
    spitter: str
    jockey: str
    charger: str
    rank_players: str
    rank_p50: str
    rank_p90: str
    rank_p99: str
    rank_max: str


class Profile58(TypedDict):
    steamid: str
    nickname: str
    steamname: str
    tag: str
    signature: str
    first_time: str
    last_time: str
    server: str
    user_group: str
    tag_color: int
    notify: int


class Stats58(TypedDict):
    steamid: str
    ci_kill: int
    ci_headshot: int
    smoker_kill: int
    smoker_headshot: int
    smoker_cut: int
    boomer_kill: int
    boomer_headshot: int
    hunter_kill: int
    hunter_headshot: int
    hunter_skeet: int
    spitter_kill: int
    spitter_headshot: int
    jockey_kill: int
    jockey_headshot: int
    jockey_skeet: int
    charger_kill: int
    charger_headshot: int
    charger_level: int
    defense_kill: int
    defense_cap: int
    itemuse_kit: int
    itemuse_pills: int
    itemuse_adrenaline: int
    itemget_throwable: int
    itemget_kit: int
    itemget_defib: int
    itemget_ammopack: int
    itemget_pills: int
    itemget_adrenaline: int
    accuracy_value: int
    accuracy_total: int
    dmg_tank_value: int
    dmg_tank_total: int
    dmg_witch_value: int
    dmg_witch_total: int
    round: int
    win: int
    assist: int
    damage: int
    damage_round: int
    protect: int
    clear: int
    clear_round: int
    revive: int
    ff: int
    incap: int
    ledge: int
    death: int
    played_minutes: int
    exp: int
    score_damage: float
    score_si_kill: float
    score_ci_kill: float
    score_clear: float
    score_revive: float
    score_protect: float
    score_ff: float
    score_incap: float
    score_defense: float
    score_assist: float
    score_round: float


class Player58Data(TypedDict):
    v5: Profile58
    v7: Stats58


class Player58Response(TypedDict):
    v5: Profile58
    v7: Stats58
    v2: dict
