from unittest import mock
from PIL import Image
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import RequestFactory, tag
from construbot.users.tests import utils, factories
from .context import ContextManager
from .utils import BasicAutocomplete, get_directory_path, get_object_403_or_404, \
    get_rid_of_company_kw, object_or_403, image_resize
# Create your tests here.


class ContextTests(utils.BaseTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_context_includes_user_groups(self):
        with mock.patch('django.urls.reverse') as reverse_mock:
            reverse_mock.return_value = '/fake/url/'
            reverse_mock.side_effect = 'fake/url/'
            view = ContextManager()
            view.user_groups = [
                'home', 'documentos', 'pendientes', 'proyectos'
            ]
            menu = view.get_menu()
            for obj in menu:
                self.assertTrue(
                    obj['title'].lower() in view.user_groups,
                    '%s is not in user_groups' % obj['title']
                )

    def test_context_includes_menu_specific_right_place_al_least_coordinator(self):
        with mock.patch('django.urls.reverse') as reverse_mock:
            reverse_mock.return_value = '/fake/url/'
            reverse_mock.side_effect = 'fake/url/'
            view = ContextManager()
            view.user_groups = [
                'users', 'documentos', 'pendientes', 'proyectos'
            ]
            menu_specific_obj = [{'title': 'fake'}, {'title': 'foo'}]
            view.menu_specific = menu_specific_obj
            view.app_label_name = 'Documentos'
            view.nivel_permiso_usuario = 2
            menu = view.get_menu()
            self.assertIn(menu_specific_obj[0], menu)
            self.assertEqual(menu.index(menu_specific_obj[0]), 3)

    def test_context_includes_menu_specific_not_there(self):
        with mock.patch('django.urls.reverse') as reverse_mock:
            reverse_mock.return_value = '/fake/url/'
            reverse_mock.side_effect = 'fake/url/'
            view = ContextManager()
            view.user_groups = [
                'users', 'documentos', 'pendientes', 'proyectos'
            ]
            menu_specific_obj = [{'title': 'fake'}, {'title': 'foo'}]
            view.menu_specific = menu_specific_obj
            view.app_label_name = 'Documentos'
            view.nivel_permiso_usuario = 1
            menu = view.get_menu()
            self.assertNotIn(menu_specific_obj[0], menu)


class BaseAutoCompleteTest(utils.BaseTestCase):

    def test_basic_autcomplete_returns_true_on_permissions(self):
        request = mock.Mock()
        instance = BasicAutocomplete()
        self.assertTrue(instance.has_add_permission(request))

    def test_get_key_words_returns_empty_obj(self):
        instance = BasicAutocomplete()
        with self.assertRaises(NotImplementedError):
            instance.get_key_words()

    @mock.patch.object(BasicAutocomplete, 'get_key_words')
    def test_autocomplete_get_queryset(self, mock_kw):
        mock_kw.return_value = {'mock_kw': 'bla'}
        instance = BasicAutocomplete()
        instance.request = mock.Mock()
        instance.q = 'string'
        instance.ordering = 'mock_ordering'
        instance.model = mock.Mock()
        instance.model.objects = mock.Mock()
        queryset_mock = mock.Mock()
        queryset_mock.order_by = mock.Mock()
        queryset_mock_instance = mock.Mock()
        queryset_mock.order_by.return_value = queryset_mock_instance
        filter_mock = mock.Mock()
        filter_mock.return_value = queryset_mock
        instance.model.objects.filter = filter_mock
        instance.model.objects.order_by = mock.Mock()
        qs = instance.get_queryset()
        instance.model.objects.filter.assert_called_with(**mock_kw())
        queryset_mock.order_by.assert_called_with('mock_ordering')
        self.assertEqual(qs, queryset_mock_instance)

    def test_autocomplete_on_post_returns_default_manager(self):
        instance = BasicAutocomplete()
        instance.request = mock.MagicMock()
        instance.model = mock.MagicMock()
        manager = mock.MagicMock()
        instance.model.objects = manager
        instance.q = None
        self.assertEqual(instance.get_queryset(), manager)

    def test_get_post_key_words(self):
        instance = BasicAutocomplete()
        self.assertDictEqual(instance.get_post_key_words(), {})

    @mock.patch.object(BasicAutocomplete, 'get_post_key_words')
    @mock.patch.object(BasicAutocomplete, 'get_queryset')
    def test_autocomplete_create_object(self, mock_queryset, post_kw_mock):
        instance = BasicAutocomplete()
        instance.create_field = 'hola'
        post_kw_mock.return_value = {'key': 'value'}
        manager = mock.MagicMock()
        mock_queryset.return_value = manager
        mock_create_method = mock.MagicMock()
        manager.create = mock_create_method
        instance.create_object('foo')
        self.assertEqual(instance.post_key_words, {'hola': 'foo', 'key': 'value'})
        self.assertTrue(post_kw_mock.called)
        manager.create.assert_called_with(**{'hola': 'foo', 'key': 'value'})


class Get_object_403_or_404Test(utils.BaseTestCase):

    @mock.patch('construbot.core.utils.shortcuts.get_object_or_404')
    def test_403_or_404_return_obj_instance(self, mock_404):
        model = mock.MagicMock()
        model_instance = mock.MagicMock()
        mock_404.return_value = model_instance
        obj = get_object_403_or_404(model, self.user)
        mock_404.assert_called_once()
        self.assertEqual(obj, model_instance)

    @mock.patch('construbot.core.utils.shortcuts.get_object_or_404')
    @mock.patch('construbot.core.utils.get_rid_of_company_kw')
    def test_403_or_404_raises_permission_denied(self, mock_get_rid, mock_404):
        model = mock.MagicMock()
        model.DoesNotExist = Http404
        mock_obj = mock.MagicMock()
        mock_obj.company = mock.MagicMock()
        mock_404.side_effect = [Http404, mock_obj]
        mock_get_rid.return_value = {'algo': 'algo'}
        kwargs = {'algo': 'algo', 'cliente__company': mock.MagicMock()}
        with self.assertRaises(PermissionDenied):
            get_object_403_or_404(model, self.user, **kwargs)
        mock_404.assert_any_call(model, **kwargs)
        mock_404.assert_any_call(model, algo='algo')
        self.assertEqual(mock_404.call_count, 2)
        mock_get_rid.assert_called_once_with(kwargs)

    @mock.patch('construbot.core.utils.shortcuts.get_object_or_404')
    def test_403_or_404_raises_404_no_company(self, mock_404):
        model = mock.MagicMock()
        model.DoesNotExist = Http404
        mock_404.side_effect = Http404
        kwargs = {'algo': 'algo', 'cliente__bla': mock.MagicMock()}
        with self.assertRaises(Http404):
            get_object_403_or_404(model, self.user, **kwargs)
        mock_404.assert_called_once()

    @mock.patch('construbot.core.utils.shortcuts.get_object_or_404')
    def test_403_or_404_raises_404_no_obj(self, mock_404):
        model = mock.MagicMock()
        _get = mock.MagicMock()
        _get.side_effect = Http404
        model.DoesNotExist = Http404
        model.objects = mock.MagicMock()
        model.objects.get = _get
        mock_404.side_effect = Http404
        kwargs = {'algo': 'algo', 'cliente__company': mock.MagicMock()}
        with self.assertRaises(Http404):
            get_object_403_or_404(model, self.user, **kwargs)
        self.assertEqual(mock_404.call_count, 2)


class Object_or_403(utils.BaseTestCase):

    def test_object_or_403_return_obj(self):
        obj = mock.Mock()
        company_1 = factories.CompanyFactory(customer=self.user.customer)
        company_2 = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company_1, company_2)
        self.user.currently_at = company_2
        obj.company = company_1
        test_obj = object_or_403(self.user, obj)
        self.assertEqual(obj, test_obj)
        self.assertEqual(company_1, self.user.currently_at)


