from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                             QTreeWidgetItem, QLineEdit, QPushButton, QMenu, 
                             QAction, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from browser_storage import BookmarkManager


class BookmarksSidebar(QWidget):
    """Sidebar widget for bookmark management."""
    
    bookmark_clicked = pyqtSignal(str)  # Emits URL when bookmark is clicked
    
    def __init__(self, bookmark_manager: BookmarkManager, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.folders = {}  # folder_name -> list of bookmark indices
        self.init_ui()
        self.load_bookmarks()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search bookmarks...")
        self.search_input.textChanged.connect(self.filter_bookmarks)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Bookmark tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemDoubleClicked.connect(self.item_double_clicked)
        layout.addWidget(self.tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_folder_btn = QPushButton("+ Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        button_layout.addWidget(add_folder_btn)
        
        refresh_btn = QPushButton("⟳")
        refresh_btn.setToolTip("Refresh")
        refresh_btn.clicked.connect(self.load_bookmarks)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Styling
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:hover {
                background-color: #f0f0f0;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #000000;
            }
        """)
    
    def load_bookmarks(self):
        """Load bookmarks into the tree."""
        self.tree.clear()
        
        bookmarks = self.bookmark_manager.get_all_bookmarks()
        
        if not bookmarks:
            item = QTreeWidgetItem(["No bookmarks yet"])
            item.setFlags(Qt.ItemIsEnabled)
            self.tree.addTopLevelItem(item)
            return
        
        # Create "All Bookmarks" folder
        all_folder = QTreeWidgetItem(["📁 All Bookmarks"])
        all_folder.setExpanded(True)
        self.tree.addTopLevelItem(all_folder)
        
        for bookmark in bookmarks:
            item = QTreeWidgetItem([f"🔖 {bookmark['title']}"])
            item.setData(0, Qt.UserRole, bookmark['url'])
            item.setToolTip(0, bookmark['url'])
            all_folder.addChild(item)
        
        # Add custom folders (placeholder for future enhancement)
        # This would require extending BookmarkManager to support folders
    
    def filter_bookmarks(self, text):
        """Filter bookmarks by search text."""
        if not text:
            # Show all
            for i in range(self.tree.topLevelItemCount()):
                self.show_all_children(self.tree.topLevelItem(i))
            return
        
        text_lower = text.lower()
        
        for i in range(self.tree.topLevelItemCount()):
            folder = self.tree.topLevelItem(i)
            has_visible_child = False
            
            for j in range(folder.childCount()):
                child = folder.child(j)
                bookmark_text = child.text(0).lower()
                url = child.data(0, Qt.UserRole) or ""
                
                if text_lower in bookmark_text or text_lower in url.lower():
                    child.setHidden(False)
                    has_visible_child = True
                else:
                    child.setHidden(True)
            
            folder.setHidden(not has_visible_child)
            if has_visible_child:
                folder.setExpanded(True)
    
    def show_all_children(self, item):
        """Show all children of an item."""
        item.setHidden(False)
        for i in range(item.childCount()):
            child = item.child(i)
            child.setHidden(False)
    
    def item_double_clicked(self, item, column):
        """Handle item double click."""
        url = item.data(0, Qt.UserRole)
        if url:
            self.bookmark_clicked.emit(url)
    
    def show_context_menu(self, position):
        """Show context menu for bookmarks."""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        url = item.data(0, Qt.UserRole)
        if not url:
            return
        
        menu = QMenu(self)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.bookmark_clicked.emit(url))
        menu.addAction(open_action)
        
        open_new_tab_action = QAction("Open in New Tab", self)
        open_new_tab_action.triggered.connect(lambda: self.bookmark_clicked.emit(url))
        menu.addAction(open_new_tab_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_bookmark(url, item))
        menu.addAction(delete_action)
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))
    
    def delete_bookmark(self, url, item):
        """Delete a bookmark."""
        reply = QMessageBox.question(
            self, "Delete Bookmark",
            "Are you sure you want to delete this bookmark?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.bookmark_manager.remove_bookmark(url)
            parent = item.parent()
            if parent:
                parent.removeChild(item)
    
    def add_folder(self):
        """Add a new folder."""
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            folder = QTreeWidgetItem([f"📁 {name}"])
            folder.setExpanded(True)
            self.tree.addTopLevelItem(folder)
            QMessageBox.information(self, "Folder Created", 
                                   f"Folder '{name}' created!\n\n"
                                   "Note: Drag and drop to organize bookmarks is coming soon.")
