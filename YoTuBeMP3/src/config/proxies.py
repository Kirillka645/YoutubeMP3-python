"""
Proxy manager for bypassing restrictions in Russia.
"""

import random
from typing import Dict, List, Optional
import requests
from requests.exceptions import ProxyError, Timeout, ConnectionError


class ProxyManager:
    """Manager for proxy servers."""
    
    def __init__(self):
        self.proxy_list: List[Dict[str, str]] = []
        self.current_proxy: Optional[Dict[str, str]] = None
        self.used_proxies: set = set()
    
    def load_proxies(self, proxy_file: str) -> int:
        """
        Load proxies from a file.
        
        Args:
            proxy_file: Path to file with proxies (format: http://user:pass@host:port)
        
        Returns:
            Number of loaded proxies
        """
        try:
            with open(proxy_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxy = self._parse_proxy(line)
                        if proxy:
                            self.proxy_list.append(proxy)
            return len(self.proxy_list)
        except FileNotFoundError:
            return 0
        except Exception:
            return 0
    
    def _parse_proxy(self, proxy_str: str) -> Optional[Dict[str, str]]:
        """
        Parse proxy string to dict.
        
        Args:
            proxy_str: Proxy string (http://user:pass@host:port)
        
        Returns:
            Proxy dict or None if invalid
        """
        if not proxy_str.startswith(('http://', 'https://', 'socks5://')):
            proxy_str = 'http://' + proxy_str
        
        return {'http': proxy_str, 'https': proxy_str}
    
    def add_proxy(self, proxy_str: str) -> bool:
        """
        Add a single proxy.
        
        Args:
            proxy_str: Proxy string
        
        Returns:
            True if added successfully
        """
        proxy = self._parse_proxy(proxy_str)
        if proxy:
            self.proxy_list.append(proxy)
            return True
        return False
    
    def test_proxy(self, proxy: Dict[str, str], timeout: int = 10) -> bool:
        """
        Test if proxy is working.
        
        Args:
            proxy: Proxy dict with 'http' and 'https' keys
            timeout: Request timeout in seconds
        
        Returns:
            True if proxy is working
        """
        try:
            test_urls = [
                'https://www.youtube.com',
                'https://httpbin.org/ip',
            ]
            
            for url in test_urls:
                response = requests.get(
                    url,
                    proxies=proxy,
                    timeout=timeout,
                    allow_redirects=True
                )
                if response.status_code == 200:
                    return True
            
            return False
        except (ProxyError, Timeout, ConnectionError):
            return False
        except Exception:
            return False
    
    def get_working_proxy(self, timeout: int = 10) -> Optional[Dict[str, str]]:
        """
        Get a working proxy from the list.
        
        Args:
            timeout: Request timeout in seconds
        
        Returns:
            Working proxy dict or None
        """
        available = [p for p in self.proxy_list if id(p) not in self.used_proxies]
        
        if not available:
            # Reset used proxies if all are used
            if self.proxy_list:
                available = self.proxy_list
                self.used_proxies.clear()
        
        random.shuffle(available)
        
        for proxy in available:
            if self.test_proxy(proxy, timeout):
                self.current_proxy = proxy
                self.used_proxies.add(id(proxy))
                return proxy
        
        return None
    
    def rotate_proxy(self) -> Optional[Dict[str, str]]:
        """
        Rotate to next working proxy.
        
        Returns:
            Next working proxy or None
        """
        return self.get_working_proxy()
    
    def get_proxy_string(self) -> Optional[str]:
        """
        Get current proxy as string.
        
        Returns:
            Proxy string or None
        """
        if self.current_proxy:
            return self.current_proxy.get('http')
        return None
    
    def has_proxies(self) -> bool:
        """Check if any proxies are loaded."""
        return len(self.proxy_list) > 0
