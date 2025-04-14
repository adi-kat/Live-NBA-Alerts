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


def get_game_link(home_team, away_team):
    stream_urls = [
        "https://the.streameast.app/nba/streams4",
        "https://crackstreams.cx/nbastreams/live1",
        "https://1stream.eu/nbastreams",
        "https://methstreams.cx/nbastreams"
    ]

    stream_links = {
        "Streameast": None,
        "Crackstreams": None,
        "Onestream": None,
        "Methstreams": None
    }

    for i, url in enumerate(stream_urls):
        try: 
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                games = soup.find_all("a", href=True)
                for game in games:
                    link = game["href"]
                    if home_team.lower() in link.lower() and away_team.lower() in link.lower():
                        stream_links[list(stream_links.keys())[i]] = link 
                        break
        except requests.RequestException as e: 
            print(f"Error fetching stream links for {url}: {e}")
    return stream_links


async def check_games():
    notified_games = set()
    
    while True:
        try:
            board = scoreboard.ScoreBoard()
            games = board.games.get_dict()

            for game in games:
                game_id = game["gameId"]
                period = game.get("period", 0)

                if game_id in notified_games:
                    continue 
                
                clock_str = game.get("gameClock", "PT00M00.00S")  
                match = re.search(r"PT(\d+)M(\d+)\.\d+S", clock_str)

                if match:
                    minutes_left = int(match.group(1))
                    seconds_left = int(match.group(2))
                else:
                    minutes_left = 0
                    seconds_left = 00

                home_team = game["homeTeam"]["teamName"]
                away_team = game["awayTeam"]["teamName"]
                home_score = int(game["homeTeam"]["score"])
                away_score = int(game["awayTeam"]["score"])
                score_diff = abs(home_score - away_score)

                home_emoji = team_emojis.get(home_team, {}).get("emoji", "")
                away_emoji = team_emojis.get(away_team, {}).get("emoji", "")

                if period == 4 and minutes_left <= 4 and seconds_left != 0 and score_diff <= 5:
                    print(f"Close game detected: {away_team} vs {home_team}")
                    
                    webhook = DiscordWebhook(url=WEBHOOK_URL)
                    
                    embed = DiscordEmbed(
                        title="Close Game Alert!",
                        description=f"{away_emoji} **{away_team}** vs {home_emoji} **{home_team}**\nScore: **{away_score}-{home_score}**\n⏳ **{minutes_left}:{seconds_left:02d}** left in Q4!\n",
                        color="FF0000"
                    )

                    stream_links = get_game_link(home_team, away_team)

                    if any(stream_links.values()): 
                        game_field = ""
                        for name, link in stream_links.items():
                            if link:
                                game_field += f"\n[{name}]({link})"
                        if game_field:
                            embed.add_embed_field(
                                name="Watch the game here: ",
                                value=f"{game_field}",
                                inline=True, )
                        
                    webhook.add_embed(embed)
                    response = webhook.execute()
            
                    notified_games.add(game_id)
                    
            print("Checked games, sleeping for 90 seconds...")
        except Exception as e:
            print(f"Error checking games: {e}")
            
        await asyncio.sleep(90)

if __name__ == "__main__":
    print("Starting NBA close game tracker...")
    asyncio.run(check_games())
