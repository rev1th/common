
def get_dropdown_style(**kwargs):
    return {'width': '15%', **kwargs}

def get_div_style(**kwargs):
    return {'textAlign': 'center', 'padding-left':'1em', **kwargs}

def get_graph_style(height: int = 100, **kwargs):
    return {'height': f'{height}vh', **kwargs}

def get_form_style(**kwargs):
    return {'justifyContent': 'center', 'display': 'flex', **kwargs}

# _TABLE_KWARGS = dict(sort_action='native', sort_mode='multi', sort_by=[],
#                 filter_action='native')

def get_grid_style(page_size: int = 50, height: int = 900, **kwargs):
    grid_options = {
        'pagination': True, 'paginationPageSize': page_size, 'animateRows': False,
        'enableCellTextSelection': True,
    }
    return dict(
        defaultColDef = {'filter': True, 'floatingFilter': True},
        columnSize='sizeToFit',
        dashGridOptions=grid_options,
        style={'height': height},
        **kwargs
    )

def get_grid_number_format(fmt: str):
    return {'function': f"params.value == null ? '' :  d3.format('{fmt}')(params.value)"}
