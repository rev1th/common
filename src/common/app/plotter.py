import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# from cycler import cycler
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def add_traces(
        figure, data_struct, text_col: str = None,
        group: str = None, mode: str = None, name: str = '',
        showlegend: bool = True, **kwargs):
    if isinstance(data_struct, pd.DataFrame):
        xvalues = list(data_struct.index)
        col_id = 0
        for col in data_struct.columns:
            if col == text_col:
                continue
            figure.add_trace(
                go.Scatter(
                    x=xvalues,
                    y=data_struct[col],
                    customdata=data_struct[text_col],
                    hovertemplate = text_col+': %{customdata}<br>(%{x}, %{y})',
                    name=name+col,
                    mode=mode[col_id] if isinstance(mode, list) else mode,
                    legendgroup=group,
                    legendgrouptitle_text=group,
                    showlegend=showlegend,
                )
                if text_col else
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
            col_id += 1
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
                       text_col=text_col,
                       showlegend=showlegend, **kwargs)
    else:
        raise TypeError("Unrecognized datatype")
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

def get_figure(
        data, data2=None, title: str = 'Series',
        x_name: str = 'X', x_format: str = None,
        y_name: str = 'Y', y_format: str = None,
        y2_name: str = 'Y2', y2_format: str = None,
        text_col: str = None, mode: str = None, mode2: str = None,
        hovermode: str = None, legend: dict = None):
    if data2 is not None:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        add_traces(fig, data, mode=mode, text_col=text_col)
        add_traces(fig, data2, group=y2_name, mode=mode2, text_col=text_col, secondary_y=True)
    else:
        fig = go.Figure()
        add_traces(fig, data, mode=mode, text_col=text_col)
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
        legend=legend,
        # dict(groupclick='toggleitem', itemdoubleclick='toggleothers')
    )
    return fig

def plot_series(*args, **kwargs):
    get_figure(*args, **kwargs).show()

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

def get_figure_3d(
        data: pd.DataFrame, title: str = 'Series 3D',
        x_id: int = 0, x_format: str = '%d-%b-%Y',
        y_id: int = 1, y_format: str = None, z_name: str = 'Value',
        z_format: str = ',.3%', mesh_ids: list[int] = [2]):
    fig = go.Figure()
    data_cols = data.columns
    for z_id in range(len(data_cols)):
        if z_id == x_id or z_id == y_id:
            continue
        fig.add_trace(go.Scatter3d(
            name=data_cols[z_id],
            x=list(data[data_cols[x_id]]),
            y=list(data[data_cols[y_id]]),
            z=list(data[data_cols[z_id]]),
            mode='markers',
        ))
        if z_id in mesh_ids:
            fig.add_trace(go.Mesh3d(
                name=f'{data_cols[z_id]}-Mesh',
                x=list(data[data_cols[x_id]]),
                y=list(data[data_cols[y_id]]),
                z=list(data[data_cols[z_id]]),
            ))
    fig.update_layout(
        title_text=title,
        scene = dict(
            xaxis=dict(
                title=data_cols[x_id],
                tickformat=x_format,
                tickvals=list(data[data_cols[x_id]]),
                showspikes=False,
                autorange='reversed',
            ),
            yaxis=dict(
                title=data_cols[y_id],
                tickformat=y_format,
                showspikes=False,
            ),
            zaxis=dict(
                title=z_name,
                tickformat=z_format,
                nticks=5,
            ),
        ),
    )
    return fig
