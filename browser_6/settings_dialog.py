from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
                             QCheckBox, QSpinBox, QFileDialog, QGroupBox, QFormLayout,
                             QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from browser_storage import SettingsManager


class SettingsDialog(QDialog):
    """Settings configuration dialog."""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Browser Settings")
        self.setMinimumSize(600, 500)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # General tab
        self.general_tab = self.create_general_tab()
        self.tabs.addTab(self.general_tab, "General")
        
        # Search tab
        self.search_tab = self.create_search_tab()
        self.tabs.addTab(self.search_tab, "Search")
        
        # Privacy tab
        self.privacy_tab = self.create_privacy_tab()
        self.tabs.addTab(self.privacy_tab, "Privacy")
        
        # Appearance tab
        self.appearance_tab = self.create_appearance_tab()
        self.tabs.addTab(self.appearance_tab, "Appearance")
        
        # Downloads tab
        self.downloads_tab = self.create_downloads_tab()
        self.tabs.addTab(self.downloads_tab, "Downloads")
        
        layout.addWidget(self.tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_general_tab(self) -> QWidget:
        """Create the general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Homepage group
        homepage_group = QGroupBox("Homepage")
        homepage_layout = QFormLayout()
        
        self.homepage_input = QLineEdit()
        self.homepage_input.setPlaceholderText("https://www.google.com")
        homepage_layout.addRow("Homepage URL:", self.homepage_input)
        
        homepage_group.setLayout(homepage_layout)
        layout.addWidget(homepage_group)
        
        # Startup group
        startup_group = QGroupBox("On Startup")
        startup_layout = QVBoxLayout()
        
        self.open_homepage_check = QCheckBox("Open homepage")
        self.open_homepage_check.setChecked(True)
        startup_layout.addWidget(self.open_homepage_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_search_tab(self) -> QWidget:
        """Create the search settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Search engine group
        search_group = QGroupBox("Default Search Engine")
        search_layout = QFormLayout()
        
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems(["Google", "DuckDuckGo", "Bing", "Yahoo"])
        search_layout.addRow("Search Engine:", self.search_engine_combo)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Search suggestions
        suggestions_group = QGroupBox("Search Suggestions")
        suggestions_layout = QVBoxLayout()
        
        self.enable_suggestions_check = QCheckBox("Show search suggestions")
        self.enable_suggestions_check.setChecked(True)
        suggestions_layout.addWidget(self.enable_suggestions_check)
        
        suggestions_group.setLayout(suggestions_layout)
        layout.addWidget(suggestions_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_privacy_tab(self) -> QWidget:
        """Create the privacy settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Privacy group
        privacy_group = QGroupBox("Privacy Settings")
        privacy_layout = QVBoxLayout()
        
        self.do_not_track_check = QCheckBox("Send 'Do Not Track' request")
        privacy_layout.addWidget(self.do_not_track_check)
        
        self.block_third_party_cookies_check = QCheckBox("Block third-party cookies")
        privacy_layout.addWidget(self.block_third_party_cookies_check)
        
        privacy_group.setLayout(privacy_layout)
        layout.addWidget(privacy_group)
        
        # Clear data group
        clear_data_group = QGroupBox("Clear Browsing Data")
        clear_data_layout = QVBoxLayout()
        
        clear_data_label = QLabel("Clear your browsing history, cookies, and cached data")
        clear_data_layout.addWidget(clear_data_label)
        
        self.clear_data_btn = QPushButton("Clear Data...")
        self.clear_data_btn.clicked.connect(self.show_clear_data_dialog)
        clear_data_layout.addWidget(self.clear_data_btn)
        
        clear_data_group.setLayout(clear_data_layout)
        layout.addWidget(clear_data_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_appearance_tab(self) -> QWidget:
        """Create the appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        self.dark_mode_check = QCheckBox("Enable dark mode")
        theme_layout.addWidget(self.dark_mode_check)
        
        self.show_bookmarks_bar_check = QCheckBox("Show bookmarks bar")
        self.show_bookmarks_bar_check.setChecked(True)
        theme_layout.addWidget(self.show_bookmarks_bar_check)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Zoom group
        zoom_group = QGroupBox("Zoom")
        zoom_layout = QFormLayout()
        
        self.default_zoom_spin = QSpinBox()
        self.default_zoom_spin.setRange(25, 500)
        self.default_zoom_spin.setValue(100)
        self.default_zoom_spin.setSuffix("%")
        zoom_layout.addRow("Default zoom level:", self.default_zoom_spin)
        
        zoom_group.setLayout(zoom_layout)
        layout.addWidget(zoom_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_downloads_tab(self) -> QWidget:
        """Create the downloads settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Download location group
        location_group = QGroupBox("Download Location")
        location_layout = QHBoxLayout()
        
        self.download_path_input = QLineEdit()
        self.download_path_input.setPlaceholderText("Default downloads folder")
        location_layout.addWidget(self.download_path_input)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_download_folder)
        location_layout.addWidget(self.browse_btn)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Download behavior group
        behavior_group = QGroupBox("Download Behavior")
        behavior_layout = QVBoxLayout()
        
        self.ask_download_location_check = QCheckBox("Ask where to save each file before downloading")
        behavior_layout.addWidget(self.ask_download_location_check)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_settings(self):
        """Load settings from the settings manager."""
        settings = self.settings_manager.get_all()
        
        # General
        self.homepage_input.setText(settings.get('homepage', 'https://www.google.com'))
        
        # Search
        search_engine = settings.get('search_engine', 'google')
        engine_map = {'google': 0, 'duckduckgo': 1, 'bing': 2, 'yahoo': 3}
        self.search_engine_combo.setCurrentIndex(engine_map.get(search_engine, 0))
        
        # Appearance
        self.dark_mode_check.setChecked(settings.get('dark_mode', False))
        self.show_bookmarks_bar_check.setChecked(settings.get('show_bookmarks_bar', True))
        self.default_zoom_spin.setValue(settings.get('default_zoom', 100))
        
        # Downloads
        self.download_path_input.setText(settings.get('download_path', ''))
    
    def apply_settings(self):
        """Apply the current settings."""
        # General
        self.settings_manager.set('homepage', self.homepage_input.text())
        
        # Search
        engine_map = {0: 'google', 1: 'duckduckgo', 2: 'bing', 3: 'yahoo'}
        search_engine = engine_map.get(self.search_engine_combo.currentIndex(), 'google')
        self.settings_manager.set('search_engine', search_engine)
        
        # Appearance
        self.settings_manager.set('dark_mode', self.dark_mode_check.isChecked())
        self.settings_manager.set('show_bookmarks_bar', self.show_bookmarks_bar_check.isChecked())
        self.settings_manager.set('default_zoom', self.default_zoom_spin.value())
        
        # Downloads
        self.settings_manager.set('download_path', self.download_path_input.text())
        
        # Emit signal
        self.settings_changed.emit(self.settings_manager.get_all())
    
    def accept_settings(self):
        """Apply settings and close dialog."""
        self.apply_settings()
        self.accept()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings_manager.reset_to_defaults()
            self.load_settings()
            QMessageBox.information(self, "Settings Reset", "All settings have been reset to defaults.")
    
    def browse_download_folder(self):
        """Browse for download folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Download Folder",
            self.download_path_input.text() or ""
        )
        
        if folder:
            self.download_path_input.setText(folder)
    
    def show_clear_data_dialog(self):
        """Show dialog to clear browsing data."""
        from PyQt5.QtWidgets import QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Clear Browsing Data")
        layout = QVBoxLayout()
        
        label = QLabel("Select the data you want to clear:")
        layout.addWidget(label)
        
        clear_history_check = QCheckBox("Browsing history")
        clear_history_check.setChecked(True)
        layout.addWidget(clear_history_check)
        
        clear_cookies_check = QCheckBox("Cookies and site data")
        layout.addWidget(clear_cookies_check)
        
        clear_cache_check = QCheckBox("Cached images and files")
        layout.addWidget(clear_cache_check)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Signal parent to clear data
            items_to_clear = []
            if clear_history_check.isChecked():
                items_to_clear.append('history')
            if clear_cookies_check.isChecked():
                items_to_clear.append('cookies')
            if clear_cache_check.isChecked():
                items_to_clear.append('cache')
            
            if items_to_clear:
                QMessageBox.information(
                    self, "Data Cleared",
                    f"The following data has been cleared: {', '.join(items_to_clear)}"
                )
