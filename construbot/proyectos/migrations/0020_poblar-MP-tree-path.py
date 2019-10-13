# Generated by Django 2.1.9 on 2019-08-08 23:12
import string
from django.db import migrations
from treebeard.numconv import NumConv


def migration_inc_path(node):
    alphabet = ''.join(sorted(string.printable))
    """:returns: The path of the next sibling of a given node path."""
    # newpos = node._str2int(node.path[-node.steplen:]) + 1
    newpos = NumConv(len(alphabet), alphabet).str2int(node.path[-4:]) + 1
    # key = node._int2str(newpos)
    key = NumConv(len(alphabet), alphabet).int2str(newpos)
    # if len(key) > node.steplen:
    if len(key) > 4:
        raise Exception("Path Overflow from: '%s'" % (node.path, ))
    return '{0}{1}{2}'.format(
        # node.path[:-node.steplen],
        node.path[:-4],
        # node.alphabet[0] * (node.steplen - len(key)),
        alphabet[0] * (4 - len(key)),
        key
    )


def migration_get_root_nodes(cls):
    try:
        return cls.objects.filter(depth=1, path__isnull=False).order_by('-pk')[0]
    except IndexError:
        return None


def poblar_mp_contratos(apps, schema_editor):
    Contrato = apps.get_model('proyectos', 'Contrato')
    contratos = Contrato.objects.all().order_by('pk')
    current_path = ''
    for contrato in contratos:
        last_root = migration_get_root_nodes(Contrato)
        if last_root:
            current_path = migration_inc_path(last_root)
        else:
            current_path = '0001'
        contrato.path = current_path
        contrato.save()


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0019_MP-Node-path-opcional'),
    ]

    operations = [
        migrations.RunPython(poblar_mp_contratos),
    ]
