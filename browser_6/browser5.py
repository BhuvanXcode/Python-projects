from PyQt5.QtCore import QUrl, Qt, QUrlQuery, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, 
                             QLineEdit, QPushButton, QCheckBox, QProgressBar, QTabWidget, 
                             QTabBar, QMenu, QAction, QShortcut, QMessageBox, QFileDialog,
                             QComboBox, QLabel, QStatusBar, QToolBar, QInputDialog, QSplitter,
                             QCompleter)
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtCore import QStringListModel
import sys
import os

# Import our custom modules
from browser_storage import BookmarkManager, HistoryManager, SettingsManager, ClosedTabsManager
from download_manager import DownloadManagerDialog
from settings_dialog import SettingsDialog
from screenshot_tool import ScreenshotTool
from ad_blocker import AdBlocker
from session_manager import SessionManager, TabGroupManager
from bookmarks_sidebar import BookmarksSidebar
from speed_dial import SpeedDial


class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Advanced Web Browser")
        self.resize(1400, 900)
        
        # Initialize managers
        self.bookmark_manager = BookmarkManager()
        self.history_manager = HistoryManager()
        self.settings_manager = SettingsManager()
        self.closed_tabs_manager = ClosedTabsManager()
        self.session_manager = SessionManager()
        self.tab_group_manager = TabGroupManager()
        self.ad_blocker = AdBlocker()
        
        # Download manager
        self.download_manager = DownloadManagerDialog(self)
        
        # Incognito mode profile
        self.incognito_profile = None
        self.is_incognito = False
        
        # Sidebar visibility
        self.sidebar_visible = False
        
        # Initialize UI
        self.init_ui()
        self.apply_settings()
        self.load_bookmarks()
        
        # Load last session if available
        if self.session_manager.has_last_session():
            self.restore_last_session()
        
        self.show()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Central widget with splitter for sidebar
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Bookmarks sidebar
        self.bookmarks_sidebar = BookmarksSidebar(self.bookmark_manager)
        self.bookmarks_sidebar.bookmark_clicked.connect(self.load_page)
        self.bookmarks_sidebar.setMaximumWidth(300)
        self.bookmarks_sidebar.setVisible(False)
        self.main_splitter.addWidget(self.bookmarks_sidebar)
        
        # Main browser area
        browser_container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        browser_container.setLayout(layout)
        
        # Create toolbar
        self.create_toolbar(layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: transparent;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        layout.addWidget(self.tabs)
        
        self.main_splitter.addWidget(browser_container)
        self.main_splitter.setStretchFactor(1, 1)
        
        self.setCentralWidget(self.main_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Ad blocker status
        self.ad_blocker_label = QLabel("🛡️ 0 ads blocked")
        self.status_bar.addPermanentWidget(self.ad_blocker_label)
        
        # Zoom label in status bar
        self.zoom_label = QLabel("100%")
        self.status_bar.addPermanentWidget(self.zoom_label)
        
        # Security indicator
        self.security_label = QLabel("🔒")
        self.status_bar.addPermanentWidget(self.security_label)
        
        # Create keyboard shortcuts
        self.create_shortcuts()
        
        # Apply modern styling
        self.apply_modern_style()
        
        # Update ad blocker display
        self.update_ad_blocker_status()
    
    def create_toolbar(self, layout):
        """Create the navigation toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        
        # Navigation buttons
        self.back_button = QPushButton("◀")
        self.back_button.setToolTip("Back (Ctrl+[)")
        self.back_button.clicked.connect(self.back)
        self.back_button.setFixedSize(35, 35)
        toolbar.addWidget(self.back_button)
        
        self.forward_button = QPushButton("▶")
        self.forward_button.setToolTip("Forward (Ctrl+])")
        self.forward_button.clicked.connect(self.forward)
        self.forward_button.setFixedSize(35, 35)
        toolbar.addWidget(self.forward_button)
        
        self.refresh_button = QPushButton("⟳")
        self.refresh_button.setToolTip("Refresh (Ctrl+R)")
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh_button.setFixedSize(35, 35)
        toolbar.addWidget(self.refresh_button)
        
        self.home_button = QPushButton("⌂")
        self.home_button.setToolTip("Home")
        self.home_button.clicked.connect(self.go_home)
        self.home_button.setFixedSize(35, 35)
        toolbar.addWidget(self.home_button)
        
        # URL bar with search engine selector
        url_container = QWidget()
        url_layout = QHBoxLayout()
        url_layout.setContentsMargins(5, 0, 5, 0)
        url_layout.setSpacing(5)
        
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems(["Google", "DuckDuckGo", "Bing", "Yahoo"])
        self.search_engine_combo.setToolTip("Select search engine")
        self.search_engine_combo.currentIndexChanged.connect(self.search_engine_changed)
        url_layout.addWidget(self.search_engine_combo)
        
        # Smart URL bar with autocomplete
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Search or enter URL...")
        self.url_input.returnPressed.connect(self.load_url)
        
        # Setup autocomplete
        self.url_completer = QCompleter()
        self.url_completer_model = QStringListModel()
        self.url_completer.setModel(self.url_completer_model)
        self.url_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.url_input.setCompleter(self.url_completer)
        
        url_layout.addWidget(self.url_input)
        
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.load_url)
        url_layout.addWidget(self.go_button)
        
        url_container.setLayout(url_layout)
        toolbar.addWidget(url_container)
        
        # Bookmark button
        self.bookmark_button = QPushButton("★")
        self.bookmark_button.setToolTip("Bookmark this page (Ctrl+D)")
        self.bookmark_button.clicked.connect(self.toggle_bookmark)
        self.bookmark_button.setFixedSize(35, 35)
        toolbar.addWidget(self.bookmark_button)
        
        # Sidebar toggle
        self.sidebar_button = QPushButton("📚")
        self.sidebar_button.setToolTip("Toggle bookmarks sidebar (Ctrl+B)")
        self.sidebar_button.clicked.connect(self.toggle_sidebar)
        self.sidebar_button.setFixedSize(35, 35)
        toolbar.addWidget(self.sidebar_button)
        
        # Screenshot button
        self.screenshot_button = QPushButton("📸")
        self.screenshot_button.setToolTip("Take screenshot (Ctrl+Shift+S)")
        self.screenshot_button.clicked.connect(self.take_screenshot)
        self.screenshot_button.setFixedSize(35, 35)
        toolbar.addWidget(self.screenshot_button)
        
        # Ad blocker toggle
        self.ad_blocker_button = QPushButton("🛡️")
        self.ad_blocker_button.setToolTip("Toggle ad blocker")
        self.ad_blocker_button.clicked.connect(self.toggle_ad_blocker)
        self.ad_blocker_button.setFixedSize(35, 35)
        self.ad_blocker_button.setCheckable(True)
        self.ad_blocker_button.setChecked(self.ad_blocker.enabled)
        toolbar.addWidget(self.ad_blocker_button)
        
        # Session menu
        self.session_button = QPushButton("💾")
        self.session_button.setToolTip("Session management")
        self.session_menu = QMenu()
        self.session_button.setMenu(self.session_menu)
        self.session_button.setFixedSize(35, 35)
        self.update_session_menu()
        toolbar.addWidget(self.session_button)
        
        # History menu
        self.history_menu_button = QPushButton("🕒")
        self.history_menu_button.setToolTip("Show history")
        self.history_menu = QMenu()
        self.history_menu_button.setMenu(self.history_menu)
        self.history_menu_button.setFixedSize(35, 35)
        toolbar.addWidget(self.history_menu_button)
        
        # Downloads button
        self.downloads_button = QPushButton("⬇")
        self.downloads_button.setToolTip("Show downloads")
        self.downloads_button.clicked.connect(self.show_downloads)
        self.downloads_button.setFixedSize(35, 35)
        toolbar.addWidget(self.downloads_button)
        
        # Settings button
        self.settings_button = QPushButton("⚙")
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        self.settings_button.setFixedSize(35, 35)
        toolbar.addWidget(self.settings_button)
        
        # New tab button
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setToolTip("New tab (Ctrl+T)")
        self.new_tab_button.clicked.connect(self.new_tab)
        self.new_tab_button.setFixedSize(35, 35)
        toolbar.addWidget(self.new_tab_button)
        
        # Incognito mode
        self.incognito_mode_checkbox = QCheckBox("🕵️")
        self.incognito_mode_checkbox.setToolTip("Enable incognito mode for new tabs")
        self.incognito_mode_checkbox.stateChanged.connect(self.toggle_incognito_mode)
        toolbar.addWidget(self.incognito_mode_checkbox)
        
        layout.addWidget(toolbar)
    
    def create_shortcuts(self):
        """Create keyboard shortcuts."""
        # Tab management
        QShortcut(QKeySequence("Ctrl+T"), self, self.new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+Shift+T"), self, self.reopen_closed_tab)
        QShortcut(QKeySequence("Ctrl+Tab"), self, self.switch_to_next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, self.switch_to_previous_tab)
        
        # Navigation
        QShortcut(QKeySequence("Ctrl+["), self, self.back)
        QShortcut(QKeySequence("Ctrl+]"), self, self.forward)
        QShortcut(QKeySequence("Ctrl+R"), self, self.refresh)
        QShortcut(QKeySequence("F5"), self, self.refresh)
        
        # Bookmarks
        QShortcut(QKeySequence("Ctrl+D"), self, self.toggle_bookmark)
        QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_sidebar)
        
        # Zoom
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.zoom_reset)
        
        # Find
        QShortcut(QKeySequence("Ctrl+F"), self, self.find_in_page)
        
        # Screenshot
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.take_screenshot)
        
        # Session
        QShortcut(QKeySequence("Ctrl+Shift+N"), self, self.save_current_session)
        
        # Address bar
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.url_input.setFocus())
        QShortcut(QKeySequence("Alt+D"), self, lambda: self.url_input.setFocus())
        
        # View source
        QShortcut(QKeySequence("Ctrl+U"), self, self.view_source)
    
    def apply_modern_style(self):
        """Apply modern styling to the browser."""
        style = """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
                spacing: 5px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #b0b0b0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                border-color: #4CAF50;
            }
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            QStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e0e0e0;
            }
            QCheckBox {
                spacing: 5px;
            }
        """
        self.setStyleSheet(style)
    
    def update_autocomplete(self):
        """Update URL autocomplete suggestions."""
        suggestions = []
        
        # Add bookmarks
        for bookmark in self.bookmark_manager.get_all_bookmarks():
            suggestions.append(bookmark['url'])
            suggestions.append(bookmark['title'])
        
        # Add recent history
        for entry in self.history_manager.get_recent_history(20):
            suggestions.append(entry['url'])
            suggestions.append(entry['title'])
        
        # Remove duplicates and update model
        suggestions = list(set(suggestions))
        self.url_completer_model.setStringList(suggestions)
    
    def add_new_tab(self, url="", use_speed_dial=True):
        """Add a new tab."""
        if not url and use_speed_dial:
            # Show speed dial
            speed_dial = SpeedDial()
            speed_dial.url_clicked.connect(self.load_page)
            
            index = self.tabs.addTab(speed_dial, "🏠 Speed Dial")
            self.tabs.setCurrentIndex(index)
            return speed_dial
        
        if not url:
            url = self.settings_manager.get('homepage', 'https://www.google.com')
        
        # Create webview with appropriate profile
        if self.is_incognito and self.incognito_mode_checkbox.isChecked():
            if self.incognito_profile is None:
                self.incognito_profile = QWebEngineProfile(self)
                self.incognito_profile.setHttpCacheType(QWebEngineProfile.NoCache)
                self.incognito_profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            webview = QWebEngineView()
            page = webview.page()
            page.setProfile(self.incognito_profile)
        else:
            webview = QWebEngineView()
        
        # Connect signals
        webview.loadProgress.connect(self.update_progress)
        webview.urlChanged.connect(self.update_url)
        webview.titleChanged.connect(self.update_title)
        webview.page().profile().downloadRequested.connect(self.download_requested)
        webview.page().linkHovered.connect(self.link_hovered)
        webview.page().fullScreenRequested.connect(self.toggle_fullscreen)
        
        # Add tab
        tab_title = "New Tab" if not self.incognito_mode_checkbox.isChecked() else "🕵️ Incognito"
        index = self.tabs.addTab(webview, tab_title)
        self.tabs.setCurrentIndex(index)
        
        # Load URL
        if url:
            self.url_input.setText(url)
            self.load_page(url)
        
        return webview
    
    def new_tab(self):
        """Create a new tab."""
        self.add_new_tab()
    
    def close_current_tab(self):
        """Close the current tab."""
        current_index = self.tabs.currentIndex()
        self.close_tab(current_index)
    
    def close_tab(self, index):
        """Close a tab at the given index."""
        if self.tabs.count() > 1:
            # Save to closed tabs
            widget = self.tabs.widget(index)
            if isinstance(widget, QWebEngineView):
                url = widget.url().toString()
                title = widget.title() or "Untitled"
                self.closed_tabs_manager.add_closed_tab(url, title)
            
            self.tabs.removeTab(index)
        else:
            # Last tab - create new one before closing
            self.new_tab()
            self.tabs.removeTab(index)
    
    def reopen_closed_tab(self):
        """Reopen the last closed tab."""
        tab_info = self.closed_tabs_manager.get_last_closed_tab()
        if tab_info:
            self.add_new_tab(tab_info['url'], use_speed_dial=False)
    
    def switch_to_next_tab(self):
        """Switch to the next tab."""
        current_index = self.tabs.currentIndex()
        next_index = (current_index + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(next_index)
    
    def switch_to_previous_tab(self):
        """Switch to the previous tab."""
        current_index = self.tabs.currentIndex()
        previous_index = (current_index - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(previous_index)
    
    def tab_changed(self, index):
        """Handle tab change."""
        widget = self.tabs.widget(index)
        if isinstance(widget, QWebEngineView):
            self.url_input.setText(widget.url().toString())
            self.update_bookmark_button()
        elif isinstance(widget, SpeedDial):
            self.url_input.setText("")
            self.bookmark_button.setText("☆")
    
    def current_webview(self):
        """Get the current webview."""
        widget = self.tabs.currentWidget()
        if isinstance(widget, QWebEngineView):
            return widget
        return None
    
    def load_page(self, url):
        """Load a page in the current tab."""
        # Check if current tab is speed dial
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, SpeedDial):
            # Replace speed dial with webview
            current_index = self.tabs.currentIndex()
            self.tabs.removeTab(current_index)
            self.add_new_tab(url, use_speed_dial=False)
            return
        
        webview = self.current_webview()
        if not webview:
            return
        
        # Check if it's a URL or search query
        if url.startswith("http://") or url.startswith("https://"):
            qurl = QUrl(url)
            webview.load(qurl)
            self.url_input.setText(url)
        elif "." in url and " " not in url:
            # Looks like a domain
            qurl = QUrl("https://" + url)
            webview.load(qurl)
            self.url_input.setText("https://" + url)
        else:
            # Search query
            search_url = self.settings_manager.get_search_url(url)
            qurl = QUrl(search_url)
            webview.load(qurl)
            self.url_input.setText(search_url)
    
    def load_url(self):
        """Load URL from the URL input."""
        url = self.url_input.text()
        self.load_page(url)
    
    def go_home(self):
        """Go to homepage or show speed dial."""
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, SpeedDial):
            return
        
        # Replace current tab with speed dial
        current_index = self.tabs.currentIndex()
        self.tabs.removeTab(current_index)
        self.add_new_tab(use_speed_dial=True)
    
    def back(self):
        """Go back."""
        webview = self.current_webview()
        if webview:
            webview.back()
    
    def forward(self):
        """Go forward."""
        webview = self.current_webview()
        if webview:
            webview.forward()
    
    def refresh(self):
        """Refresh the current page."""
        webview = self.current_webview()
        if webview:
            webview.reload()
    
    def update_progress(self, progress):
        """Update the progress bar."""
        if progress < 100:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)
    
    def update_url(self, url):
        """Update the URL bar."""
        url_string = url.toString()
        self.url_input.setText(url_string)
        
        # Update security indicator
        if url_string.startswith("https://"):
            self.security_label.setText("🔒 Secure")
        else:
            self.security_label.setText("⚠ Not Secure")
        
        # Add to history (not in incognito mode)
        if not self.incognito_mode_checkbox.isChecked():
            webview = self.current_webview()
            if webview:
                title = webview.title() or url_string
                self.history_manager.add_entry(url_string, title)
                self.update_history_menu()
                self.update_autocomplete()
        
        # Update bookmark button
        self.update_bookmark_button()
    
    def update_title(self, title):
        """Update the tab title."""
        index = self.tabs.currentIndex()
        if title:
            # Truncate long titles
            display_title = title[:30] + "..." if len(title) > 30 else title
            self.tabs.setTabText(index, display_title)
            self.setWindowTitle(f"{title} - Advanced Web Browser")
        else:
            self.tabs.setTabText(index, "Loading...")
    
    def toggle_bookmark(self):
        """Toggle bookmark for current page."""
        webview = self.current_webview()
        if not webview:
            return
        
        url = webview.url().toString()
        title = webview.title() or url
        
        if self.bookmark_manager.is_bookmarked(url):
            self.bookmark_manager.remove_bookmark(url)
            self.bookmark_button.setText("☆")
            self.status_bar.showMessage("Bookmark removed", 2000)
        else:
            self.bookmark_manager.add_bookmark(url, title)
            self.bookmark_button.setText("★")
            self.status_bar.showMessage("Bookmark added", 2000)
        
        self.load_bookmarks()
        self.bookmarks_sidebar.load_bookmarks()
        self.update_autocomplete()
    
    def update_bookmark_button(self):
        """Update bookmark button state."""
        webview = self.current_webview()
        if webview:
            url = webview.url().toString()
            if self.bookmark_manager.is_bookmarked(url):
                self.bookmark_button.setText("★")
            else:
                self.bookmark_button.setText("☆")
    
    def load_bookmarks(self):
        """Load bookmarks (kept for compatibility)."""
        self.update_autocomplete()
    
    def update_history_menu(self):
        """Update the history menu."""
        self.history_menu.clear()
        
        history = self.history_manager.get_recent_history(20)
        if not history:
            no_history_action = QAction("No history yet", self)
            no_history_action.setEnabled(False)
            self.history_menu.addAction(no_history_action)
        else:
            for entry in history:
                action = QAction(entry['title'], self)
                action.triggered.connect(lambda checked, url=entry['url']: self.load_page(url))
                self.history_menu.addAction(action)
        
        self.history_menu.addSeparator()
        
        # Clear history
        clear_action = QAction("Clear History...", self)
        clear_action.triggered.connect(self.clear_history)
        self.history_menu.addAction(clear_action)
    
    def clear_history(self):
        """Clear browsing history."""
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all browsing history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history_manager.clear_all()
            self.update_history_menu()
            self.update_autocomplete()
            QMessageBox.information(self, "History Cleared", "All browsing history has been cleared.")
    
    def download_requested(self, download):
        """Handle download request."""
        # Show download manager
        if not self.download_manager.isVisible():
            self.download_manager.show()
        
        # Add download to manager
        self.download_manager.add_download(download)
    
    def show_downloads(self):
        """Show the download manager."""
        self.download_manager.show()
        self.download_manager.raise_()
        self.download_manager.activateWindow()
    
    def link_hovered(self, url):
        """Show hovered link in status bar."""
        if url:
            self.status_bar.showMessage(url)
        else:
            self.status_bar.clearMessage()
    
    def toggle_fullscreen(self, request):
        """Toggle fullscreen mode."""
        if request.toggleOn():
            self.showFullScreen()
            request.accept()
        else:
            self.showNormal()
            request.accept()
    
    def toggle_incognito_mode(self, state):
        """Toggle incognito mode."""
        self.is_incognito = (state == Qt.Checked)
        if self.is_incognito:
            self.status_bar.showMessage("🕵️ Incognito mode enabled for new tabs", 3000)
        else:
            self.status_bar.showMessage("Incognito mode disabled", 3000)
    
    def search_engine_changed(self, index):
        """Handle search engine change."""
        engine_map = {0: 'google', 1: 'duckduckgo', 2: 'bing', 3: 'yahoo'}
        engine = engine_map.get(index, 'google')
        self.settings_manager.set('search_engine', engine)
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.settings_manager, self)
        dialog.settings_changed.connect(self.apply_settings)
        dialog.exec_()
    
    def apply_settings(self):
        """Apply settings from settings manager."""
        settings = self.settings_manager.get_all()
        
        # Apply search engine
        engine = settings.get('search_engine', 'google')
        engine_map = {'google': 0, 'duckduckgo': 1, 'bing': 2, 'yahoo': 3}
        self.search_engine_combo.setCurrentIndex(engine_map.get(engine, 0))
        
        # Apply dark mode
        if settings.get('dark_mode', False):
            self.apply_dark_mode()
        else:
            self.apply_modern_style()
    
    def apply_dark_mode(self):
        """Apply dark mode styling."""
        dark_style = """
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QToolBar {
                background-color: #2d2d2d;
                border-bottom: 1px solid #3d3d3d;
                padding: 5px;
                spacing: 5px;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 5px 10px;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #5d5d5d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                border-color: #4CAF50;
            }
            QLineEdit {
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QComboBox {
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 5px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
            }
            QTabBar::tab:hover {
                background-color: #4d4d4d;
            }
            QStatusBar {
                background-color: #2d2d2d;
                border-top: 1px solid #3d3d3d;
                color: #ffffff;
            }
            QCheckBox {
                spacing: 5px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """
        self.setStyleSheet(dark_style)
    
    def zoom_in(self):
        """Zoom in."""
        webview = self.current_webview()
        if webview:
            current_zoom = webview.zoomFactor()
            new_zoom = min(current_zoom + 0.1, 5.0)
            webview.setZoomFactor(new_zoom)
            self.zoom_label.setText(f"{int(new_zoom * 100)}%")
    
    def zoom_out(self):
        """Zoom out."""
        webview = self.current_webview()
        if webview:
            current_zoom = webview.zoomFactor()
            new_zoom = max(current_zoom - 0.1, 0.25)
            webview.setZoomFactor(new_zoom)
            self.zoom_label.setText(f"{int(new_zoom * 100)}%")
    
    def zoom_reset(self):
        """Reset zoom to 100%."""
        webview = self.current_webview()
        if webview:
            webview.setZoomFactor(1.0)
            self.zoom_label.setText("100%")
    
    def find_in_page(self):
        """Find text in page."""
        text, ok = QInputDialog.getText(self, "Find in Page", "Enter text to find:")
        if ok and text:
            webview = self.current_webview()
            if webview:
                webview.findText(text)
    
    def toggle_sidebar(self):
        """Toggle bookmarks sidebar."""
        self.sidebar_visible = not self.sidebar_visible
        self.bookmarks_sidebar.setVisible(self.sidebar_visible)
        
        if self.sidebar_visible:
            self.bookmarks_sidebar.load_bookmarks()
            self.status_bar.showMessage("Bookmarks sidebar shown", 2000)
        else:
            self.status_bar.showMessage("Bookmarks sidebar hidden", 2000)
    
    def take_screenshot(self):
        """Take a screenshot of the current page."""
        webview = self.current_webview()
        if not webview:
            QMessageBox.warning(self, "Screenshot", "No page to capture!")
            return
        
        # Capture visible area
        pixmap = ScreenshotTool.capture_visible_area(webview)
        
        # Show annotator
        ScreenshotTool.show_annotator(pixmap, self)
    
    def toggle_ad_blocker(self):
        """Toggle ad blocker on/off."""
        enabled = self.ad_blocker.toggle_enabled()
        self.ad_blocker_button.setChecked(enabled)
        
        if enabled:
            self.status_bar.showMessage("🛡️ Ad blocker enabled", 3000)
        else:
            self.status_bar.showMessage("Ad blocker disabled", 3000)
        
        self.update_ad_blocker_status()
    
    def update_ad_blocker_status(self):
        """Update ad blocker status display."""
        stats = self.ad_blocker.get_statistics()
        if stats['enabled']:
            self.ad_blocker_label.setText(f"🛡️ {stats['blocked_count']} ads blocked")
        else:
            self.ad_blocker_label.setText("🛡️ Disabled")
    
    def save_current_session(self):
        """Save the current session."""
        name, ok = QInputDialog.getText(self, "Save Session", "Session name:")
        if not ok or not name:
            return
        
        # Collect all tabs
        tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, QWebEngineView):
                url = widget.url().toString()
                title = widget.title() or url
                tabs.append({'url': url, 'title': title})
        
        if tabs:
            filename = self.session_manager.save_session(tabs, name)
            if filename:
                QMessageBox.information(self, "Session Saved", 
                                       f"Session '{name}' saved with {len(tabs)} tabs!")
                self.update_session_menu()
        else:
            QMessageBox.warning(self, "No Tabs", "No tabs to save!")
    
    def update_session_menu(self):
        """Update the session menu."""
        self.session_menu.clear()
        
        # Save current session
        save_action = QAction("💾 Save Current Session...", self)
        save_action.triggered.connect(self.save_current_session)
        self.session_menu.addAction(save_action)
        
        self.session_menu.addSeparator()
        
        # List saved sessions
        sessions = self.session_manager.get_all_sessions()
        if sessions:
            for session in sessions:
                action = QAction(f"{session['name']} ({session['tab_count']} tabs)", self)
                action.triggered.connect(lambda checked, s=session: self.restore_session(s['filename']))
                self.session_menu.addAction(action)
        else:
            no_sessions_action = QAction("No saved sessions", self)
            no_sessions_action.setEnabled(False)
            self.session_menu.addAction(no_sessions_action)
    
    def restore_session(self, filename):
        """Restore a saved session."""
        tabs = self.session_manager.load_session(filename)
        if not tabs:
            QMessageBox.warning(self, "Session Error", "Could not load session!")
            return
        
        reply = QMessageBox.question(
            self, "Restore Session",
            f"Restore session with {len(tabs)} tabs?\nCurrent tabs will be closed.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Close all current tabs
            while self.tabs.count() > 0:
                self.tabs.removeTab(0)
            
            # Open session tabs
            for tab in tabs:
                self.add_new_tab(tab['url'], use_speed_dial=False)
            
            self.status_bar.showMessage(f"Restored {len(tabs)} tabs", 3000)
    
    def restore_last_session(self):
        """Restore the last session."""
        tabs = self.session_manager.load_last_session()
        if tabs:
            for tab in tabs:
                self.add_new_tab(tab['url'], use_speed_dial=False)
    
    def view_source(self):
        """View page source."""
        webview = self.current_webview()
        if not webview:
            return
        
        webview.page().toHtml(lambda html: self.show_source_dialog(html))
    
    def show_source_dialog(self, html):
        """Show page source in a dialog."""
        from PyQt5.QtWidgets import QTextEdit, QDialog, QVBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Page Source")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setPlainText(html)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("font-family: 'Courier New'; font-size: 10pt;")
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def closeEvent(self, event):
        """Handle browser close event."""
        # Auto-save session
        tabs = []
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, QWebEngineView):
                url = widget.url().toString()
                title = widget.title() or url
                tabs.append({'url': url, 'title': title})
        
        if tabs:
            self.session_manager.auto_save(tabs)
        
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application icon if it exists
    icon_path = os.path.join(os.path.dirname(__file__), "icon.jfif")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    browser = WebBrowser()
    browser.add_new_tab()
    
    sys.exit(app.exec_())
