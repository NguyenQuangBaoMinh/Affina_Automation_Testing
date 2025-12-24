"""
Locator Manager
Loads and manages element locators from YAML config
"""
import yaml
import os
from typing import Optional, Dict, Any


class LocatorManager:
    """Manage element locators from YAML file"""
    
    def __init__(self, locators_file: str = "app/locators/locators.yaml"):
        """
        Initialize locator manager
        
        Args:
            locators_file: Path to locators YAML file
        """
        self.locators_file = locators_file
        self.locators = {}
        self.load_locators()
    
    def load_locators(self) -> bool:
        """
        Load locators from YAML file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.locators_file):
                print(f"  Warning: Locators file not found: {self.locators_file}")
                return False
            
            with open(self.locators_file, 'r', encoding='utf-8') as f:
                self.locators = yaml.safe_load(f)
            
            print(f"✓ Loaded locators from: {self.locators_file}")
            print(f"  Categories: {', '.join(self.locators.keys())}")
            return True
        
        except Exception as e:
            print(f"✗ Error loading locators: {str(e)}")
            return False
    
    def get(self, category: str, element: str) -> Optional[str]:
        """
        Get locator for specific element
        
        Args:
            category: Category (e.g., 'login', 'contract')
            element: Element name (e.g., 'email_input', 'save_button')
        
        Returns:
            Locator string or None
        
        Example:
            locator = manager.get('login', 'email_input')
            # Returns: "input[name='email'], input[type='email'], #email"
        """
        try:
            return self.locators.get(category, {}).get(element)
        except Exception as e:
            print(f"✗ Error getting locator {category}.{element}: {str(e)}")
            return None
    
    def get_all(self, category: str) -> Dict[str, str]:
        """
        Get all locators for a category
        
        Args:
            category: Category name
        
        Returns:
            Dictionary of element_name -> locator
        """
        return self.locators.get(category, {})
    
    def has(self, category: str, element: str) -> bool:
        """
        Check if locator exists
        
        Args:
            category: Category name
            element: Element name
        
        Returns:
            True if exists, False otherwise
        """
        return element in self.locators.get(category, {})
    
    def reload(self) -> bool:
        """Reload locators from file"""
        return self.load_locators()


# Singleton instance
_locator_manager = None

def get_locator_manager() -> LocatorManager:
    """Get singleton locator manager instance"""
    global _locator_manager
    if _locator_manager is None:
        _locator_manager = LocatorManager()
    return _locator_manager
