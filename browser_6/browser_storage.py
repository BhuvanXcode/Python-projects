import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class BookmarkManager:
    """Manages browser bookmarks with persistent storage."""
    
    def __init__(self, storage_path: str = "browser_data"):
        self.storage_path = storage_path
        self.bookmarks_file = os.path.join(storage_path, "bookmarks.json")
        self._ensure_storage_exists()
        self.bookmarks = self._load_bookmarks()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def _load_bookmarks(self) -> List[Dict[str, str]]:
        """Load bookmarks from JSON file."""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_bookmarks(self):
        """Save bookmarks to JSON file."""
        try:
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving bookmarks: {e}")
    
    def add_bookmark(self, url: str, title: str) -> bool:
        """Add a new bookmark."""
        # Check if bookmark already exists
        if any(b['url'] == url for b in self.bookmarks):
            return False
        
        bookmark = {
            'url': url,
            'title': title,
            'added': datetime.now().isoformat()
        }
        self.bookmarks.append(bookmark)
        self._save_bookmarks()
        return True
    
    def remove_bookmark(self, url: str) -> bool:
        """Remove a bookmark by URL."""
        original_length = len(self.bookmarks)
        self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
        if len(self.bookmarks) < original_length:
            self._save_bookmarks()
            return True
        return False
    
    def get_all_bookmarks(self) -> List[Dict[str, str]]:
        """Get all bookmarks."""
        return self.bookmarks.copy()
    
    def is_bookmarked(self, url: str) -> bool:
        """Check if a URL is bookmarked."""
        return any(b['url'] == url for b in self.bookmarks)
    
    def clear_all(self):
        """Clear all bookmarks."""
        self.bookmarks = []
        self._save_bookmarks()


class HistoryManager:
    """Manages browsing history with persistent storage."""
    
    def __init__(self, storage_path: str = "browser_data", max_entries: int = 1000):
        self.storage_path = storage_path
        self.history_file = os.path.join(storage_path, "history.json")
        self.max_entries = max_entries
        self._ensure_storage_exists()
        self.history = self._load_history()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def _load_history(self) -> List[Dict[str, str]]:
        """Load history from JSON file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_history(self):
        """Save history to JSON file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving history: {e}")
    
    def add_entry(self, url: str, title: str):
        """Add a new history entry."""
        entry = {
            'url': url,
            'title': title,
            'visited': datetime.now().isoformat()
        }
        
        # Add to beginning of list (most recent first)
        self.history.insert(0, entry)
        
        # Trim to max entries
        if len(self.history) > self.max_entries:
            self.history = self.history[:self.max_entries]
        
        self._save_history()
    
    def get_recent_history(self, limit: int = 50) -> List[Dict[str, str]]:
        """Get recent history entries."""
        return self.history[:limit]
    
    def search_history(self, query: str, limit: int = 20) -> List[Dict[str, str]]:
        """Search history by URL or title."""
        query_lower = query.lower()
        results = [
            entry for entry in self.history
            if query_lower in entry['url'].lower() or query_lower in entry['title'].lower()
        ]
        return results[:limit]
    
    def clear_all(self):
        """Clear all history."""
        self.history = []
        self._save_history()
    
    def clear_range(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """Clear history within a date range."""
        if start_date is None and end_date is None:
            self.clear_all()
            return
        
        filtered_history = []
        for entry in self.history:
            visited = datetime.fromisoformat(entry['visited'])
            if start_date and visited < start_date:
                filtered_history.append(entry)
            elif end_date and visited > end_date:
                filtered_history.append(entry)
        
        self.history = filtered_history
        self._save_history()


class SettingsManager:
    """Manages browser settings with persistent storage."""
    
    DEFAULT_SETTINGS = {
        'homepage': 'https://www.google.com',
        'search_engine': 'google',
        'dark_mode': False,
        'download_path': '',
        'show_bookmarks_bar': True,
        'enable_javascript': True,
        'enable_plugins': True,
        'zoom_level': 100,
        'default_zoom': 100,
    }
    
    SEARCH_ENGINES = {
        'google': 'https://www.google.com/search?q={}',
        'duckduckgo': 'https://duckduckgo.com/?q={}',
        'bing': 'https://www.bing.com/search?q={}',
        'yahoo': 'https://search.yahoo.com/search?p={}',
    }
    
    def __init__(self, storage_path: str = "browser_data"):
        self.storage_path = storage_path
        self.settings_file = os.path.join(storage_path, "settings.json")
        self._ensure_storage_exists()
        self.settings = self._load_settings()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def _load_settings(self) -> Dict:
        """Load settings from JSON file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULT_SETTINGS, **loaded}
            except (json.JSONDecodeError, IOError):
                return self.DEFAULT_SETTINGS.copy()
        return self.DEFAULT_SETTINGS.copy()
    
    def _save_settings(self):
        """Save settings to JSON file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a setting value."""
        self.settings[key] = value
        self._save_settings()
    
    def get_all(self) -> Dict:
        """Get all settings."""
        return self.settings.copy()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._save_settings()
    
    def get_search_url(self, query: str) -> str:
        """Get search URL for the configured search engine."""
        engine = self.settings.get('search_engine', 'google')
        template = self.SEARCH_ENGINES.get(engine, self.SEARCH_ENGINES['google'])
        return template.format(query)


class ClosedTabsManager:
    """Manages recently closed tabs for restoration."""
    
    def __init__(self, max_tabs: int = 10):
        self.max_tabs = max_tabs
        self.closed_tabs = []
    
    def add_closed_tab(self, url: str, title: str):
        """Add a closed tab to the history."""
        tab_info = {
            'url': url,
            'title': title,
            'closed': datetime.now().isoformat()
        }
        self.closed_tabs.insert(0, tab_info)
        
        # Trim to max tabs
        if len(self.closed_tabs) > self.max_tabs:
            self.closed_tabs = self.closed_tabs[:self.max_tabs]
    
    def get_last_closed_tab(self) -> Optional[Dict[str, str]]:
        """Get and remove the most recently closed tab."""
        if self.closed_tabs:
            return self.closed_tabs.pop(0)
        return None
    
    def get_all_closed_tabs(self) -> List[Dict[str, str]]:
        """Get all closed tabs."""
        return self.closed_tabs.copy()
    
    def clear_all(self):
        """Clear all closed tabs."""
        self.closed_tabs = []