class Object_or_403(utils.BaseTestCase):

    def test_object_or_403_return_obj(self):
        obj = mock.Mock()
        company_1 = factories.CompanyFactory(customer=self.user.customer)
        company_2 = factories.CompanyFactory(customer=self.user.customer)
        self.user.company.add(company_1, company_2)
        self.user.currently_at = company_2
        obj.company = company_1
        test_obj = object_or_403(self.user, obj)
        self.assertEqual(obj, test_obj)
        self.assertEqual(company_1, self.user.currently_at)


class Get_rid_of_company_kw(utils.BaseTestCase):

    def test_get_rid_gets_job_done(self):
        # We assume only company appears only once in kw
        bla_mock = mock.Mock()
        kwargs = {
            'cliente__bla__company': mock.Mock(),
            'bla__hola': bla_mock
        }
        kw = get_rid_of_company_kw(kwargs)
        kw_test = {'bla__hola': bla_mock}
        self.assertDictEqual(kw, kw_test)


class DirectoyPathTest(utils.BaseTestCase):

    @mock.patch('construbot.core.utils.strftime')
    def test_get_directory_path_returns_correct_string(self, mock_strftime):
        mock_strftime.return_value = '2018-06-15-17-28-49'
        mock_instance = mock.MagicMock()
        mock_instance._meta.verbose_name_plural = 'models'
        mock_instance.cliente.company.customer.customer_name = 'customer'
        mock_instance.cliente.company.customer.id = '12'
        mock_instance.cliente.company.company_name = 'company'
        path = get_directory_path(mock_instance, 'file.txt')
        self.assertEqual(path, '12-customer/company/models/2018-06-15-17-28-49-file.txt')


# class ImagereziseTest(utils.CBVTestCase):

#     def assertNotRaises(self, func, exception, message):
#         try:
#             func()
#         except exception:
#             self.fail(message)
#     @tag('current')
#     @mock.patch.object(Image, 'open')
#     def test_resize_image_with_rgba(self, mock_open):
#         im_mock = mock.Mock()
#         mock_open.return_value = im_mock
#         im_mock_save = mock.Mock(side_effect=OSError('RGBA'))
#         im_mock.save = im_mock_save
#         mock_image = mock.Mock()
#         mock_image.name = 'bla.jpeg'
#         image_resize(mock_image)
#         self.assertEqual(im_mock_save.call_count, 1)
