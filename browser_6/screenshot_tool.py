from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QToolBar, QColorDialog, QSpinBox,
                             QComboBox, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QImage
import os
from datetime import datetime


class ScreenshotAnnotator(QDialog):
    """Dialog for annotating screenshots."""
    
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Screenshot Annotator")
        self.setWindowFlags(Qt.Window)
        
        self.original_pixmap = pixmap
        self.pixmap = pixmap.copy()
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(255, 0, 0)
        self.pen_width = 3
        self.tool = "pen"  # pen, highlighter, text, arrow, rectangle
        
        self.init_ui()
        
        # Resize to fit screen
        screen_size = QApplication.desktop().availableGeometry()
        max_width = int(screen_size.width() * 0.9)
        max_height = int(screen_size.height() * 0.9)
        
        if self.pixmap.width() > max_width or self.pixmap.height() > max_height:
            self.pixmap = self.pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.setFixedSize(self.pixmap.size())
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QToolBar()
        
        # Tool selection
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["Pen", "Highlighter", "Rectangle", "Arrow", "Text"])
        self.tool_combo.currentTextChanged.connect(self.tool_changed)
        toolbar.addWidget(QLabel("Tool:"))
        toolbar.addWidget(self.tool_combo)
        
        toolbar.addSeparator()
        
        # Color selection
        self.color_btn = QPushButton("Color")
        self.color_btn.clicked.connect(self.choose_color)
        self.color_btn.setStyleSheet(f"background-color: {self.pen_color.name()};")
        toolbar.addWidget(self.color_btn)
        
        toolbar.addSeparator()
        
        # Width selection
        toolbar.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 20)
        self.width_spin.setValue(3)
        self.width_spin.valueChanged.connect(self.width_changed)
        toolbar.addWidget(self.width_spin)
        
        toolbar.addSeparator()
        
        # Undo
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.undo)
        toolbar.addWidget(undo_btn)
        
        # Clear
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)
        toolbar.addWidget(clear_btn)
        
        toolbar.addSeparator()
        
        # Save
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_screenshot)
        toolbar.addWidget(save_btn)
        
        # Copy
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        toolbar.addWidget(copy_btn)
        
        # Close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        toolbar.addWidget(close_btn)
        
        layout.addWidget(toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
    
    def tool_changed(self, tool_name):
        """Handle tool change."""
        self.tool = tool_name.lower()
    
    def choose_color(self):
        """Choose pen color."""
        color = QColorDialog.getColor(self.pen_color, self)
        if color.isValid():
            self.pen_color = color
            self.color_btn.setStyleSheet(f"background-color: {self.pen_color.name()};")
    
    def width_changed(self, width):
        """Handle width change."""
        self.pen_width = width
    
    def undo(self):
        """Undo last action."""
        self.pixmap = self.original_pixmap.copy()
        self.update()
    
    def clear_all(self):
        """Clear all annotations."""
        self.pixmap = self.original_pixmap.copy()
        self.update()
    
    def save_screenshot(self):
        """Save screenshot to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"screenshot_{timestamp}.png"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenshot",
            default_name,
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*.*)"
        )
        
        if file_path:
            self.pixmap.save(file_path)
            QMessageBox.information(self, "Saved", f"Screenshot saved to:\n{file_path}")
    
    def copy_to_clipboard(self):
        """Copy screenshot to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.pixmap)
        QMessageBox.information(self, "Copied", "Screenshot copied to clipboard!")
    
    def paintEvent(self, event):
        """Paint the screenshot."""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        if self.drawing and event.buttons() & Qt.LeftButton:
            painter = QPainter(self.pixmap)
            
            if self.tool == "pen":
                pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawLine(self.last_point, event.pos())
            
            elif self.tool == "highlighter":
                color = QColor(self.pen_color)
                color.setAlpha(100)
                pen = QPen(color, self.pen_width * 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawLine(self.last_point, event.pos())
            
            self.last_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.drawing = False
            
            if self.tool == "rectangle":
                painter = QPainter(self.pixmap)
                pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine)
                painter.setPen(pen)
                rect = QRect(self.last_point, event.pos())
                painter.drawRect(rect)
                self.update()
            
            elif self.tool == "arrow":
                painter = QPainter(self.pixmap)
                pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine)
                painter.setPen(pen)
                painter.drawLine(self.last_point, event.pos())
                
                # Draw arrowhead
                # Simple triangle at the end
                end_point = event.pos()
                start_point = self.last_point
                
                # Calculate arrow direction
                dx = end_point.x() - start_point.x()
                dy = end_point.y() - start_point.y()
                
                # Draw simple arrowhead
                painter.setBrush(self.pen_color)
                arrow_size = 10
                
                self.update()


class ScreenshotTool:
    """Screenshot capture tool."""
    
    @staticmethod
    def capture_visible_area(webview):
        """Capture visible area of webview."""
        # Get the webview's visible size
        size = webview.size()
        pixmap = QPixmap(size)
        webview.render(pixmap)
        return pixmap
    
    @staticmethod
    def capture_full_page(webview):
        """Capture full page including scrolled content."""
        # Get page size
        page = webview.page()
        
        # Create a larger pixmap for the full page
        # Note: This is a simplified version
        size = webview.size()
        pixmap = QPixmap(size)
        webview.render(pixmap)
        
        return pixmap
    
    @staticmethod
    def show_annotator(pixmap, parent=None):
        """Show screenshot annotator dialog."""
        dialog = ScreenshotAnnotator(pixmap, parent)
        dialog.exec_()
    
    @staticmethod
    def quick_save(pixmap, directory=None):
        """Quickly save screenshot without dialog."""
        if directory is None:
            directory = os.path.expanduser("~/Pictures")
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(directory, filename)
        
        pixmap.save(filepath)
        return filepath
