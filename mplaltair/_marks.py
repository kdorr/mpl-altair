import matplotlib
import numpy as np
from ._data import _locate_channel_field, _locate_channel_data, _locate_channel_dtype, _convert_to_mpl_date

def _handle_bar(chart, ax):
    """Convert encodings, manipulate data if needed, and plot the bar chart on the axes."""

    if _locate_channel_dtype(chart, 'y') == 'quantitative':
        if _locate_channel_dtype(chart, 'x') == 'quantitative' and _locate_channel_dtype(chart, 'y') != 'quantitative':
            _horizontal_bar(chart, ax)
        else:
            _vertical_bar(chart, ax)
    elif _locate_channel_dtype(chart, 'y') == ['nominal', 'ordinal']:
        if _locate_channel_dtype(chart, 'x') in ['nominal', 'ordinal']:
            _heatmap(chart, ax)
        else:
            _horizontal_bar(chart, ax)

def _horizontal_bar(chart, ax):
    raise NotImplementedError

def _vertical_bar(chart, ax):
    raise NotImplementedError

def _heatmap(chart, ax):
    raise NotImplementedError