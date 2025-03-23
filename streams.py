import json
import requests 
import re
import asyncio
from teamEmoji import team_emojis
from bs4 import BeautifulSoup 
from discord_webhook import DiscordWebhook, DiscordEmbed
from nba_api.live.nba.endpoints import scoreboard 


with open("config.json") as f:
    config = json.load(f)
WEBHOOK_URL = config["webhookUrl"] 


def get_game_link(home_team, away_team):
    streameast_url = "https://the.streameast.app/nba/streams4"
    crackstreams_url = "https://crackstreams.cx/nbastreams/live1"
    onestream_url = "https://1stream.eu/nbastreams"
    methstreams_url = "https://methstreams.cx/nbastreams"

    streameast_link = None
    crackstreams_link = None
    onestream_link = None
    methstreams_link = None
    
    response = requests.get(streameast_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        games = soup.find_all("a", href=True)
        for game in games:
            link = game["href"]
            if 'nba/' in link and home_team.lower() in link.lower() and away_team.lower() in link.lower():
                streameast_link = f"{link}"
                break

    response = requests.get(onestream_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        games = soup.find_all("a", href=True)
        for game in games:
            link = game["href"]
            if home_team.lower() in link.lower() and away_team.lower() in link.lower():
                onestream_link = f"{link}"
                break

    response = requests.get(crackstreams_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        games = soup.find_all("a", href=True)
        for game in games:
            link = game["href"]
            if home_team.lower() in link.lower() and away_team.lower() in link.lower():
                crackstreams_link = f"{link}"
                break

    response = requests.get(methstreams_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        games = soup.find_all("a", href=True)
        for game in games:
            link = game["href"]
            if home_team.lower() in link.lower() and away_team.lower() in link.lower():
                methstreams_link = f"{link}"
                break
    
    return streameast_link, onestream_link, crackstreams_link, methstreams_link


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
                    seconds_left = 0

                home_team = game["homeTeam"]["teamName"]
                away_team = game["awayTeam"]["teamName"]
                home_score = int(game["homeTeam"]["score"])
                away_score = int(game["awayTeam"]["score"])
                score_diff = abs(home_score - away_score)

                home_emoji = team_emojis.get(home_team, {}).get("emoji", "")
                away_emoji = team_emojis.get(away_team, {}).get("emoji", "")

                if period == 4 and minutes_left <= 5 and seconds_left != 0 and score_diff <= 5:
                    print(f"Close game detected: {away_team} vs {home_team}")
                    webhook = DiscordWebhook(url=WEBHOOK_URL)
                    
                    embed = DiscordEmbed(
                        title="Close Game Alert!",
                        description=f"{away_emoji} **{away_team}** vs {home_emoji} **{home_team}**\nScore: **{away_score}-{home_score}**\n⏳ **{minutes_left}:{seconds_left:02d}** left in Q4!\n",
                        color="FF0000"
                    )
                    
                    streameast_link, onestream_link, crackstreams_link, methstreams_link = get_game_link(home_team, away_team)
                    if streameast_link and onestream_link and crackstreams_link and methstreams_link:
                        game_field = f"\n[Streameast]({streameast_link})\n[1Stream]({onestream_link})\n[Crackstreams]({crackstreams_link})\n[Methstreams]({methstreams_link})"
                        embed.add_embed_field(
                            name="Watch the game here: ",
                            value=f"{game_field}",
                            inline=True,
                        )
    
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