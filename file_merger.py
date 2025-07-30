#!/usr/bin/env python3
"""
Advanced File Merger Script

A highly configurable tool for recursively merging files with extensive filtering options.
Supports multiple extensions, keyword filtering, directory inclusion/exclusion, and more.

Author: Generated for file merging operations
Version: 1.0.0
"""

import os
import re
import argparse
import json
import logging
from pathlib import Path
from typing import List, Set, Dict, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import fnmatch
import mimetypes


@dataclass
class MergeConfig:
    """Configuration class for file merging operations."""
    
    # Basic settings
    source_dirs: List[str] = field(default_factory=list)
    output_file: str = "merged_output.txt"
    extensions: List[str] = field(default_factory=lambda: ['.txt'])
    
    # Filtering options
    include_keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    include_dirs: List[str] = field(default_factory=list)
    exclude_dirs: List[str] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    
    # Content filtering
    content_include_regex: Optional[str] = None
    content_exclude_regex: Optional[str] = None
    min_file_size: int = 0  # bytes
    max_file_size: Optional[int] = None  # bytes
    
    # Processing options
    recursive: bool = True
    case_sensitive: bool = False
    follow_symlinks: bool = False
    sort_files: bool = True
    sort_by: str = "name"  # name, size, date
    reverse_sort: bool = False
    
    # Output formatting
    add_separators: bool = True
    separator_style: str = "header"  # header, line, custom
    custom_separator: str = "-" * 80
    include_file_info: bool = True
    add_timestamps: bool = True
    encoding: str = "utf-8"
    
    # Advanced options
    dry_run: bool = False
    verbose: bool = False
    ignore_errors: bool = False
    max_files: Optional[int] = None
    backup_output: bool = False


