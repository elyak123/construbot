main_menu = [
    {
        'title': 'Proyectos',
        'url': 'proyectos:proyect_dashboard',
        'always_appear': True,
        'urlkwargs': '',
        'icon': 'briefcase',
        'parent': False,
        'child': False,
    },
    {
        'title': 'Users',
        'url': 'users:list',
        'always_appear': False,
        'urlkwargs': None,
        'icon': 'key',
        'parent': False,
        'child': False,
    },
    {
        'title': 'Documentos',
        'url': 'oficios:Start',
        'always_appear': False,
        'urlkwargs': '',
        'icon': 'glyphicon glyphicon-folder-open',
        'parent': False,
        'child': False,
    },
    {
        'title': 'Pendientes',
        'url': 'pendientes:Tasklist',
        'always_appear': False,
        'urlkwargs': '',
        'icon': 'glyphicon glyphicon-check',
        'parent': False,
        'child': False,
        'group': 'Pendientes'
    },
]
