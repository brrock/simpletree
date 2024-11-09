#!/usr/bin/env python3

import os
from pathlib import Path
import sys
import fnmatch
from typing import List, Set

class GitignoreParser:
    def __init__(self):
        self.patterns: List[str] = []
        # Common patterns to always ignore
        self.default_patterns = [
            'node_modules',
            'dist',
            '__pycache__',
            '*.pyc',
            '.git',
            '.DS_Store',
            'build',
            '.env',
            'venv',
            '.venv'
        ]
        
    def load_gitignore(self, directory: str) -> None:
        """Load patterns from .gitignore file if it exists"""
        gitignore_path = os.path.join(directory, '.gitignore')
        self.patterns = self.default_patterns.copy()
        
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        # Remove leading and trailing slashes
                        line = line.strip('/')
                        self.patterns.append(line)

    def should_ignore(self, path: str, is_dir: bool = False) -> bool:
        """Check if a path should be ignored based on gitignore patterns"""
        path = os.path.normpath(path)
        name = os.path.basename(path)
        
        for pattern in self.patterns:
            # Handle directory-specific patterns
            if pattern.endswith('/') and not is_dir:
                continue
                
            # Remove trailing slash for directory patterns
            pattern = pattern.rstrip('/')
            
            # Check if pattern matches the full path or just the name
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(name, pattern):
                return True
            
            # Handle wildcard directory patterns
            if '**' in pattern:
                parts = pattern.split('**')
                if len(parts) == 2:
                    if path.startswith(parts[0]) and path.endswith(parts[1]):
                        return True
                        
        return False

def tree(directory=".", level=0, prefix="", gitignore_parser=None):
    """
    Print directory structure in a tree format, respecting gitignore rules.
    
    Args:
        directory (str): Path to the directory to start from
        level (int): Current recursion level
        prefix (str): Prefix for the current line
        gitignore_parser (GitignoreParser): Parser for handling gitignore patterns
    """
    # Get the path object
    path = Path(directory)
    
    # Initialize gitignore parser at root level
    if level == 0:
        gitignore_parser = GitignoreParser()
        gitignore_parser.load_gitignore(directory)
        
    # Check if path should be ignored
    if gitignore_parser.should_ignore(str(path), path.is_dir()):
        return
        
    # Print the current directory/file
    if level == 0:
        print(path.name)
    else:
        is_last = not any(Path(directory).parent.iterdir())
        print(f"{prefix}{'└── ' if is_last else '├── '}{path.name}")
    
    # If it's a directory, process its contents
    if path.is_dir():
        # Get and sort the contents
        try:
            contents = sorted(list(path.iterdir()), 
                            key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return
            
        # Filter out ignored paths
        contents = [
            item for item in contents 
            if not gitignore_parser.should_ignore(str(item), item.is_dir())
        ]
        
        # Process each item
        for i, item in enumerate(contents):
            # Prepare the prefix for the next level
            if level == 0:
                new_prefix = "    "
            else:
                is_last_item = i == len(contents) - 1
                new_prefix = prefix + ("    " if is_last_item else "│   ")
            
            # Recursive call
            tree(str(item), level + 1, new_prefix, gitignore_parser)

def main():
    # Use command line argument if provided, otherwise use current directory
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    tree(path)

if __name__ == "__main__":
    main()
