#!/usr/bin/env python3
"""
ADOIT REST API Client

Client for interacting with ADOIT's REST API (v4) to query architecture repositories.

Note: ADOIT Community Edition restricts write operations (POST/PATCH/DELETE return 403).
This client focuses on read operations for analyzing current state.

Configuration:
    Create a .env file with:
        ADOIT_URL=https://adoit-ce.boc-cloud.com
        ADOIT_USERNAME=user@example.com
        ADOIT_PASSWORD=your_password
        ADOIT_REPOSITORY_ID=optional_default_repo_id

Usage:
    # Using environment variables (recommended)
    client = ADOITClient.from_env()
    
    # Or explicit credentials
    client = ADOITClient(
        base_url="https://adoit-ce.boc-cloud.com",
        username="user@example.com",
        password="password"
    )
    
    # List repositories
    repos = client.list_repositories()
    
    # Query elements
    capabilities = client.find_elements("Capability")
    
    # Get element details
    element = client.get_element(element_id)
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json


def load_env_file(env_path: str = None) -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}
    
    # Search paths for .env file
    search_paths = [
        env_path,
        Path.cwd() / '.env',
        Path.home() / '.adoit' / '.env',
        Path(__file__).parent / '.env',
    ]
    
    for path in search_paths:
        if path and Path(path).exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"').strip("'")
            break
    
    return env_vars


@dataclass
class ADOITElement:
    """Represents an ADOIT repository element"""
    id: str
    name: str
    element_type: str
    description: str = ""
    attributes: Dict[str, Any] = None
    relationships: List[Dict] = None
    
    def __post_init__(self):
        self.attributes = self.attributes or {}
        self.relationships = self.relationships or []


class ADOITClient:
    """Client for ADOIT REST API v4"""
    
    @classmethod
    def from_env(cls, env_path: str = None) -> 'ADOITClient':
        """
        Create client from environment variables.
        
        Reads from .env file or environment:
            ADOIT_URL - Base URL (required)
            ADOIT_USERNAME - Username (required)
            ADOIT_PASSWORD - Password (required)
            ADOIT_REPOSITORY_ID - Default repository (optional)
        
        Args:
            env_path: Optional path to .env file
        
        Returns:
            Configured ADOITClient instance
        """
        # Load from .env file
        env_vars = load_env_file(env_path)
        
        # Environment variables take precedence
        base_url = os.getenv('ADOIT_URL') or env_vars.get('ADOIT_URL')
        username = os.getenv('ADOIT_USERNAME') or env_vars.get('ADOIT_USERNAME')
        password = os.getenv('ADOIT_PASSWORD') or env_vars.get('ADOIT_PASSWORD')
        repo_id = os.getenv('ADOIT_REPOSITORY_ID') or env_vars.get('ADOIT_REPOSITORY_ID')
        
        if not all([base_url, username, password]):
            missing = []
            if not base_url: missing.append('ADOIT_URL')
            if not username: missing.append('ADOIT_USERNAME')
            if not password: missing.append('ADOIT_PASSWORD')
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Create a .env file with:\n"
                "  ADOIT_URL=https://your-instance.boc-cloud.com\n"
                "  ADOIT_USERNAME=your@email.com\n"
                "  ADOIT_PASSWORD=your_password\n"
                "  ADOIT_REPOSITORY_ID=optional_repo_id"
            )
        
        return cls(
            base_url=base_url,
            username=username,
            password=password,
            repository_id=repo_id
        )
    
    def __init__(
        self, 
        base_url: str,
        username: str,
        password: str,
        repository_id: Optional[str] = None
    ):
        """
        Initialize ADOIT client.
        
        Args:
            base_url: ADOIT instance URL (e.g., https://adoit-ce.boc-cloud.com)
            username: ADOIT username
            password: ADOIT password
            repository_id: Optional default repository ID
        """
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password)
        self.repository_id = repository_id
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Dict = None, 
        data: Dict = None
    ) -> Dict:
        """Make API request"""
        url = f"{self.base_url}/rest/4.0/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise PermissionError(
                    "Access denied. ADOIT CE restricts this operation. "
                    "Use Excel import for write operations."
                )
            raise
    
    # ==================== Repository Operations ====================
    
    def list_repositories(self) -> List[Dict]:
        """List available repositories"""
        return self._request('GET', '/repositories')
    
    def get_repository(self, repo_id: str = None) -> Dict:
        """Get repository details"""
        repo_id = repo_id or self.repository_id
        return self._request('GET', f'/repositories/{repo_id}')
    
    # ==================== Element Operations ====================
    
    def find_elements(
        self,
        element_type: str,
        repo_id: str = None,
        name_filter: str = None,
        limit: int = 100
    ) -> List[ADOITElement]:
        """
        Find elements by type.
        
        Args:
            element_type: ArchiMate element type (e.g., "Capability")
            repo_id: Repository ID (uses default if not specified)
            name_filter: Optional name filter
            limit: Maximum results
        
        Returns:
            List of ADOITElement objects
        """
        repo_id = repo_id or self.repository_id
        
        params = {
            'type': element_type,
            'limit': limit
        }
        if name_filter:
            params['name'] = name_filter
        
        response = self._request(
            'GET',
            f'/repositories/{repo_id}/objects',
            params=params
        )
        
        elements = []
        for item in response.get('items', []):
            elements.append(ADOITElement(
                id=item.get('id', ''),
                name=item.get('name', ''),
                element_type=item.get('type', element_type),
                description=item.get('description', ''),
                attributes=item.get('attributes', {})
            ))
        
        return elements
    
    def get_element(self, element_id: str, repo_id: str = None) -> ADOITElement:
        """Get element by ID with full details"""
        repo_id = repo_id or self.repository_id
        
        response = self._request(
            'GET',
            f'/repositories/{repo_id}/objects/{element_id}'
        )
        
        return ADOITElement(
            id=response.get('id', element_id),
            name=response.get('name', ''),
            element_type=response.get('type', ''),
            description=response.get('description', ''),
            attributes=response.get('attributes', {}),
            relationships=response.get('relations', [])
        )
    
    def get_element_relationships(
        self,
        element_id: str,
        repo_id: str = None,
        relationship_type: str = None
    ) -> List[Dict]:
        """Get relationships for an element"""
        repo_id = repo_id or self.repository_id
        
        params = {}
        if relationship_type:
            params['type'] = relationship_type
        
        response = self._request(
            'GET',
            f'/repositories/{repo_id}/objects/{element_id}/relations',
            params=params
        )
        
        return response.get('items', [])
    
    # ==================== Model Operations ====================
    
    def list_models(
        self,
        repo_id: str = None,
        model_type: str = None
    ) -> List[Dict]:
        """List models in repository"""
        repo_id = repo_id or self.repository_id
        
        params = {}
        if model_type:
            params['type'] = model_type
        
        response = self._request(
            'GET',
            f'/repositories/{repo_id}/models',
            params=params
        )
        
        return response.get('items', [])
    
    def get_model(self, model_id: str, repo_id: str = None) -> Dict:
        """Get model details"""
        repo_id = repo_id or self.repository_id
        return self._request('GET', f'/repositories/{repo_id}/models/{model_id}')
    
    # ==================== Analysis Helpers ====================
    
    def get_capability_hierarchy(self, repo_id: str = None) -> Dict[str, List[str]]:
        """
        Get capability hierarchy as parent->children mapping.
        
        Returns:
            Dict mapping parent capability names to list of child names
        """
        capabilities = self.find_elements('Capability', repo_id, limit=1000)
        
        hierarchy = {}
        for cap in capabilities:
            rels = self.get_element_relationships(cap.id, repo_id, 'Composition')
            children = [r.get('target', {}).get('name', '') for r in rels if r.get('direction') == 'outgoing']
            if children:
                hierarchy[cap.name] = children
        
        return hierarchy
    
    def find_unrealized_capabilities(self, repo_id: str = None) -> List[ADOITElement]:
        """Find capabilities not realized by any application component"""
        capabilities = self.find_elements('Capability', repo_id, limit=1000)
        
        unrealized = []
        for cap in capabilities:
            rels = self.get_element_relationships(cap.id, repo_id, 'Realization')
            incoming_realizations = [r for r in rels if r.get('direction') == 'incoming']
            if not incoming_realizations:
                unrealized.append(cap)
        
        return unrealized
    
    def get_application_portfolio(self, repo_id: str = None) -> List[ADOITElement]:
        """Get all application components with their capabilities"""
        apps = self.find_elements('Application Component', repo_id, limit=1000)
        
        for app in apps:
            rels = self.get_element_relationships(app.id, repo_id, 'Realization')
            app.relationships = [r for r in rels if r.get('direction') == 'outgoing']
        
        return apps


def main():
    """CLI interface for ADOIT client"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ADOIT REST API Client')
    parser.add_argument('--url', help='ADOIT base URL (or set ADOIT_URL env var)')
    parser.add_argument('--username', '-u', help='Username (or set ADOIT_USERNAME env var)')
    parser.add_argument('--password', '-p', help='Password (or set ADOIT_PASSWORD env var)')
    parser.add_argument('--repo', '-r', help='Repository ID (or set ADOIT_REPOSITORY_ID env var)')
    parser.add_argument('--env-file', help='Path to .env file')
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # List repositories
    subparsers.add_parser('list-repos', help='List repositories')
    
    # Find elements
    find_parser = subparsers.add_parser('find', help='Find elements')
    find_parser.add_argument('type', help='Element type')
    find_parser.add_argument('--name', help='Name filter')
    
    # Get element
    get_parser = subparsers.add_parser('get', help='Get element')
    get_parser.add_argument('id', help='Element ID')
    
    # List models
    subparsers.add_parser('list-models', help='List models')
    
    # Capability analysis
    subparsers.add_parser('capability-gaps', help='Find unrealized capabilities')
    
    args = parser.parse_args()
    
    try:
        # Try to create client from explicit args or environment
        if args.url and args.username and args.password:
            client = ADOITClient(
                base_url=args.url,
                username=args.username,
                password=args.password,
                repository_id=args.repo
            )
        else:
            # Fall back to environment variables / .env file
            client = ADOITClient.from_env(args.env_file)
            if args.repo:
                client.repository_id = args.repo
        if args.command == 'list-repos':
            repos = client.list_repositories()
            print(json.dumps(repos, indent=2))
        
        elif args.command == 'find':
            elements = client.find_elements(args.type, name_filter=args.name)
            for el in elements:
                print(f"{el.id}: {el.name}")
        
        elif args.command == 'get':
            element = client.get_element(args.id)
            print(json.dumps({
                'id': element.id,
                'name': element.name,
                'type': element.element_type,
                'description': element.description,
                'attributes': element.attributes,
                'relationships': element.relationships
            }, indent=2))
        
        elif args.command == 'list-models':
            models = client.list_models()
            for m in models:
                print(f"{m.get('id')}: {m.get('name')}")
        
        elif args.command == 'capability-gaps':
            gaps = client.find_unrealized_capabilities()
            print(f"Found {len(gaps)} unrealized capabilities:")
            for cap in gaps:
                print(f"  - {cap.name}")
        
        else:
            parser.print_help()
    
    except PermissionError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
