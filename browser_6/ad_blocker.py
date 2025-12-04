from PyQt5.QtCore import QUrl
import json
import os


class AdBlocker:
    """Ad blocking functionality."""
    
    # Common ad domains and patterns
    DEFAULT_BLOCKLIST = [
        "doubleclick.net",
        "googlesyndication.com",
        "googleadservices.com",
        "google-analytics.com",
        "googletagmanager.com",
        "facebook.com/tr",
        "facebook.net",
        "ads.yahoo.com",
        "advertising.com",
        "adserver",
        "adservice",
        "adsystem",
        "/ads/",
        "/ad/",
        "banner",
        "popup",
        "popunder",
        "tracking",
        "analytics",
        "metrics",
    ]
    
    def __init__(self, storage_path="browser_data"):
        self.storage_path = storage_path
        self.blocklist_file = os.path.join(storage_path, "adblocker.json")
        self.enabled = True
        self.blocked_count = 0
        self.whitelist = []
        self.custom_blocklist = []
        
        self._ensure_storage_exists()
        self._load_settings()
    
    def _ensure_storage_exists(self):
        """Create storage directory if it doesn't exist."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def _load_settings(self):
        """Load ad blocker settings."""
        if os.path.exists(self.blocklist_file):
            try:
                with open(self.blocklist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.enabled = data.get('enabled', True)
                    self.whitelist = data.get('whitelist', [])
                    self.custom_blocklist = data.get('custom_blocklist', [])
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_settings(self):
        """Save ad blocker settings."""
        try:
            data = {
                'enabled': self.enabled,
                'whitelist': self.whitelist,
                'custom_blocklist': self.custom_blocklist
            }
            with open(self.blocklist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving ad blocker settings: {e}")
    
    def should_block(self, url: str) -> bool:
        """Check if URL should be blocked."""
        if not self.enabled:
            return False
        
        url_lower = url.lower()
        
        # Check whitelist first
        for whitelisted in self.whitelist:
            if whitelisted in url_lower:
                return False
        
        # Check default blocklist
        for blocked in self.DEFAULT_BLOCKLIST:
            if blocked in url_lower:
                self.blocked_count += 1
                return True
        
        # Check custom blocklist
        for blocked in self.custom_blocklist:
            if blocked in url_lower:
                self.blocked_count += 1
                return True
        
        return False
    
    def add_to_whitelist(self, domain: str):
        """Add domain to whitelist."""
        if domain not in self.whitelist:
            self.whitelist.append(domain)
            self._save_settings()
    
    def remove_from_whitelist(self, domain: str):
        """Remove domain from whitelist."""
        if domain in self.whitelist:
            self.whitelist.remove(domain)
            self._save_settings()
    
    def add_to_blocklist(self, pattern: str):
        """Add pattern to custom blocklist."""
        if pattern not in self.custom_blocklist:
            self.custom_blocklist.append(pattern)
            self._save_settings()
    
    def remove_from_blocklist(self, pattern: str):
        """Remove pattern from custom blocklist."""
        if pattern in self.custom_blocklist:
            self.custom_blocklist.remove(pattern)
            self._save_settings()
    
    def toggle_enabled(self):
        """Toggle ad blocker on/off."""
        self.enabled = not self.enabled
        self._save_settings()
        return self.enabled
    
    def get_blocked_count(self) -> int:
        """Get number of blocked ads."""
        return self.blocked_count
    
    def reset_blocked_count(self):
        """Reset blocked ads counter."""
        self.blocked_count = 0
    
    def get_statistics(self) -> dict:
        """Get ad blocker statistics."""
        return {
            'enabled': self.enabled,
            'blocked_count': self.blocked_count,
            'whitelist_count': len(self.whitelist),
            'custom_blocklist_count': len(self.custom_blocklist),
            'total_rules': len(self.DEFAULT_BLOCKLIST) + len(self.custom_blocklist)
        }


class AdBlockerInterceptor:
    """Request interceptor for ad blocking."""
    
    def __init__(self, ad_blocker: AdBlocker):
        self.ad_blocker = ad_blocker
    
    def interceptRequest(self, info):
        """Intercept and block ad requests."""
        url = info.requestUrl().toString()
        
        if self.ad_blocker.should_block(url):
            # Block the request
            info.block(True)
