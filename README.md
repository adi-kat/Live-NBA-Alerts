# Live NBA Close Game Tracker

This project is a Python-based script that tracks NBA games in real-time, using the NBA API to check live game scores and send notifications via a Discord webhook when a game is within 5 points with 5 minutes left in the fourth quarter.

<div align="center">
  <img src=https://github.com/user-attachments/assets/8d99b124-63aa-49dd-851a-be0c3da83a65>
</div>

## Features

- Track live NBA games and monitor scores in real-time.
- Notify users about close games (within 5 points and 5 minutes left) with a detailed Discord message.
- Automatically provides links to multiple streaming services (e.g., Streameast, 1Stream) for watching the game.
- Async, non-blocking, and efficient checking of game scores every 90 seconds.
- @Role tagging support – Notifies a specific Discord role (e.g., `@NBA Alerts`) when an alert is triggered, so only interested users are pinged.

## Prerequisites

Before running the project, ensure that you have:

- Python 3.7 or higher installed.
- A Discord Webhook URL (for notifications).
- The Discord Role ID you want to ping (you can get this by enabling Developer Mode in Discord, right-clicking the role, and selecting “Copy ID”).

## Installation

### Clone the repository

```bash
git clone https://github.com/yourusername/live-nba-close-game-tracker.git
cd live-nba-close-game-tracker
