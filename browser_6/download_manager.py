from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QProgressBar,
                             QHeaderView, QMessageBox, QFileDialog, QAbstractItemView)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QObject
from PyQt5.QtWebEngineWidgets import QWebEngineDownloadItem
import os
from datetime import datetime


class DownloadSignals(QObject):
    """Signals for download events."""
    download_finished = pyqtSignal(str)
    download_failed = pyqtSignal(str)


class DownloadInfo:
    """Information about a download."""
    
    def __init__(self, download_item: QWebEngineDownloadItem):
        self.download_item = download_item
        self.filename = os.path.basename(download_item.path())
        self.url = download_item.url().toString()
        self.total_bytes = download_item.totalBytes()
        self.received_bytes = 0
        self.state = "Downloading"
        self.start_time = datetime.now()
        self.path = download_item.path()
        self.progress = 0
        
    def update_progress(self, received: int, total: int):
        """Update download progress."""
        self.received_bytes = received
        self.total_bytes = total
        if total > 0:
            self.progress = int((received / total) * 100)
    
    def get_size_string(self) -> str:
        """Get human-readable size string."""
        def format_bytes(bytes_val):
            if bytes_val < 1024:
                return f"{bytes_val} B"
            elif bytes_val < 1024 * 1024:
                return f"{bytes_val / 1024:.1f} KB"
            elif bytes_val < 1024 * 1024 * 1024:
                return f"{bytes_val / (1024 * 1024):.1f} MB"
            else:
                return f"{bytes_val / (1024 * 1024 * 1024):.1f} GB"
        
        if self.total_bytes > 0:
            return f"{format_bytes(self.received_bytes)} / {format_bytes(self.total_bytes)}"
        else:
            return f"{format_bytes(self.received_bytes)}"


class DownloadManagerDialog(QDialog):
    """Dialog for managing downloads."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Manager")
        self.setMinimumSize(700, 400)
        self.downloads = []
        self.signals = DownloadSignals()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Downloads")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(title_label)
        
        # Downloads table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Filename", "Size", "Progress", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setColumnWidth(2, 150)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.clear_completed_btn = QPushButton("Clear Completed")
        self.clear_completed_btn.clicked.connect(self.clear_completed)
        button_layout.addWidget(self.clear_completed_btn)
        
        self.open_folder_btn = QPushButton("Open Download Folder")
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        button_layout.addWidget(self.open_folder_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_download(self, download_item: QWebEngineDownloadItem):
        """Add a new download to the manager."""
        download_info = DownloadInfo(download_item)
        self.downloads.append(download_info)
        
        # Add row to table
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Filename
        self.table.setItem(row, 0, QTableWidgetItem(download_info.filename))
        
        # Size
        self.table.setItem(row, 1, QTableWidgetItem(download_info.get_size_string()))
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        self.table.setCellWidget(row, 2, progress_bar)
        
        # Status
        self.table.setItem(row, 3, QTableWidgetItem("Downloading"))
        
        # Actions
        action_widget = QWidget()
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(2, 2, 2, 2)
        
        pause_btn = QPushButton("Pause")
        pause_btn.clicked.connect(lambda: self.pause_download(row))
        action_layout.addWidget(pause_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(lambda: self.cancel_download(row))
        action_layout.addWidget(cancel_btn)
        
        action_widget.setLayout(action_layout)
        self.table.setCellWidget(row, 4, action_widget)
        
        # Connect download signals
        download_item.downloadProgress.connect(
            lambda received, total, r=row: self.update_download_progress(r, received, total)
        )
        download_item.finished.connect(
            lambda r=row: self.download_finished(r)
        )
        
        # Accept the download
        download_item.accept()
    
    def update_download_progress(self, row: int, received: int, total: int):
        """Update download progress."""
        if row >= len(self.downloads):
            return
        
        download_info = self.downloads[row]
        download_info.update_progress(received, total)
        
        # Update size
        self.table.item(row, 1).setText(download_info.get_size_string())
        
        # Update progress bar
        progress_bar = self.table.cellWidget(row, 2)
        if progress_bar:
            progress_bar.setValue(download_info.progress)
    
    def download_finished(self, row: int):
        """Handle download completion."""
        if row >= len(self.downloads):
            return
        
        download_info = self.downloads[row]
        download_info.state = "Completed"
        
        # Update status
        self.table.item(row, 3).setText("Completed")
        
        # Update actions
        action_widget = QWidget()
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(2, 2, 2, 2)
        
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(lambda: self.open_file(row))
        action_layout.addWidget(open_btn)
        
        show_btn = QPushButton("Show in Folder")
        show_btn.clicked.connect(lambda: self.show_in_folder(row))
        action_layout.addWidget(show_btn)
        
        action_widget.setLayout(action_layout)
        self.table.setCellWidget(row, 4, action_widget)
        
        self.signals.download_finished.emit(download_info.filename)
    
    def pause_download(self, row: int):
        """Pause/resume a download."""
        if row >= len(self.downloads):
            return
        
        download_info = self.downloads[row]
        download_item = download_info.download_item
        
        if download_item.state() == QWebEngineDownloadItem.DownloadInProgress:
            download_item.pause()
            self.table.item(row, 3).setText("Paused")
            
            # Update button
            action_widget = self.table.cellWidget(row, 4)
            if action_widget:
                pause_btn = action_widget.layout().itemAt(0).widget()
                pause_btn.setText("Resume")
        elif download_item.state() == QWebEngineDownloadItem.DownloadPaused:
            download_item.resume()
            self.table.item(row, 3).setText("Downloading")
            
            # Update button
            action_widget = self.table.cellWidget(row, 4)
            if action_widget:
                pause_btn = action_widget.layout().itemAt(0).widget()
                pause_btn.setText("Pause")
    
    def cancel_download(self, row: int):
        """Cancel a download."""
        if row >= len(self.downloads):
            return
        
        download_info = self.downloads[row]
        download_item = download_info.download_item
        
        reply = QMessageBox.question(
            self, "Cancel Download",
            f"Are you sure you want to cancel '{download_info.filename}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            download_item.cancel()
            download_info.state = "Cancelled"
            self.table.item(row, 3).setText("Cancelled")
            
            # Remove action buttons
            self.table.setCellWidget(row, 4, QWidget())
    
    def open_file(self, row: int):
        """Open the downloaded file."""
        if row >= len(self.downloads):
            return
        
        download_info = self.downloads[row]
        path = download_info.path
        
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self, "File Not Found", f"The file '{download_info.filename}' was not found.")
    
    def show_in_folder(self, row: int):
        """Show the downloaded file in folder."""
        if row >= len(self.downloads):
            return
        
        download_info = self.downloads[row]
        path = download_info.path
        
        if os.path.exists(path):
            os.startfile(os.path.dirname(path))
        else:
            QMessageBox.warning(self, "File Not Found", f"The file '{download_info.filename}' was not found.")
    
    def clear_completed(self):
        """Clear completed downloads from the list."""
        rows_to_remove = []
        for i in range(len(self.downloads) - 1, -1, -1):
            if self.downloads[i].state == "Completed":
                rows_to_remove.append(i)
        
        for row in rows_to_remove:
            self.table.removeRow(row)
            del self.downloads[row]
    
    def open_download_folder(self):
        """Open the default download folder."""
        # Get the download path from the first download or use default
        if self.downloads:
            folder = os.path.dirname(self.downloads[0].path)
        else:
            folder = os.path.expanduser("~/Downloads")
        
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            QMessageBox.warning(self, "Folder Not Found", "Download folder not found.")
