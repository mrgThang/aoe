# AOE
AOE game for Procon 2023

# How to run

- `cp env.example .env`
- Add token, game url, game id from server to `.env` file
- `python main.py`

# Game Guide
[How to play](how_to_play.pdf)

# Project structure
- `main.py` for init setup
- `map_controller.py` for window control
- `map_components.py` store components for map
- `map.py` for map control
- `services.py` for request to server
- `models.py` define models for request and reponse from server

# Next tasks

- Display craftsmen id
- Add logic to display territories
