import json
import os
from typing import List, Dict
from datetime import datetime


class SessionManager:
    """Manages browser sessions (save/restore tabs)."""
    
    def __init__(self, storage_path: str = "browser_data"):
        self.storage_path = storage_path
        self.sessions_dir = os.path.join(storage_path, "sessions")
        self.auto_save_file = os.path.join(self.sessions_dir, "last_session.json")
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist."""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)
    
    def save_session(self, tabs: List[Dict[str, str]], name: str = None) -> str:
        """
        Save current session.
        
        Args:
            tabs: List of dicts with 'url' and 'title' keys
            name: Optional session name, if None uses timestamp
        
        Returns:
            Session filename
        """
        if name is None:
            name = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        
        session_data = {
            'name': name,
            'created': datetime.now().isoformat(),
            'tabs': tabs,
            'tab_count': len(tabs)
        }
        
        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_name}.json"
        filepath = os.path.join(self.sessions_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            return filename
        except IOError as e:
            print(f"Error saving session: {e}")
            return None
    
    def load_session(self, filename: str) -> List[Dict[str, str]]:
        """Load a session by filename."""
        filepath = os.path.join(self.sessions_dir, filename)
        
        if not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                return session_data.get('tabs', [])
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading session: {e}")
            return []
    
    def get_all_sessions(self) -> List[Dict[str, any]]:
        """Get list of all saved sessions."""
        sessions = []
        
        if not os.path.exists(self.sessions_dir):
            return sessions
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json') and filename != 'last_session.json':
                filepath = os.path.join(self.sessions_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        sessions.append({
                            'filename': filename,
                            'name': session_data.get('name', filename),
                            'created': session_data.get('created', ''),
                            'tab_count': session_data.get('tab_count', 0)
                        })
                except (json.JSONDecodeError, IOError):
                    continue
        
        # Sort by creation date (newest first)
        sessions.sort(key=lambda x: x.get('created', ''), reverse=True)
        return sessions
    
    def delete_session(self, filename: str) -> bool:
        """Delete a saved session."""
        filepath = os.path.join(self.sessions_dir, filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except OSError:
                return False
        return False
    
    def auto_save(self, tabs: List[Dict[str, str]]):
        """Auto-save current session (for restore on startup)."""
        session_data = {
            'name': 'Last Session',
            'created': datetime.now().isoformat(),
            'tabs': tabs,
            'tab_count': len(tabs)
        }
        
        try:
            with open(self.auto_save_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error auto-saving session: {e}")
    
    def load_last_session(self) -> List[Dict[str, str]]:
        """Load the last auto-saved session."""
        if not os.path.exists(self.auto_save_file):
            return []
        
        try:
            with open(self.auto_save_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                return session_data.get('tabs', [])
        except (json.JSONDecodeError, IOError):
            return []
    
    def has_last_session(self) -> bool:
        """Check if there's a last session to restore."""
        return os.path.exists(self.auto_save_file)


class TabGroupManager:
    """Manages tab groups for organization."""
    
    def __init__(self):
        self.groups = {}  # group_id -> {'name': str, 'color': str, 'tabs': [indices]}
        self.next_group_id = 1
    
    def create_group(self, name: str, color: str = "#4CAF50") -> int:
        """Create a new tab group."""
        group_id = self.next_group_id
        self.next_group_id += 1
        
        self.groups[group_id] = {
            'name': name,
            'color': color,
            'tabs': [],
            'collapsed': False
        }
        
        return group_id
    
    def add_tab_to_group(self, group_id: int, tab_index: int):
        """Add a tab to a group."""
        if group_id in self.groups:
            if tab_index not in self.groups[group_id]['tabs']:
                self.groups[group_id]['tabs'].append(tab_index)
    
    def remove_tab_from_group(self, group_id: int, tab_index: int):
        """Remove a tab from a group."""
        if group_id in self.groups:
            if tab_index in self.groups[group_id]['tabs']:
                self.groups[group_id]['tabs'].remove(tab_index)
    
    def get_tab_group(self, tab_index: int) -> int:
        """Get the group ID for a tab."""
        for group_id, group_data in self.groups.items():
            if tab_index in group_data['tabs']:
                return group_id
        return None
    
    def delete_group(self, group_id: int):
        """Delete a group."""
        if group_id in self.groups:
            del self.groups[group_id]
    
    def toggle_collapse(self, group_id: int):
        """Toggle group collapse state."""
        if group_id in self.groups:
            self.groups[group_id]['collapsed'] = not self.groups[group_id]['collapsed']
            return self.groups[group_id]['collapsed']
        return False
    
    def get_all_groups(self) -> Dict:
        """Get all groups."""
        return self.groups.copy()
