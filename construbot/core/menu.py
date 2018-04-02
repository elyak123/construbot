main_menu = [
    {
        'title': 'Users',
        'icon': 'person',
        'submenu': [
            {
                'title': 'Mi usuario',
                'url': 'users:list',
                # 'urlkwargs': {'username': ''},
                'list': [
                    {
                        'title': 'url1',
                        'url': '',
                    },
                    {
                        'title': 'url2',
                        'url': '',
                    },
                    {
                        'title': 'url3',
                        'url': '',
                    },
                ]
            }, {
                'title': 'Listado',
                'url': 'users:list',
            }, {
                'title': 'Crear usuario',
                'url': 'users:new',
            },
        ]
    },
    {
        'title': 'Home',
        'url': 'home:index',
        'urlkwargs': None,
        'icon': 'glyphicon glyphicon-home',
        'parent': False,
        'child': False,
    },
    {
        'title': 'Documentos',
        'url': 'oficios:Start',
        'urlkwargs': '',
        'icon': 'glyphicon glyphicon-folder-open',
        'parent': False,
        'child': False,
    },
    {
        'title': 'Pendientes',
        'url': 'pendientes:Tasklist',
        'urlkwargs': '',
        'icon': 'glyphicon glyphicon-check',
        'parent': False,
        'child': False,
        'group': 'Pendientes'
    },
    {
        'title': 'Proyectos',
        'url': 'pmgt:pmgt_dashboard',
        'urlkwargs': '',
        'icon': 'glyphicon glyphicon-road',
        'parent': False,
        'child': False,
    },

]
