from src.domain.enumerations import ChannelMoods
from src.domain.entities.google_account import GoogleAccount

class Channel:
    name: str
    url: str
    google_account: GoogleAccount

