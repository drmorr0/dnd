from typing import List
from typing import Tuple

from bokeh.plotting import figure


def plot_ac(ac_list: List, d20_pts: List, pool_pts: List, title: str, y_range: Tuple[int, int]) -> figure:
    plot = figure(
        title=title,
        toolbar_location=None,
        width=300,
        height=200,
        y_range=y_range,
    )
    plot.grid.grid_line_color = None
    plot.xaxis.minor_tick_line_color = None
    plot.yaxis.minor_tick_line_color = None
    plot.xaxis.axis_label = "Opponent AC"
    plot.line(ac_list, d20_pts, color='red')
    plot.line(ac_list, pool_pts, color='navy')
    return plot
