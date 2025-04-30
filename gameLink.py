import requests
from bs4 import BeautifulSoup

def find_game_link(soup, home_team, away_team):
    games = soup.find_all("a", href=True)
    for game in games:
        link = game["href"]
        if home_team.lower() in link.lower() and away_team.lower() in link.lower():
            return link
    return None

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
            response.raise_for_status() 
            soup = BeautifulSoup(response.text, "html.parser")
            link = find_game_link(soup, home_team, away_team)
            if link:
                stream_links[list(stream_links.keys())[i]] = link
        except requests.RequestException as e:
            print(f"⚠️ Could not fetch streams from {url}. Skipping... ({e})")
        except Exception as e:
            print(f"⚠️ An unexpected error occurred while processing {url}: {e}")
    return stream_links
