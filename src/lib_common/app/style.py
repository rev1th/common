
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

def get_grid_style(height: int = 800, page_size: int = None, **kwargs):
    grid_options = {
        'animateRows': False, 
        'enableCellTextSelection': True, 'rowSelection': 'multiple',
        'groupDisplayType': 'multipleColumns',
    }
    if page_size:
        grid_options.update({'pagination': True, 'paginationPageSize': page_size})
    return dict(
        defaultColDef = {'filter': True},
        columnSize='responsiveSizeToFit',
        dashGridOptions=grid_options,
        style={'height': height},
        **kwargs
    )

def get_grid_number_format(fmt: str):
    return {'function': f"params.value == null ? '' :  d3.format('{fmt}')(params.value)"}
