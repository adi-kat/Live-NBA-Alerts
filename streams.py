import json
import requests 
import re
import asyncio
from teamEmoji1 import team_emojis
from bs4 import BeautifulSoup 
from discord_webhook import DiscordWebhook, DiscordEmbed
from nba_api.live.nba.endpoints import scoreboard


with open("config.json") as f:
    config = json.load(f)
WEBHOOK_URL = config["webhookUrl"] 
ROLE_ID = config["roleId"]


async def parse_game_clock(clock_str):
    match = re.search(r"PT(\d+)M(\d+)\.\d+S", clock_str)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0

async def send_close_game_notification(game):
    home_team = game["homeTeam"]["teamName"]
    away_team = game["awayTeam"]["teamName"]
    home_score = int(game["homeTeam"]["score"])
    away_score = int(game["awayTeam"]["score"])
    minutes_left, seconds_left = await parse_game_clock(game.get("gameClock", "PT00M00.00S"))

    webhook = DiscordWebhook(
        url=WEBHOOK_URL,
        content=f"<@&{ROLE_ID}>",
        allowed_mentions={"roles": [ROLE_ID]}
    )

    embed = DiscordEmbed(
        title="Close Game Alert!",
        description=f"{team_emojis.get(away_team, {}).get('emoji', '')} **{away_team}** vs {team_emojis.get(home_team, {}).get('emoji', '')} **{home_team}**\nScore: **{away_score}-{home_score}**\n⏳ **{minutes_left}:{seconds_left:02d}** left in Q4!\n",
        color=int("FF0000", 16)
    )

    stream_links = get_game_link(home_team, away_team)
    if any(stream_links.values()):
        game_field = "\n".join(f"[{name}]({link})" for name, link in stream_links.items() if link)
        if game_field:
            embed.add_embed_field(
                name="Watch the game here: ",
                value=game_field,
                inline=True,
            )

    webhook.add_embed(embed)
    try:
        response = webhook.execute()
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending webhook for {away_team} vs {home_team}: {e}")

async def _is_close_game(game):
    period = game.get("period", 0)
    clock_str = game.get("gameClock", "PT00M00.00S")
    minutes_left, seconds_left = await parse_game_clock(clock_str)
    home_score = int(game["homeTeam"]["score"])
    away_score = int(game["awayTeam"]["score"])
    score_diff = abs(home_score - away_score)

    return (
        period == 4 and
        minutes_left <= 4 and
        seconds_left != 0 and
        score_diff <= 5
    )

async def _process_game(game, notified_games):
    game_id = game["gameId"]
    if game_id not in notified_games and await _is_close_game(game):
        print(f"Close game detected: {game['awayTeam']['teamName']} vs {game['homeTeam']['teamName']}")
        await send_close_game_notification(game)
        notified_games.add(game_id)

async def check_games():
    notified_games = set()

    while True:
        try:
            start = time.perf_counter()
            board = scoreboard.ScoreBoard()
            games = board.games.get_dict()
            tasks = [
                _process_game(game, notified_games.copy())  
                for game in games
            ]
            await asyncio.gather(*tasks)
            end = time.perf_counter()
            print(f"Checked {len(games)} games in {end - start:.2f} seconds.")
            print("Checked games, sleeping for 90 seconds...")
        except Exception as e:
            print(f"Error checking games: {e}")

        await asyncio.sleep(90)

if __name__ == "__main__":
    print("Starting NBA close game tracker...")
    asyncio.run(check_games())
