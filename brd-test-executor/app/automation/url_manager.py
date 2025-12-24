"""
URL Manager
Load and manage URL mappings from YAML config
"""
import yaml
import os
from typing import Optional


class URLManager:
    """Manage URL mappings for test automation"""
    
    def __init__(self, url_file: str = "app/locators/url_mapping.yaml"):
        """
        Initialize URL manager
        
        Args:
            url_file: Path to URL mapping YAML file
        """
        self.url_file = url_file
        self.urls = {}
        self.base_url = ""
        self.load_urls()
    
    def load_urls(self) -> bool:
        """
        Load URLs from YAML file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.url_file):
                print(f"  Warning: URL mapping file not found: {self.url_file}")
                return False
            
            with open(self.url_file, 'r', encoding='utf-8') as f:
                self.urls = yaml.safe_load(f)
            
            self.base_url = self.urls.get('base_url', '')
            
            print(f"✓ Loaded URL mappings from: {self.url_file}")
            print(f"  Base URL: {self.base_url}")
            print(f"  Modules: {', '.join([k for k in self.urls.keys() if k != 'base_url'])}")
            return True
        
        except Exception as e:
            print(f"✗ Error loading URLs: {str(e)}")
            return False
    
    def get(self, module: str, action: str, **kwargs) -> Optional[str]:
        """
        Get full URL for specific module and action
        
        Args:
            module: Module name (e.g., 'contract', 'lead')
            action: Action name (e.g., 'list', 'create', 'edit')
            **kwargs: Variables to replace in URL (e.g., id='123')
        
        Returns:
            Full URL or None
        
        Example:
            url = manager.get('contract', 'list')
            # Returns: "https://agency-uat.affina.com.vn/account/contract"
            
            url = manager.get('contract', 'edit', id='123')
            # Returns: "https://agency-uat.affina.com.vn/account/contract/edit/123"
        """
        try:
            module_urls = self.urls.get(module)
            if not module_urls:
                print(f"  Module '{module}' not found in URL mapping")
                return None
            
            path = module_urls.get(action)
            if not path:
                print(f"  Action '{action}' not found in module '{module}'")
                return None
            
            # Replace variables in path (e.g., {id} -> 123)
            for key, value in kwargs.items():
                path = path.replace(f"{{{key}}}", str(value))
            
            # Construct full URL
            full_url = f"{self.base_url}{path}"
            return full_url
        
        except Exception as e:
            print(f"✗ Error getting URL: {str(e)}")
            return None
    
    def get_path(self, module: str, action: str, **kwargs) -> Optional[str]:
        """
        Get path only (without base URL)
        
        Args:
            module: Module name
            action: Action name
            **kwargs: Variables to replace
        
        Returns:
            Path string or None
        """
        try:
            module_urls = self.urls.get(module)
            if not module_urls:
                return None
            
            path = module_urls.get(action)
            if not path:
                return None
            
            # Replace variables
            for key, value in kwargs.items():
                path = path.replace(f"{{{key}}}", str(value))
            
            return path
        
        except Exception as e:
            print(f"✗ Error getting path: {str(e)}")
            return None
    
    def get_all_urls(self, module: str) -> dict:
        """
        Get all URLs for a module
        
        Args:
            module: Module name
        
        Returns:
            Dictionary of action -> URL
        """
        module_urls = self.urls.get(module, {})
        return {
            action: f"{self.base_url}{path}"
            for action, path in module_urls.items()
        }


# Singleton instance
_url_manager = None

def get_url_manager() -> URLManager:
    """Get singleton URL manager instance"""
    global _url_manager
    if _url_manager is None:
        _url_manager = URLManager()
    return _url_manager
