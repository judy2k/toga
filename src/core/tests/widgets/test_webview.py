import toga
import toga_dummy
from toga_dummy.utils import EventLog, TestCase


class WebViewTests(TestCase):
    def setUp(self):
        super().setUp()

        self.url = 'https://pybee.org/'

        def callback(widget):
            pass

        self.on_key_down = callback
        self.web_view = toga.WebView(url=self.url,
                                     on_key_down=self.on_key_down,
                                     factory=toga_dummy.factory)

    def test_widget_created(self):
        self.assertEqual(self.web_view._impl.interface, self.web_view)
        self.assertActionPerformed(self.web_view, 'create WebView')

    def test_setting_url_invokes_impl_method(self):
        new_url = 'https://github.com/'
        self.web_view.url = new_url
        self.assertEqual(self.web_view.url, new_url)
        self.assertValueSet(self.web_view, 'url', new_url)

    def test_set_content_invokes_impl_method(self):
        root_url = 'https://github.com/'
        new_content = """<!DOCTYPE html>
            <html>
              <body>
                <h1>My First Heading</h1>
                <p>My first paragraph.</p>
              </body>
            </html>
        """

        self.web_view.set_content(root_url, new_content)
        self.assertActionPerformedWith(self.web_view, 'set content', root_url=root_url, content=new_content)