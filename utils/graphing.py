import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

import datetime
from typing import Sequence
from dataclasses import dataclass
from pathlib import Path

import discord

DIR_PATH = Path(f"/utils/plots")

@dataclass
class InstantaneousMetrics:
    """Represents all the data for the metrics stored for a particular datetime object. I like attribute lookup xD."""
    time: datetime.datetime
    counts: dict
    
    def total_count(self) -> int:
        return sum(self.counts.values())

    def clean_hours_repr(self) -> str:
        return self.time.strftime("%H:%M")    # returns in 00:00 format

    def clean_date_repr(self) -> str:
        return self.time.strftime("%d/%m/%Y")


def parse_data(db_response: dict) -> InstantaneousMetrics:
    """Convert the mongodb response dictionary into the dataclass instance.
    The dictionary is in the form `{datetime: <time inserted>, counts: <dict containing message count for each user>}`."""
    return InstantaneousMetrics(time=db_response["datetime"], counts=db_response["counts"])


def graph_hourly_message_count(data: Sequence[InstantaneousMetrics]) -> discord.Embed:
    date = data[0].time.strftime("%d%m%Y")
    first, last = data[0].time.strftime("%H"), data[-1].time.strftime("%H")
    file_name = f"{date}-{first}-{last}.png"

    file_path = DIR_PATH / file_name

    if file_path.exists():
        return make_discord_embed(file_name)
    else:
        fig, ax = plt.subplots()
        ax.set_title("Messages sent, hourly")
        ax.set_xlabel("Time")
        ax.set_ylabel("Messages")
        # x-axis time, y-axis message message count
        x_array = np.array([x.clean_hours_repr() for x in data])
        y_array = np.array([y.total_count() for y in data])

        ax.plot(x_array, y_array)
        fig.savefig(f"/utils/plots/{file_name}.png")     # saves file with name <date>-<first plotted hour>-<last plotted hour>
        plt.close(fig)
        return make_discord_embed(file_name)


def make_discord_embed(file_name: str) -> discord.Embed:
        file_for_discord = discord.File(DIR_PATH, file_name=file_name)
        embed = discord.Embed()
        embed.set_image(url=f"attachment://{file_name}")
        return embed