class FileMerger:
    """Advanced file merger with extensive configuration options."""
    
    def __init__(self, config: MergeConfig):
        self.config = config
        self.setup_logging()
        self.files_processed = 0
        self.files_skipped = 0
        self.errors_encountered = 0
        
        # Compile regex patterns for performance
        self.content_include_pattern = None
        self.content_exclude_pattern = None
        if config.content_include_regex:
            flags = 0 if config.case_sensitive else re.IGNORECASE
            self.content_include_pattern = re.compile(config.content_include_regex, flags)
        if config.content_exclude_regex:
            flags = 0 if config.case_sensitive else re.IGNORECASE
            self.content_exclude_pattern = re.compile(config.content_exclude_regex, flags)
    
    def setup_logging(self):
        """Configure logging based on verbosity settings."""
        level = logging.DEBUG if self.config.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included based on all filters."""
        
        # Check extension
        if self.config.extensions and file_path.suffix.lower() not in [ext.lower() for ext in self.config.extensions]:
            self.logger.debug(f"Skipping {file_path}: extension not in allowed list")
            return False
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            if file_size < self.config.min_file_size:
                self.logger.debug(f"Skipping {file_path}: file too small ({file_size} bytes)")
                return False
            if self.config.max_file_size and file_size > self.config.max_file_size:
                self.logger.debug(f"Skipping {file_path}: file too large ({file_size} bytes)")
                return False
        except OSError as e:
            self.logger.warning(f"Could not get file size for {file_path}: {e}")
            if not self.config.ignore_errors:
                return False
        
        # Check filename patterns
        filename = file_path.name
        if not self.config.case_sensitive:
            filename = filename.lower()
        
        # Include patterns
        if self.config.include_patterns:
            if not any(fnmatch.fnmatch(filename, pattern.lower() if not self.config.case_sensitive else pattern) 
                      for pattern in self.config.include_patterns):
                self.logger.debug(f"Skipping {file_path}: doesn't match include patterns")
                return False
        
        # Exclude patterns
        if self.config.exclude_patterns:
            if any(fnmatch.fnmatch(filename, pattern.lower() if not self.config.case_sensitive else pattern) 
                  for pattern in self.config.exclude_patterns):
                self.logger.debug(f"Skipping {file_path}: matches exclude patterns")
                return False
        
        # Keyword filtering
        if self.config.include_keywords:
            if not any(keyword.lower() if not self.config.case_sensitive else keyword in filename 
                      for keyword in self.config.include_keywords):
                self.logger.debug(f"Skipping {file_path}: doesn't contain include keywords")
                return False
        
        if self.config.exclude_keywords:
            if any(keyword.lower() if not self.config.case_sensitive else keyword in filename 
                  for keyword in self.config.exclude_keywords):
                self.logger.debug(f"Skipping {file_path}: contains exclude keywords")
                return False
        
        return True
    
    def should_include_directory(self, dir_path: Path) -> bool:
        """Determine if a directory should be traversed."""
        dir_name = dir_path.name
        if not self.config.case_sensitive:
            dir_name = dir_name.lower()
        
        # Include directories
        if self.config.include_dirs:
            if not any(fnmatch.fnmatch(dir_name, pattern.lower() if not self.config.case_sensitive else pattern) 
                      for pattern in self.config.include_dirs):
                return False
        
        # Exclude directories
        if self.config.exclude_dirs:
            if any(fnmatch.fnmatch(dir_name, pattern.lower() if not self.config.case_sensitive else pattern) 
                  for pattern in self.config.exclude_dirs):
                return False
        
        return True
    
    def should_include_content(self, content: str) -> bool:
        """Check if file content matches include/exclude regex patterns."""
        if self.content_include_pattern and not self.content_include_pattern.search(content):
            return False
        
        if self.content_exclude_pattern and self.content_exclude_pattern.search(content):
            return False
        
        return True
    
    def collect_files(self) -> List[Path]:
        """Collect all files that match the filtering criteria."""
        all_files = []
        
        for source_dir in self.config.source_dirs:
            source_path = Path(source_dir)
            if not source_path.exists():
                self.logger.warning(f"Source directory does not exist: {source_dir}")
                continue
            
            if not source_path.is_dir():
                self.logger.warning(f"Source path is not a directory: {source_dir}")
                continue
            
            self.logger.info(f"Scanning directory: {source_dir}")
            files_in_dir = self._collect_files_from_directory(source_path)
            all_files.extend(files_in_dir)
            self.logger.info(f"Found {len(files_in_dir)} files in {source_dir}")
        
        # Sort files if requested
        if self.config.sort_files:
            all_files = self._sort_files(all_files)
        
        # Limit number of files if specified
        if self.config.max_files:
            all_files = all_files[:self.config.max_files]
        
        self.logger.info(f"Total files to process: {len(all_files)}")
        return all_files
    
    def _collect_files_from_directory(self, directory: Path) -> List[Path]:
        """Recursively collect files from a directory."""
        files = []
        
        try:
            for item in directory.iterdir():
                if item.is_file() or (item.is_symlink() and self.config.follow_symlinks and item.is_file()):
                    if self.should_include_file(item):
                        files.append(item)
                elif item.is_dir() and self.config.recursive:
                    if item.is_symlink() and not self.config.follow_symlinks:
                        continue
                    if self.should_include_directory(item):
                        files.extend(self._collect_files_from_directory(item))
        except PermissionError as e:
            self.logger.warning(f"Permission denied accessing {directory}: {e}")
            if not self.config.ignore_errors:
                raise
        except Exception as e:
            self.logger.error(f"Error accessing {directory}: {e}")
            if not self.config.ignore_errors:
                raise
        
        return files
    
    def _sort_files(self, files: List[Path]) -> List[Path]:
        """Sort files based on the specified criteria."""
        if self.config.sort_by == "name":
            key_func = lambda f: f.name.lower() if not self.config.case_sensitive else f.name
        elif self.config.sort_by == "size":
            key_func = lambda f: f.stat().st_size if f.exists() else 0
        elif self.config.sort_by == "date":
            key_func = lambda f: f.stat().st_mtime if f.exists() else 0
        else:
            key_func = lambda f: f.name.lower() if not self.config.case_sensitive else f.name
        
        return sorted(files, key=key_func, reverse=self.config.reverse_sort)
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """Read and return file content with error handling."""
        try:
            with open(file_path, 'r', encoding=self.config.encoding, errors='replace') as f:
                content = f.read()
            
            # Apply content filtering
            if not self.should_include_content(content):
                self.logger.debug(f"Skipping {file_path}: content doesn't match regex filters")
                return None
            
            return content
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            self.errors_encountered += 1
            if not self.config.ignore_errors:
                raise
            return None
    
    def generate_separator(self, file_path: Path) -> str:
        """Generate separator text for file boundaries."""
        if not self.config.add_separators:
            return ""
        
        if self.config.separator_style == "line":
            return f"\n{'-' * 80}\n"
        elif self.config.separator_style == "custom":
            return f"\n{self.config.custom_separator}\n"
        else:  # header style
            header = f" FILE: {file_path} "
            separator_length = max(80, len(header) + 10)
            padding = (separator_length - len(header)) // 2
            separator = "=" * separator_length
            
            result = f"\n{separator}\n{' ' * padding}{header}{' ' * padding}\n{separator}\n"
            
            if self.config.include_file_info:
                try:
                    stat = file_path.stat()
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    result += f"Size: {size} bytes | Modified: {modified}\n"
                    result += "-" * separator_length + "\n"
                except:
                    pass
            
            return result
    
    def merge_files(self) -> bool:
        """Main method to merge all files."""
        self.logger.info("Starting file merge operation")
        
        if self.config.dry_run:
            self.logger.info("DRY RUN MODE - No files will be written")
        
        # Backup existing output file if requested
        if self.config.backup_output and Path(self.config.output_file).exists():
            backup_name = f"{self.config.output_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            Path(self.config.output_file).rename(backup_name)
            self.logger.info(f"Backed up existing output file to: {backup_name}")
        
        # Collect files
        files_to_merge = self.collect_files()
        
        if not files_to_merge:
            self.logger.warning("No files found matching the specified criteria")
            return False
        
        if self.config.dry_run:
            self.logger.info("Files that would be merged:")
            for file_path in files_to_merge:
                self.logger.info(f"  - {file_path}")
            return True
        
        # Merge files
        try:
            with open(self.config.output_file, 'w', encoding=self.config.encoding) as output_file:
                # Write header if timestamps are enabled
                if self.config.add_timestamps:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    header = f"File merge completed on {timestamp}\n"
                    header += f"Total files merged: {len(files_to_merge)}\n"
                    header += f"Configuration: {len(self.config.source_dirs)} source directories\n"
                    header += "=" * 80 + "\n\n"
                    output_file.write(header)
                
                for file_path in files_to_merge:
                    try:
                        content = self.read_file_content(file_path)
                        if content is not None:
                            separator = self.generate_separator(file_path)
                            output_file.write(separator)
                            output_file.write(content)
                            if not content.endswith('\n'):
                                output_file.write('\n')
                            
                            self.files_processed += 1
                            self.logger.debug(f"Merged: {file_path}")
                        else:
                            self.files_skipped += 1
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
                        self.errors_encountered += 1
                        if not self.config.ignore_errors:
                            raise
        
        except Exception as e:
            self.logger.error(f"Error writing output file: {e}")
            return False
        
        # Print summary
        self.print_summary()
        return True
    
    def print_summary(self):
        """Print operation summary."""
        self.logger.info("=" * 50)
        self.logger.info("MERGE OPERATION SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Files processed: {self.files_processed}")
        self.logger.info(f"Files skipped: {self.files_skipped}")
        self.logger.info(f"Errors encountered: {self.errors_encountered}")
        self.logger.info(f"Output file: {self.config.output_file}")
        
        if Path(self.config.output_file).exists():
            output_size = Path(self.config.output_file).stat().st_size
            self.logger.info(f"Output file size: {output_size:,} bytes")


def load_config_from_file(config_file: str) -> MergeConfig:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        return MergeConfig(**config_data)
    except Exception as e:
        raise ValueError(f"Error loading config file {config_file}: {e}")


def save_config_to_file(config: MergeConfig, config_file: str):
    """Save configuration to JSON file."""
    config_dict = {
        key: value for key, value in config.__dict__.items()
        if not key.startswith('_')
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_dict, f, indent=2)


def create_sample_config(output_file: str = "merge_config_sample.json"):
    """Create a sample configuration file."""
    sample_config = MergeConfig(
        source_dirs=["./src", "./docs"],
        output_file="merged_output.txt",
        extensions=[".py", ".txt", ".md"],
        include_keywords=["important", "main"],
        exclude_keywords=["temp", "backup"],
        exclude_dirs=["__pycache__", ".git", "node_modules"],
        include_patterns=["*.py", "README*"],
        exclude_patterns=["*test*", "*.tmp"],
        content_include_regex=r"class|def|function",
        min_file_size=100,
        max_file_size=1000000,
        recursive=True,
        case_sensitive=False,
        sort_files=True,
        sort_by="name",
        add_separators=True,
        separator_style="header",
        include_file_info=True,
        add_timestamps=True,
        verbose=True
    )
    
    save_config_to_file(sample_config, output_file)
    print(f"Sample configuration saved to: {output_file}")


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Advanced File Merger - Recursively merge files with extensive filtering options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python file_merger.py /path/to/source -o merged.txt -e .py .txt
  
  # Advanced filtering
  python file_merger.py /path/to/source -o output.txt -e .py \\
    --include-keywords main utils --exclude-dirs __pycache__ tests \\
    --content-regex "class|def" --min-size 100
  
  # Using config file
  python file_merger.py --config my_config.json
  
  # Generate sample config
  python file_merger.py --sample-config
        """
    )
    
    # Main arguments
    parser.add_argument('source_dirs', nargs='*', help='Source directories to scan')
    parser.add_argument('-o', '--output', default='merged_output.txt', help='Output file path')
    parser.add_argument('-e', '--extensions', nargs='+', help='File extensions to include (e.g., .py .txt)')
    
    # Configuration file options
    parser.add_argument('--config', help='Load configuration from JSON file')
    parser.add_argument('--save-config', help='Save current configuration to JSON file')
    parser.add_argument('--sample-config', action='store_true', help='Generate sample configuration file')
    
    # Filtering options
    parser.add_argument('--include-keywords', nargs='+', default=[], help='Include files with these keywords')
    parser.add_argument('--exclude-keywords', nargs='+', default=[], help='Exclude files with these keywords')
    parser.add_argument('--include-dirs', nargs='+', default=[], help='Include only these directory patterns')
    parser.add_argument('--exclude-dirs', nargs='+', default=[], help='Exclude these directory patterns')
    parser.add_argument('--include-patterns', nargs='+', default=[], help='Include files matching these patterns')
    parser.add_argument('--exclude-patterns', nargs='+', default=[], help='Exclude files matching these patterns')
    
    # Content filtering
    parser.add_argument('--content-regex', help='Include only files with content matching this regex')
    parser.add_argument('--content-exclude-regex', help='Exclude files with content matching this regex')
    parser.add_argument('--min-size', type=int, default=0, help='Minimum file size in bytes')
    parser.add_argument('--max-size', type=int, help='Maximum file size in bytes')
    
    # Processing options
    parser.add_argument('--no-recursive', action='store_true', help='Disable recursive directory traversal')
    parser.add_argument('--case-sensitive', action='store_true', help='Enable case-sensitive matching')
    parser.add_argument('--follow-symlinks', action='store_true', help='Follow symbolic links')
    parser.add_argument('--no-sort', action='store_true', help='Disable file sorting')
    parser.add_argument('--sort-by', choices=['name', 'size', 'date'], default='name', help='Sort files by')
    parser.add_argument('--reverse-sort', action='store_true', help='Reverse sort order')
    
    # Output formatting
    parser.add_argument('--no-separators', action='store_true', help='Disable file separators')
    parser.add_argument('--separator-style', choices=['header', 'line', 'custom'], default='header', help='Separator style')
    parser.add_argument('--custom-separator', default='-'*80, help='Custom separator string')
    parser.add_argument('--no-file-info', action='store_true', help='Exclude file information')
    parser.add_argument('--no-timestamps', action='store_true', help='Exclude timestamps')
    parser.add_argument('--encoding', default='utf-8', help='File encoding')
    
    # Advanced options
    parser.add_argument('--dry-run', action='store_true', help='Show what would be merged without doing it')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--ignore-errors', action='store_true', help='Continue on errors')
    parser.add_argument('--max-files', type=int, help='Maximum number of files to process')
    parser.add_argument('--backup', action='store_true', help='Backup existing output file')
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.sample_config:
        create_sample_config()
        return
    
    # Load configuration
    if args.config:
        config = load_config_from_file(args.config)
    else:
        # Create config from command line arguments
        config = MergeConfig(
            source_dirs=args.source_dirs,
            output_file=args.output,
            extensions=args.extensions or ['.txt'],
            include_keywords=args.include_keywords,
            exclude_keywords=args.exclude_keywords,
            include_dirs=args.include_dirs,
            exclude_dirs=args.exclude_dirs,
            include_patterns=args.include_patterns,
            exclude_patterns=args.exclude_patterns,
            content_include_regex=args.content_regex,
            content_exclude_regex=args.content_exclude_regex,
            min_file_size=args.min_size,
            max_file_size=args.max_size,
            recursive=not args.no_recursive,
            case_sensitive=args.case_sensitive,
            follow_symlinks=args.follow_symlinks,
            sort_files=not args.no_sort,
            sort_by=args.sort_by,
            reverse_sort=args.reverse_sort,
            add_separators=not args.no_separators,
            separator_style=args.separator_style,
            custom_separator=args.custom_separator,
            include_file_info=not args.no_file_info,
            add_timestamps=not args.no_timestamps,
            encoding=args.encoding,
            dry_run=args.dry_run,
            verbose=args.verbose,
            ignore_errors=args.ignore_errors,
            max_files=args.max_files,
            backup_output=args.backup
        )
    
    # Save configuration if requested
    if args.save_config:
        save_config_to_file(config, args.save_config)
        print(f"Configuration saved to: {args.save_config}")
    
    # Validate configuration
    if not config.source_dirs:
        print("Error: No source directories specified")
        parser.print_help()
        return
    
    # Create and run merger
    merger = FileMerger(config)
    success = merger.merge_files()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()