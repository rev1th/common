
import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from cycler import cycler
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def add_traces(figure, data_struct,
               y_col: str = None, text_col: str = None,
               group: str = 'G1', mode: str = None, name: str = '',
               showlegend: bool = True, **kwargs):
    if isinstance(data_struct, pd.DataFrame):
        xvalues = list(data_struct.index)
        if y_col and text_col:
            figure.add_trace(
                go.Scatter(
                    x=xvalues,
                    y=data_struct[y_col],
                    customdata=data_struct[text_col],
                    hovertemplate = text_col+': %{customdata}<br>(%{x}, %{y})',
                    name=name+y_col,
                    mode=mode,
                    legendgroup=group,
                    legendgrouptitle_text=group,
                    showlegend=showlegend,
                ),
                **kwargs
            )
            return
        for col in data_struct.columns:
            figure.add_trace(
                go.Scatter(
                    x=xvalues,
                    y=data_struct[col],
                    name=name+col,
                    mode=mode,
                    legendgroup=group,
                    legendgrouptitle_text=group,
                    showlegend=showlegend,
                ),
                **kwargs
            )
    elif isinstance(data_struct, pd.Series):
        figure.add_trace(
            go.Scatter(
                x=list(data_struct.index),
                y=list(data_struct.values),
                name=name,
                mode=mode,
                legendgroup=group,
                legendgrouptitle_text=group,
                showlegend=showlegend,
            ),
            **kwargs
        )
    elif isinstance(data_struct, dict):
        for k, v in data_struct.items():
            add_traces(figure, v, group=group, mode=mode, name=name+k,
                       y_col=y_col, text_col=text_col,
                       showlegend=showlegend, **kwargs)
    else:
        raise Exception("Unrecognized datatype")
    # if isinstance(v, pd.DataFrame):
    #     v.plot(ax=ax1)
    # elif isinstance(v, pd.Series):
    #     ax1.plot(v)
    # elif isinstance(v, dict):
    #     for kk, vv in v.items():
    #         ax1.plot(vv, label=kk)
    # else:
    #     raise Exception("Unrecognized datatype")
    # ax1.legend(loc=2)
    # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    #     ax2 = ax1.twinx()
    #     ax2.set_ylabel('Price')
    #     ax2.set_prop_cycle(cycler(color=['b', 'r', 'k', 'g', 'c', 'm', 'y']))

def get_figure(data, data2=None, title: str = 'Series',
                x_name: str = 'Time', x_format: str = '%H:%M',
                y_name: str = 'Price', y_format: str = None,
                y2_name: str = 'Spread', y2_format: str = None,
                y_col: str = None, text_col: str = None,
                hovermode: str = None):
    if data2 is not None:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        add_traces(fig, data, group=y_name, y_col=y_col, text_col=text_col)
        add_traces(fig, data2, group=y2_name, mode='lines',
                   y_col=y_col, text_col=text_col, secondary_y=True)
    else:
        fig = go.Figure()
        add_traces(fig, data)
    fig.update_layout(
        title_text=title,
        xaxis=dict(
            title=x_name,
            tickformat=x_format,
        ),
        yaxis=dict(
            title=y_name,
            tickformat=y_format,
        ),
        yaxis2=dict(
            title=y2_name,
            tickformat=y2_format,
        ),
        hovermode=hovermode,
    )
    return fig

def plot_series(data, data2=None, title: str = 'Series',
                x_name: str = 'Time', x_format: str = '%H:%M',
                y_name: str = 'Price', y_format: str = None,
                y2_name: str = 'Spread', y2_format: str = None,
                text_col: str = None, y_col: str = None,
                hovermode: str = None):
    get_figure(data, data2=data2, title=title,
               x_name=x_name, x_format=x_format,
               y_name=y_name, y_format=y_format,
               y2_name=y2_name, y2_format=y2_format,
               text_col=text_col, y_col=y_col,
               hovermode=hovermode).show()

def plot_series_multiple(data: dict[str, any], title: str = 'Multi plots',
                         x_name: str = 'Time', x_format: str = '%H:%M',
                         y_name: str = 'Price', y_format: str = None) -> None:
    titles = list(sorted(data.keys()))
    nc = 4
    nr = (len(data)-1)//nc + 1
    # _, axs = plt.subplots(nx, ny)
    fig = make_subplots(rows=nr, cols=nc, subplot_titles=titles)
    ni = 0
    for k in titles:
        add_traces(fig, data[k], group=k, row=ni//nc+1, col=ni%nc+1)
        # ax1 = axs[ni//ny, ni%ny]
        # ax1.set_title(k)
        ni += 1
    fig.update_layout(
        title_text=title,
        xaxis=dict(
            title=x_name,
            tickformat=x_format,
        ),
        yaxis=dict(
            title=y_name,
            tickformat=y_format,
        ),
    )
    fig.show()

def plot_series_3d(data: pd.DataFrame, data2 = None, title: str = 'Vol Surface',
                   x_id: int = 0, x_format: str = '%d-%b-%Y',
                   y_id: int = 1, z_id: int = 2, z_format: str = ',.2%') -> None:
    fig = go.Figure()
    data_cols = data.columns
    fig.add_trace(go.Mesh3d(
        name='Mesh',
        x=list(data[data_cols[x_id]]),
        y=list(data[data_cols[y_id]]),
        z=list(data[data_cols[z_id]]),
    ))
    fig.add_trace(go.Scatter3d(
        name='Nodes',
        x=list(data[data_cols[x_id]]),
        y=list(data[data_cols[y_id]]),
        z=list(data[data_cols[z_id]]),
        mode='markers',
    ))
    if data2 is not None:
        fig.add_trace(go.Scatter3d(
            name='Extra',
            x=list(data2[data_cols[x_id]]),
            y=list(data2[data_cols[y_id]]),
            z=list(data2[data_cols[z_id]]),
            mode='markers',
        ))
    fig.update_layout(
        title_text=title,
        scene = dict(
            xaxis=dict(
                title=data_cols[x_id],
                tickformat=x_format,
                tickvals=list(data[data_cols[x_id]]),
                showspikes=False,
            ),
            yaxis=dict(
                title=data_cols[y_id],
                showspikes=False,
            ),
            zaxis=dict(
                title=data_cols[z_id],
                tickformat=z_format,
                nticks=5,
            ),
        ),
    )
    fig.show()
