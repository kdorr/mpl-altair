import parse_chart
import matplotlib
import altair
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from ._convert import _convert
from ._data import _normalize_data, _locate_channel_dtype, _locate_channel_data, _locate_channel_field, _convert_to_mpl_date
from ._axis import convert_axis


def convert(alt_chart):
    """Convert an altair encoding to a Matplotlib figure


    Parameters
    ----------
    chart
        The Altair chart object generated by Altair

    Returns
    -------
    mapping : dict
        Mapping from parts of the encoding to the Matplotlib artists.  This is
        for later customization.


    """
    chart = parse_chart.ChartMetadata(alt_chart)
    fig, ax = plt.subplots()
    if chart.mark in ['point', 'circle', 'square']:  # scatter
        _normalize_data(alt_chart)
        mapping = _convert(alt_chart)
        ax.scatter(**mapping)
        # convert_axis(ax, chart)
    elif chart.mark == 'line':  # line
        _normalize_data(alt_chart)
        _handle_line(chart, ax)
    else:
        raise NotImplementedError
    convert_axis(ax, alt_chart)
    fig.tight_layout()
    return fig, ax


def _handle_line(chart, ax):
    """Convert encodings, manipulate data if needed, plot on ax.

    Parameters
    ----------
    chart : altair.Chart
        The Altair chart object

    ax
        The Matplotlib axes object

    Notes
    -----
    Fill isn't necessary until mpl-altair can handle multiple plot types in one plot.
    Size is unsupported by both Matplotlib and Altair.
    When both Color and Stroke are provided, color is ignored and stroke is used.
    Shape is unsupported in line graphs unless another plot type is plotted at the same time.
    """
    groups = []
    kwargs = {}

    if chart.encoding['opacity']:
        groups.append('opacity')
    if chart.encoding['stroke']:
        groups.append('stroke')
    elif chart.encoding['color']:
        groups.append('color')

    list_fields = lambda c, g: [chart.encoding[i].field for i in g]
    try:
        for label, subset in chart.data.groupby(list_fields(chart, groups)):
            if 'opacity' in groups:
                kwargs['alpha'] = opacity_norm(chart, subset[chart.encoding['opacity'].field].iloc[0])

                if 'color' not in groups and 'stroke' not in groups:
                    kwargs['color'] = matplotlib.rcParams['lines.color']
            ax.plot(subset[chart.encoding['x'].field], subset[chart.encoding['y'].field], **kwargs)
    except ValueError:
        ax.plot(chart.encoding['x'].data, chart.encoding['y'].data)


def opacity_norm(chart, val):
    arr = chart.encoding['opacity'].data
    if chart.encoding['opacity'].type in ['ordinal', 'nominal', 'temporal']:
        unique, indices = np.unique(arr, return_inverse=True)
        arr = indices
        if chart.encoding['opacity'].type == "temporal":
            val = unique.tolist().index(_convert_to_mpl_date(val))
        else:
            val = unique.tolist().index(val)
    data_min, data_max = (arr.min(), arr.max())
    desired_min, desired_max = (0.15, 1)  # Chosen so that the minimum value is visible (aka nonzero)
    return ((val - data_min) / (data_max - data_min)) * (desired_max - desired_min) + desired_min
