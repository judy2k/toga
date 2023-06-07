import json
import webbrowser

from travertino.size import at_least

import toga
from toga.widgets.webview import JavaScriptResult
from toga_winforms.libs import (
    Action,
    Color,
    CoreWebView2CreationProperties,
    String,
    Task,
    TaskScheduler,
    Uri,
    WebView2,
    WebView2RuntimeNotFoundException,
    WinForms,
)

from .base import Widget


def requires_corewebview2(method):
    def wrapper(self, *args, **kwargs):
        def task():
            method(self, *args, **kwargs)

        if self.corewebview2_available:
            task()
        else:
            self.pending_tasks.append(task)

    return wrapper


class WebView(Widget):
    def create(self):
        self.native = WebView2()
        self.native.CoreWebView2InitializationCompleted += (
            self.winforms_initialization_completed
        )
        self.native.NavigationCompleted += self.winforms_navigation_completed
        self.loaded_future = None

        props = CoreWebView2CreationProperties()
        props.UserDataFolder = str(toga.App.app.paths.cache / "WebView2")
        self.native.CreationProperties = props

        # Trigger the configuration of the webview
        self.corewebview2_available = None
        self.pending_tasks = []
        self.native.EnsureCoreWebView2Async(None)
        self.native.DefaultBackgroundColor = Color.Transparent

    def winforms_initialization_completed(self, sender, args):
        # The WebView2 widget has an "internal" widget (CoreWebView2) that is
        # the actual web view. The view isn't ready until the internal widget has
        # completed initialization, and that isn't done until an explicit
        # request is made (EnsureCoreWebView2Async).
        if args.IsSuccess:
            # We've initialized, so we must have the runtime
            self.corewebview2_available = True
            settings = self.native.CoreWebView2.Settings
            self.default_user_agent = settings.UserAgent

            debug = True
            settings.AreDefaultContextMenusEnabled = debug
            settings.AreDefaultScriptDialogsEnabled = True
            settings.AreDevToolsEnabled = debug
            settings.IsBuiltInErrorPageEnabled = True
            settings.IsScriptEnabled = True
            settings.IsWebMessageEnabled = True
            settings.IsStatusBarEnabled = debug
            settings.IsZoomControlEnabled = True

            for task in self.pending_tasks:
                task()
            self.pending_tasks = None

        elif isinstance(
            args.InitializationException, WebView2RuntimeNotFoundException
        ):  # pragma: nocover
            print("Could not find the Microsoft Edge WebView2 Runtime.")
            if self.corewebview2_available is None:
                # The initialize message is sent twice on failure.
                # We only want to show the dialog once, so track that we
                # know the runtime is missing.
                self.corewebview2_available = False
                WinForms.MessageBox.Show(
                    "The Microsoft Edge WebView2 Runtime is not installed. "
                    "Web content will not be displayed.\n\n"
                    "Click OK to download the WebView2 Evergreen Runtime "
                    "Bootstrapper from Microsoft.",
                    "Missing Edge Webview2 runtime",
                    WinForms.MessageBoxButtons.OK,
                    WinForms.MessageBoxIcon.Error,
                )
                webbrowser.open(
                    "https://developer.microsoft.com/en-us/microsoft-edge/webview2/#download-section"
                )

        else:  # pragma: nocover
            raise RuntimeError(args.InitializationException)

    def winforms_navigation_completed(self, sender, args):
        self.interface.on_webview_load(self.interface)

        if self.loaded_future:
            self.loaded_future.set_result(None)
            self.loaded_future = None

    def get_url(self):
        source = self.native.Source
        if source is None:  # pragma: nocover
            return None  # CoreWebView2 is not yet initialized.
        else:
            url = str(source)
            return None if url == "about:blank" else url

    @requires_corewebview2
    def set_url(self, value, future=None):
        self.loaded_future = future
        if value is None:
            self.set_content("about:blank", "")
        else:
            self.native.Source = Uri(value)

    @requires_corewebview2
    def set_content(self, root_url, content):
        self.native.NavigateToString(content)

    def get_user_agent(self):
        cwv = self.native.CoreWebView2
        return cwv.Settings.UserAgent if cwv else ""

    @requires_corewebview2
    def set_user_agent(self, value):
        self.native.CoreWebView2.Settings.UserAgent = (
            self.default_user_agent if value is None else value
        )

    def evaluate_javascript(self, javascript, on_result=None):
        result = JavaScriptResult()
        task_scheduler = TaskScheduler.FromCurrentSynchronizationContext()

        def callback(task):
            value = json.loads(task.Result)
            result.future.set_result(value)
            if on_result:
                on_result(value)

        self.native.ExecuteScriptAsync(javascript).ContinueWith(
            Action[Task[String]](callback), task_scheduler
        )

        return result

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)
