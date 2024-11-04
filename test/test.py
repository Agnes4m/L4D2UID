import httpx
from lxml import html
from bs4 import BeautifulSoup

resp = httpx.get(
    "https://sb.trygek.com/l4d_stats/ranking/player.php",
    params={"steamid": "STEAM_1:0:203395448"},
)
html_content = resp.content
soup = BeautifulSoup(html_content, "lxml")

tbody = soup.find(
    "div",
    class_="content text-center text-md-left",
    style="background-color: #f2f2f2;",
)
# print(tbody)
if tbody is not None:
    kill_tag = tbody.find(
        name="div",
        class_="card-body worldmap d-flex flex-column justify-content-center text-center",
    )
    print(kill_tag)
    tbody_tags = tbody.find_all(
        "table",
        class_="table content-table-noborder text-left",
    )
    print(len(tbody_tags))
    info_tag = tbody_tags[0]
    detail_tag = tbody_tags[1]
    error_tag = tbody_tags[2]
    inf_avg_tag = tbody_tags[3]
    sur_tag = tbody_tags[4]
    inf_tag = tbody_tags[5]

    info_tr = info_tag.select("tr")
    info_dict = {
        "name": info_tr[0].select("td")[1].text.strip(),
        "avatar": info_tr[1].select("td")[1].text.strip(),
        "steamid": info_tr[2].select("td")[1].text.strip(),
        "playtime": info_tr[3].select("td")[1].text.strip(),
        "lasttime": info_tr[4].select("td")[1].text.strip(),
    }
    print(info_dict)
    detail_tag = {
        "rank": detail_tag.select("tr")[0].select("td")[1].text.strip(),
        "source": detail_tag.select("tr")[1].select("td")[1].text.strip(),
        "avg_source": detail_tag.select("tr")[2].select("td")[1].text.strip(),
        "kills": detail_tag.select("tr")[3].select("td")[1].text.strip(),
        "kills_people": detail_tag.select("tr")[4]
        .select("td")[1]
        .text.strip(),
        "headshots": detail_tag.select("tr")[5].select("td")[1].text.strip(),
        "avg_headshots": detail_tag.select("tr")[6]
        .select("td")[1]
        .text.strip(),
        "map_play": detail_tag.select("tr")[7].select("td")[1].text.strip(),
    }
    error_tag = {
        "mistake_shout": error_tag.select("tr")[0]
        .select("td")[1]
        .text.strip(),
        "kill_friend": error_tag.select("tr")[1].select("td")[1].text.strip(),
        "down_friend": error_tag.select("tr")[2].select("td")[1].text.strip(),
        "abandon_friend": error_tag.select("tr")[3]
        .select("td")[1]
        .text.strip(),
        "put_into": error_tag.select("tr")[4].select("td")[1].text.strip(),
        "agitate_witch": error_tag.select("tr")[5]
        .select("td")[1]
        .text.strip(),
    }
    inf_avg_dict = {
        "avg_smoker": inf_avg_tag.select("tr")[0].select("td")[1].text.strip(),
        "avg_boomer": inf_avg_tag.select("tr")[1].select("td")[1].text.strip(),
        "avg_hunter": inf_avg_tag.select("tr")[2].select("td")[1].text.strip(),
        "avg_charger": inf_avg_tag.select("tr")[3]
        .select("td")[1]
        .text.strip(),
        "avg_spitter": inf_avg_tag.select("tr")[4]
        .select("td")[1]
        .text.strip(),
        "avg_jockey": inf_avg_tag.select("tr")[5].select("td")[1].text.strip(),
        "avg_tank": inf_avg_tag.select("tr")[6].select("td")[1].text.strip(),
    }
    sur_dict = {
        "map_clear": sur_tag.select("tr")[0].select("td")[1].text.strip(),
        "prefect_into": sur_tag.select("tr")[1].select("td")[1].text.strip(),
        "get_oil": sur_tag.select("tr")[2].select("td")[1].text.strip(),
        "ammo_arrange": sur_tag.select("tr")[3].select("td")[1].text.strip(),
        "adrenaline_give": sur_tag.select("tr")[4]
        .select("td")[1]
        .text.strip(),
        "pills_give": sur_tag.select("tr")[5].select("td")[1].text.strip(),
        "first_aid_give": sur_tag.select("tr")[6].select("td")[1].text.strip(),
        "friend_up": sur_tag.select("tr")[7].select("td")[1].text.strip(),
        "diss_friend": sur_tag.select("tr")[8].select("td")[1].text.strip(),
        "save_friend": sur_tag.select("tr")[9].select("td")[1].text.strip(),
        "protect_friend": sur_tag.select("tr")[10]
        .select("td")[1]
        .text.strip(),
        "pro_from_smoker": sur_tag.select("tr")[11]
        .select("td")[1]
        .text.strip(),
        "pro_from_hunter": sur_tag.select("tr")[12]
        .select("td")[1]
        .text.strip(),
        "pro_from_charger": sur_tag.select("tr")[13]
        .select("td")[1]
        .text.strip(),
        "pro_from_jockey": sur_tag.select("tr")[14]
        .select("td")[1]
        .text.strip(),
        "melee_charge": sur_tag.select("tr")[15].select("td")[1].text.strip(),
        "tank_kill": sur_tag.select("tr")[16].select("td")[1].text.strip(),
        "witch_instantly_kill": sur_tag.select("tr")[17]
        .select("td")[1]
        .text.strip(),
    }
    inf_dict = {
        "sur_ace": inf_tag.select("tr")[0].select("td")[1].text.strip(),
        "sur_down": inf_tag.select("tr")[1].select("td")[1].text.strip(),
        "boommer_hit": inf_tag.select("tr")[2].select("td")[1].text.strip(),
        "hunter_prefect": inf_tag.select("tr")[3].select("td")[1].text.strip(),
        "hunter_success": inf_tag.select("tr")[4].select("td")[1].text.strip(),
        "tank_damage": inf_tag.select("tr")[5].select("td")[1].text.strip(),
        "charger_multiple": inf_tag.select("tr")[6]
        .select("td")[1]
        .text.strip(),
    }
# info_dict = cast(AnnePlayerInfo, info_dict)
# detail_dict = cast(AnnePlayerDetail, detail_tag)
# error_dict = cast(AnnePlayerError, error_tag)
# inf_avg_dict = cast(AnnePlayerInfAvg, inf_avg_dict)
# sur_dict = cast(AnnePlayerSur, sur_dict)
# inf_dict = cast(AnnePlayerInf, inf_dict)

# out_dict = {
#     "kill_msg": kill_tag.text if kill_tag is not None else "",
#     "info": info_dict,
#     "detail": detail_dict,
#     "inf_avg": inf_avg_dict,
#     "sur": sur_dict,
#     "inf": inf_dict,
#     "error": error_dict,
# }
