from Microsoft.Web.WebView2.WinForms import WebView2

from .base import SimpleProbe


class WebViewProbe(SimpleProbe):
    native_class = WebView2

    # https://github.com/MicrosoftEdge/WebView2Feedback/issues/530
    content_supports_url = False

    # https://github.com/MicrosoftEdge/WebView2Feedback/issues/983
    javascript_supports_exception = False

    async def get_page_content(self):
        return await self.impl.evaluate_javascript("document.body.innerHTML")
