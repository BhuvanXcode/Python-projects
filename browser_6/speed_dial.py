from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QLineEdit, QScrollArea, QFrame,
                             QInputDialog, QMessageBox, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
import json
import os


class SpeedDialTile(QFrame):
    """A single speed dial tile."""
    
    clicked = pyqtSignal(str)  # Emits URL when clicked
    remove_requested = pyqtSignal(object)  # Emits self when remove is requested
    
    def __init__(self, url: str, title: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.title = title
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Thumbnail placeholder
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(200, 150)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px solid #d0d0d0;
                border-radius: 8px;
            }
        """)
        
        # Create simple thumbnail with first letter
        self.create_simple_thumbnail()
        
        layout.addWidget(self.thumbnail_label)
        
        # Title
        title_label = QLabel(self.title[:30] + "..." if len(self.title) > 30 else self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(title_label)
        
        # URL
        url_label = QLabel(self.url[:40] + "..." if len(self.url) > 40 else self.url)
        url_label.setAlignment(Qt.AlignCenter)
        url_label.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(url_label)
        
        self.setLayout(layout)
        
        # Styling
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QFrame:hover {
                background-color: #f9f9f9;
                border: 2px solid #4CAF50;
            }
        """)
        
        self.setCursor(Qt.PointingHandCursor)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def create_simple_thumbnail(self):
        """Create a simple thumbnail with the first letter."""
        pixmap = QPixmap(200, 150)
        pixmap.fill(QColor("#4CAF50"))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 72, QFont.Bold)
        painter.setFont(font)
        
        # Get first letter of title
        letter = self.title[0].upper() if self.title else "?"
        painter.drawText(pixmap.rect(), Qt.AlignCenter, letter)
        painter.end()
        
        self.thumbnail_label.setPixmap(pixmap)
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.url)
    
    def show_context_menu(self, position):
        """Show context menu."""
        menu = QMenu(self)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.clicked.emit(self.url))
        menu.addAction(open_action)
        
        open_new_tab_action = QAction("Open in New Tab", self)
        open_new_tab_action.triggered.connect(lambda: self.clicked.emit(self.url))
        menu.addAction(open_new_tab_action)
        
        menu.addSeparator()
        
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(lambda: self.remove_requested.emit(self))
        menu.addAction(remove_action)
        
        menu.exec_(self.mapToGlobal(position))


class SpeedDial(QWidget):
    """Speed dial homepage with frequently visited sites."""
    
    url_clicked = pyqtSignal(str)  # Emits URL when tile is clicked
    
    def __init__(self, storage_path: str = "browser_data", parent=None):
        super().__init__(parent)
        self.storage_path = storage_path
        self.speed_dial_file = os.path.join(storage_path, "speed_dial.json")
        self.tiles = []
        self.tile_widgets = []
        
        self._ensure_storage_exists()
        self.init_ui()
        self.load_tiles()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def init_ui(self):
        """Initialize the UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Speed Dial")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("+ Add Site")
        add_btn.clicked.connect(self.add_tile_dialog)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        header_layout.addWidget(add_btn)
        
        main_layout.addLayout(header_layout)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search or enter URL...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d0d0d0;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 16px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.search_input.returnPressed.connect(self.search_or_navigate)
        main_layout.addWidget(self.search_input)
        
        # Scroll area for tiles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Tiles container
        self.tiles_container = QWidget()
        self.tiles_layout = QGridLayout()
        self.tiles_layout.setSpacing(15)
        self.tiles_container.setLayout(self.tiles_layout)
        
        scroll.setWidget(self.tiles_container)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        
        # Background styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
    
    def load_tiles(self):
        """Load speed dial tiles from storage."""
        if os.path.exists(self.speed_dial_file):
            try:
                with open(self.speed_dial_file, 'r', encoding='utf-8') as f:
                    self.tiles = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.tiles = self.get_default_tiles()
        else:
            self.tiles = self.get_default_tiles()
        
        self.refresh_tiles()
    
    def get_default_tiles(self) -> list:
        """Get default speed dial tiles."""
        return [
            {"url": "https://www.google.com", "title": "Google"},
            {"url": "https://www.youtube.com", "title": "YouTube"},
            {"url": "https://www.github.com", "title": "GitHub"},
            {"url": "https://www.wikipedia.org", "title": "Wikipedia"},
            {"url": "https://www.reddit.com", "title": "Reddit"},
            {"url": "https://www.stackoverflow.com", "title": "Stack Overflow"},
        ]
    
    def save_tiles(self):
        """Save speed dial tiles to storage."""
        try:
            with open(self.speed_dial_file, 'w', encoding='utf-8') as f:
                json.dump(self.tiles, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving speed dial: {e}")
    
    def refresh_tiles(self):
        """Refresh the tile display."""
        # Clear existing widgets
        for widget in self.tile_widgets:
            widget.deleteLater()
        self.tile_widgets.clear()
        
        # Add tiles in grid (4 columns)
        columns = 4
        for i, tile_data in enumerate(self.tiles):
            row = i // columns
            col = i % columns
            
            tile = SpeedDialTile(tile_data['url'], tile_data['title'])
            tile.clicked.connect(self.url_clicked.emit)
            tile.remove_requested.connect(self.remove_tile)
            
            self.tiles_layout.addWidget(tile, row, col)
            self.tile_widgets.append(tile)
    
    def add_tile_dialog(self):
        """Show dialog to add a new tile."""
        url, ok1 = QInputDialog.getText(self, "Add Site", "Enter URL:")
        if not ok1 or not url:
            return
        
        title, ok2 = QInputDialog.getText(self, "Add Site", "Enter title:")
        if not ok2 or not title:
            title = url
        
        self.add_tile(url, title)
    
    def add_tile(self, url: str, title: str):
        """Add a new tile."""
        self.tiles.append({"url": url, "title": title})
        self.save_tiles()
        self.refresh_tiles()
    
    def remove_tile(self, tile_widget):
        """Remove a tile."""
        reply = QMessageBox.question(
            self, "Remove Site",
            f"Remove '{tile_widget.title}' from Speed Dial?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Find and remove from tiles list
            self.tiles = [t for t in self.tiles if t['url'] != tile_widget.url]
            self.save_tiles()
            self.refresh_tiles()
    
    def search_or_navigate(self):
        """Handle search/navigation from search bar."""
        text = self.search_input.text()
        if text:
            self.url_clicked.emit(text)
            self.search_input.clear()
