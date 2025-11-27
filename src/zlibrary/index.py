"""
Download index management for Z-Library Search Application
"""
import json
import os
import time
import re
from typing import Dict, Any, Tuple, Optional
from zlibrary.config import Config
from zlibrary.logging_config import get_logger


class IndexManager:
    """Manages the download index to prevent duplicate downloads"""

    def __init__(self, config: Config):
        self.config = config
        self.index_file = self.config.get('download_index_file', 'download_index.json')
        self.logger = get_logger(__name__)
    
    def _try_repair_json(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to repair a corrupted JSON file by removing incomplete entries
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Repaired JSON as dict, or None if repair failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to find the last valid closing brace
            # Remove incomplete entries at the end
            last_complete_entry = content.rfind('},')
            if last_complete_entry > 0:
                # Find the opening brace
                opening_brace = content.find('{')
                if opening_brace >= 0:
                    # Reconstruct valid JSON
                    repaired = content[:last_complete_entry + 1] + '\n}'
                    repaired_data = json.loads(repaired)
                    self.logger.info(f"Successfully repaired JSON file with {len(repaired_data)} entries")
                    return repaired_data
        except Exception as e:
            self.logger.error(f"Failed to repair JSON: {e}")
        
        return None
    
    def create_download_index(self):
        """Create or initialize a download index file to track downloaded books"""
        # Create the download index file if it doesn't exist
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
            print(f"Created new download index: {self.index_file}")
        else:
            print(f"Using existing download index: {self.index_file}")  # This is a user-facing message, so keeping the print

    def add_to_download_index(self, book_id: str, book_title: str):
        """
        Add a book to the download index to prevent duplicates

        Args:
            book_id (str): Unique identifier for the book
            book_title (str): Title of the book
        """
        # Load existing index
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            except json.JSONDecodeError as e:
                self.logger.error(f"Corrupted index file: {e}")
                # Try to repair the file
                repaired_index = self._try_repair_json(self.index_file)
                if repaired_index is not None:
                    # Save repaired version
                    backup_file = f"{self.index_file}.corrupt.{int(time.time())}"
                    os.rename(self.index_file, backup_file)
                    self.logger.info(f"Repaired index file. Backup saved to: {backup_file}")
                    index = repaired_index
                else:
                    # Backup corrupted file and create new one
                    backup_file = f"{self.index_file}.corrupt.{int(time.time())}"
                    os.rename(self.index_file, backup_file)
                    self.logger.info(f"Could not repair. Corrupted index backed up to: {backup_file}")
                    index = {}
            except Exception as e:
                self.logger.error(f"Error reading index file: {e}")
                index = {}
        else:
            index = {}

        # Add the book to index
        index[book_id] = {
            'title': book_title,
            'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Save the updated index
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

    def is_already_downloaded(self, book_id: str) -> bool:
        """
        Check if a book has already been downloaded

        Args:
            book_id (str): Unique identifier for the book

        Returns:
            bool: True if book is already in index, False otherwise
        """
        if not os.path.exists(self.index_file):
            return False

        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            return book_id in index
        except json.JSONDecodeError as e:
            self.logger.error(f"Corrupted index file: {e}")
            # Try to repair the file
            repaired_index = self._try_repair_json(self.index_file)
            if repaired_index is not None:
                # Save repaired version
                backup_file = f"{self.index_file}.corrupt.{int(time.time())}"
                os.rename(self.index_file, backup_file)
                with open(self.index_file, 'w', encoding='utf-8') as f:
                    json.dump(repaired_index, f, indent=2)
                self.logger.info(f"Repaired index file. Backup saved to: {backup_file}")
                return book_id in repaired_index
            else:
                # Backup corrupted file and create new one
                backup_file = f"{self.index_file}.corrupt.{int(time.time())}"
                os.rename(self.index_file, backup_file)
                self.logger.info(f"Could not repair. Corrupted index backed up to: {backup_file}")
                return False
        except Exception as e:
            self.logger.error(f"Error reading index file: {e}")
            return False

    def get_download_index(self) -> Dict[str, Any]:
        """
        Get the entire download index

        Returns:
            dict: Download index
        """
        if not os.path.exists(self.index_file):
            return {}

        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"Corrupted index file: {e}")
            # Try to repair the file
            repaired_index = self._try_repair_json(self.index_file)
            if repaired_index is not None:
                # Save repaired version
                backup_file = f"{self.index_file}.corrupt.{int(time.time())}"
                os.rename(self.index_file, backup_file)
                with open(self.index_file, 'w', encoding='utf-8') as f:
                    json.dump(repaired_index, f, indent=2)
                self.logger.info(f"Repaired index file. Backup saved to: {backup_file}")
                return repaired_index
            else:
                # Backup corrupted file and create new one
                backup_file = f"{self.index_file}.corrupt.{int(time.time())}"
                os.rename(self.index_file, backup_file)
                self.logger.info(f"Could not repair. Corrupted index backed up to: {backup_file}")
                return {}
        except Exception as e:
            self.logger.error(f"Error reading index file: {e}")
            return {}

    def validate_download_index(self, download_dir: str = "books") -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Check download index entries against actual files on disk

        Args:
            download_dir (str): Directory where files are stored

        Returns:
            tuple: (valid_entries, missing_files)
        """
        import re

        # Make sure the download directory exists
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)

        # Get the download index
        index = self.get_download_index()

        valid_entries = {}
        missing_files = {}

        for book_id, data in index.items():
            # Get the filename from the title by cleaning it
            filename = data.get('title', f"unknown_book_{book_id}")

            # Find if a file exists in the directory that corresponds to this book
            # We'll look for files that contain the book title (with flexible matching)
            file_found = False
            for file in os.listdir(download_dir):
                # Check if the filename contains the book title (case-insensitive, removing punctuation)
                clean_title = re.sub(r'[^\w\s]', '', filename.lower())
                clean_file = re.sub(r'[^\w\s]', '', file.lower())
                # Check if most words from the title appear in the file name
                title_words = set(clean_title.split())
                file_words = set(clean_file.split())
                if title_words and file_words:
                    # At least half of the title words should match
                    word_overlap = len(title_words.intersection(file_words))
                    if word_overlap > 0 and word_overlap >= len(title_words) // 2:
                        valid_entries[book_id] = data
                        file_found = True
                        break
                # Also check if the filename contains the book ID as a substring
                if book_id in file:
                    valid_entries[book_id] = data
                    file_found = True
                    break

            if not file_found:
                missing_files[book_id] = {
                    'data': data,
                    'expected_path': f"{download_dir}/[filename_not_found_with_title:{filename}]"
                }

        return valid_entries, missing_files

    def update_download_index_check(self, download_dir: str = "books") -> int:
        """
        Update download index by removing entries for files that don't exist on disk
        """
        valid_entries, missing_files = self.validate_download_index(download_dir)

        # Update the index file to remove missing entries
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(valid_entries, f, indent=2)

        print(f"Updated download index: {len(valid_entries)} valid entries, {len(missing_files)} removed entries")  # User-facing output

        if missing_files:
            print("Missing files:")
            for book_id, info in missing_files.items():
                print(f"  - {book_id}: {info['data']['title']} (expected: {info['expected_path']})")  # User-facing output

        return len(missing_files)