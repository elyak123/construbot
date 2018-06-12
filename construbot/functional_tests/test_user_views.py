from .functional_tests_base import FunctionalTest
from django.urls import reverse
from django.test import tag, override_settings

@tag("detail")
class TestCorrectDetailView(FunctionalTest):
    def test_correct_detail_view(self):
        self.user_login(self.user.username, "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario {0}')]".format(self.user.username)))
        self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario {0}')]".format(self.user.username))

    def test_join_to_another_user_detail(self):
        self.user_login(self.user.username, "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Users')]"))
        url = self.live_server_url + reverse('users:detail', kwargs={'username': self.user2.username})
        self.browser.get(url)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario {0}')]".format(self.user2.username)))
        self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario {0}')]".format(self.user2.username))

@tag("list")
class TestCorrectListView(FunctionalTest):
    def test_correct_list_view(self):
        self.user_login(self.user.username, "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Users')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Listado')]").click()
        for user in self.user, self.user2:
            self.browser.find_element_by_xpath("//a[contains(text(), '{0}')]".format(user.username))


@tag("edit")
class TestEditingUsers(FunctionalTest):
    def test_correct_edit_user(self):
        self.user_login(self.user.username, "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Users')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Listado')]").click()
        self.wait_for(lambda: self.browser.find_element_by_xpath("//a[@href='/users/~update/']"))
        self.browser.find_element_by_xpath("//a[@href='/users/~update/']").click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_username"))
        self.browser.find_element_by_id("id_username").clear()
        self.browser.find_element_by_id("id_username").send_keys("edited")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario edited')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario edited')]")
        self.browser.find_element_by_class_name("oi-caret-bottom").click()
        self.browser.find_element_by_class_name("oi-account-logout").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//button[@type='submit']").click())
        self.wait_for(lambda:self.browser.find_element_by_xpath("//div[contains(text(), 'You have signed out.')]"))
        self.user_login("edited", "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario edited')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario edited')]")


@tag("create")
class TestCorrectUserCreation(FunctionalTest):
    def test_correct_user_creation_and_login(self):
        self.user_login(self.user.username, "password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//*[contains(text(), 'Users')]"))
        self.browser.find_element_by_xpath("//*[contains(text(), 'Crear')]").click()
        self.wait_for(lambda:self.browser.find_element_by_id("id_groups"))
        self.fast_multiselect('id_groups', ['proyectos', 'users', 'Administrators'])
        self.browser.find_element_by_id("id_username").send_keys("TEST-USERNAME")
        self.browser.find_element_by_id("id_first_name").send_keys("TEST")
        self.browser.find_element_by_id("id_last_name").send_keys("USERNAME")
        self.browser.find_element_by_id("id_email").send_keys("a@a.com")
        self.fast_multiselect('id_company', ['{0}'.format(self.user.currently_at.company_name)])
        self.browser.find_element_by_id("id_password1").send_keys("000password")
        self.browser.find_element_by_id("id_password2").send_keys("000password")
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario TEST-USERNAME')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario TEST-USERNAME')]")
        self.browser.find_element_by_class_name("oi-caret-bottom").click()
        self.browser.find_element_by_class_name("oi-account-logout").click()
        self.wait_for(lambda:self.browser.find_element_by_xpath("//button[@type='submit']").click())
        self.wait_for(lambda:self.browser.find_element_by_xpath("//div[contains(text(), 'You have signed out.')]"))
        self.user_login("TEST-USERNAME", "000password")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario TEST-USERNAME')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario TEST-USERNAME')]")

    @override_settings(ACCOUNT_EMAIL_VERIFICATION='none')
    def test_create_admin_user(self):
        url = self.live_server_url
        self.browser.get(url)
        self.wait_for(lambda:self.browser.find_element_by_xpath("//a[@href='/accounts/signup/']"))
        self.browser.find_element_by_xpath("//a[@href='/accounts/signup/']").click()
        self.browser.find_element_by_id("id_email").send_keys("a@a.com")
        self.browser.find_element_by_id("id_username").send_keys("test_user")
        self.browser.find_element_by_id("id_password1").send_keys("somepass")
        self.browser.find_element_by_id("id_password2").send_keys("somepass")
        self.browser.find_element_by_id("id_first_name").send_keys("test")
        self.browser.find_element_by_id("id_last_name").send_keys("user")
        self.browser.find_element_by_id("id_company").send_keys("test_company")
        self.wait_for(lambda:self.browser.find_element_by_xpath("//button[@type='submit']").click())
        self.wait_for(lambda:self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario test_user')]"))
        self.browser.find_element_by_xpath("//h2[contains(text(), 'Detalle del usuario test_user')]")