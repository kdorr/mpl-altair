import matplotlib
import altair
import matplotlib.pyplot as plt
from ._convert import _convert
from ._data import _normalize_data
from ._axis import convert_axis


def convert(chart):
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

    fig, ax = plt.subplots()
    if chart.mark in ['point', 'circle', 'square']:  # scatter
        _normalize_data(chart)
        mapping = _convert(chart)
        ax.scatter(**mapping)
        # convert_axis(ax, chart)
    elif chart.mark == 'line':  # line
        _normalize_data(chart)
        _line_division(chart, ax)
    else:
        raise NotImplementedError
    convert_axis(ax, chart)
    fig.tight_layout()
    return fig, ax


def _line_division(chart, ax):
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
    Opacity still needs to be implemented.
    """
    if chart.to_dict()['encoding'].get('opacity'):
        raise NotImplementedError("Still need to implement.")
        # dtype = _locate_channel_dtype(chart, 'opacity')
        # normalize opacity values to (0,1)
        # mapping['kwargs'] = {'alpha': normalized_vals}  # ish (not really going to work)

    if chart.to_dict()['encoding'].get('stroke'):
        grouping = chart.to_dict()['encoding']['stroke']['field']
    elif chart.to_dict()['encoding'].get('color'):  # If both color and stroke are encoded, color is ignored.
        grouping = chart.to_dict()['encoding']['color']['field']
    else:
        mapping = _convert(chart)
        ax.plot(*mapping['args'])
        # convert_axis(ax, chart)
        return

    for lab, subset in chart.data.groupby(grouping):
        tmp_chart = chart
        tmp_chart.data = subset
        mapping = _convert(tmp_chart)
        mapping['kwargs'] = {'label': lab}  # for legend purposes later on
        ax.plot(*mapping['args'], **mapping['kwargs'])
        # convert_axis(ax, chart)