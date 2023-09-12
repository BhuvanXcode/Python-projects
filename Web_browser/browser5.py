from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QProgressBar, QTabWidget, QTabBar, QMenu, QAction, QShortcut, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon, QKeySequence
import sys

class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Browser")
        self.resize(800, 600)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)

        # Create navigation bar
        navigation_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.setShortcut("Ctrl+B")
        self.forward_button = QPushButton("Forward")
        self.forward_button.setShortcut("Ctrl+F")
        self.home_button = QPushButton("Home")
        self.url_input = QLineEdit()
        self.go_button = QPushButton("Go")
        self.go_button.setShortcut("Return")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setShortcut("Ctrl+R")
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setShortcut("Ctrl+T")
        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.bookmark_button = QPushButton("Bookmark")
        self.bookmarks_menu = QMenu()
        self.bookmarks_menu_button = QPushButton("Bookmarks")
        self.history_menu = QMenu()
        self.history_menu_button = QPushButton("History")
        self.incognito_mode_checkbox = QCheckBox("Incognito Mode")

        navigation_layout.addWidget(self.back_button)
        navigation_layout.addWidget(self.forward_button)
        navigation_layout.addWidget(self.home_button)
        navigation_layout.addWidget(self.url_input)
        navigation_layout.addWidget(self.go_button)
        navigation_layout.addWidget(self.refresh_button)
        navigation_layout.addWidget(self.new_tab_button)
        navigation_layout.addWidget(self.dark_mode_checkbox)
        navigation_layout.addWidget(self.bookmark_button)
        navigation_layout.addWidget(self.bookmarks_menu_button)
        navigation_layout.addWidget(self.history_menu_button)
        navigation_layout.addWidget(self.incognito_mode_checkbox)

        layout.addLayout(navigation_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tabs)

        self.setCentralWidget(container)

        self.back_button.clicked.connect(self.back)
        self.forward_button.clicked.connect(self.forward)
        self.home_button.clicked.connect(self.go_home)
        self.go_button.clicked.connect(self.load_url)
        self.refresh_button.clicked.connect(self.refresh)
        self.new_tab_button.clicked.connect(self.new_tab)
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        self.bookmark_button.clicked.connect(self.bookmark_current_page)
        self.bookmarks_menu_button.setMenu(self.bookmarks_menu)
        self.history_menu_button.setMenu(self.history_menu)

        # Create keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self, self.new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+Tab"), self, self.switch_to_next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, self.switch_to_previous_tab)

        self.show()

    def add_new_tab(self, url="https://www.google.com"):
        webview = QWebEngineView()
        webview.loadProgress.connect(self.update_progress)
        webview.urlChanged.connect(self.update_url)
        webview.titleChanged.connect(self.update_title)
        webview.page().profile().downloadRequested.connect(self.download_requested)
        webview.page().linkHovered.connect(self.link_hovered)
        webview.customContextMenuRequested.connect(self.context_menu_requested)

        index = self.tabs.addTab(webview, "New Tab")
        self.tabs.setCurrentIndex(index)

        self.url_input.setText(url)
        self.load_page(url)

        close_button = QPushButton("X")
        close_button.setStyleSheet("font-size: 8px; padding: 0; margin: 0;")
        close_button.clicked.connect(lambda: self.close_tab(index))
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, close_button)

        # Update bookmarks menu
        bookmark_action = QAction(url, self)
        bookmark_action.triggered.connect(lambda: self.load_page(url))
        self.bookmarks_menu.addAction(bookmark_action)

        # Connect fullscreen request signal
        webview.page().fullScreenRequested.connect(self.toggle_fullscreen)

    def new_tab(self):
        self.add_new_tab()

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        self.close_tab(current_index)

    def switch_to_next_tab(self):
        current_index = self.tabs.currentIndex()
        next_index = (current_index + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(next_index)

    def switch_to_previous_tab(self):
        current_index = self.tabs.currentIndex()
        previous_index = (current_index - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(previous_index)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_webview(self):
        return self.tabs.currentWidget()

    def load_page(self, url):
        if url.startswith("http://") or url.startswith("https://"):
            webview = self.current_webview()
            qurl = QUrl(url)
            webview.load(qurl)
            self.url_input.setText(url)
        else:
            query = QUrlQuery()
            query.addQueryItem("q", url)
            search_url = QUrl("https://www.google.com/search")
            search_url.setQuery(query)
            self.load_page(search_url.toString())

    def go_home(self):
        self.load_page("https://www.google.com")

    def load_url(self):
        url = self.url_input.text()
        self.load_page(url)

    def toggle_dark_mode(self, state):
        webview = self.current_webview()
        if state == Qt.Checked:
            self.setStyleSheet("background-color: #222; color: #fff;")
            webview.page().runJavaScript(
                """
                document.documentElement.style.backgroundColor = '#222';
                document.documentElement.style.color = '#fff';
                """
            )
        else:
            self.setStyleSheet("")
            webview.page().runJavaScript(
                """
                document.documentElement.style.backgroundColor = '';
                document.documentElement.style.color = '';
                """
            )

    def update_progress(self, progress):
        if progress < 100:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)

    def update_url(self, url):
        self.url_input.setText(url.toString())

    def update_title(self, title):
        index = self.tabs.currentIndex()
        self.tabs.setTabText(index, title)

    def back(self):
        webview = self.current_webview()
        webview.back()

    def forward(self):
        webview = self.current_webview()
        webview.forward()

    def refresh(self):
        webview = self.current_webview()
        webview.reload()

    def download_requested(self, download):
        download_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.path())
        if download_path:
            download.setPath(download_path)
            download.accept()

    def link_hovered(self, url):
        self.statusBar().showMessage(url)

    def context_menu_requested(self, pos):
        webview = self.current_webview()
        menu = QMenu(self)

        # Create context menu actions
        back_action = QAction("Back", self)
        forward_action = QAction("Forward", self)
        reload_action = QAction("Reload", self)
        open_action = QAction("Open in New Tab", self)

        # Connect actions to their respective slots
        back_action.triggered.connect(self.back)
        forward_action.triggered.connect(self.forward)
        reload_action.triggered.connect(self.refresh)
        open_action.triggered.connect(lambda: self.add_new_tab(webview.page().url().toString()))

        # Add actions to the menu
        menu.addAction(back_action)
        menu.addAction(forward_action)
        menu.addAction(reload_action)
        menu.addAction(open_action)

        menu.exec_(webview.mapToGlobal(pos))

    def bookmark_current_page(self):
        webview = self.current_webview()
        url = webview.page().url().toString()
        title = webview.page().title()

        bookmark_action = QAction(title, self)
        bookmark_action.triggered.connect(lambda: self.load_page(url))
        self.bookmarks_menu.addAction(bookmark_action)


    def load_history(self):
        # Load browsing history from storage and populate the history menu
        # Code to load history from storage goes here
        # For demonstration purposes, let's assume we have a list of URLs
        urls = [
            "https://www.google.com",
            "https://www.openai.com",
            "https://www.python.org",
        ]
        for url in urls:
            history_action = QAction(url, self)
            history_action.triggered.connect(lambda: self.load_page(url))
            self.history_menu.addAction(history_action)

    def load_bookmarks(self):
        # Load bookmarks from storage and populate the bookmarks menu
        # Code to load bookmarks from storage goes here
        # For demonstration purposes, let's assume we have a list of URLs and titles
        bookmarks = [
            {"url": "https://www.wikipedia.org", "title": "Wikipedia"},
            {"url": "https://www.github.com", "title": "GitHub"},
            {"url": "https://www.youtube.com", "title": "YouTube"},
        ]
        for bookmark in bookmarks:
            bookmark_action = QAction(bookmark["title"], self)
            bookmark_action.triggered.connect(lambda: self.load_page(bookmark["url"]))
            self.bookmarks_menu.addAction(bookmark_action)

    def toggle_fullscreen(self, request):
        if request.toggleOn():
            self.showFullScreen()
        else:
            self.showNormal()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.jfif"))  # Set the browser icon
    browser = WebBrowser()
    browser.add_new_tab()
    browser.load_history()
    browser.load_bookmarks()
    sys.exit(app.exec_())
