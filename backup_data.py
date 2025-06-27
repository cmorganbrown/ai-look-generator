#!/usr/bin/env python3
"""
Data Backup and Restore Utility for TrendScraper
This script helps backup and restore data across deployments
"""

import os
import json
import shutil
from datetime import datetime
import zipfile

class DataBackup:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.backup_dir = os.path.join(base_dir, "backups")
        self.data_dirs = ["uploads", "landing_pages", "looks"]
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, backup_name=None):
        """Create a backup of all data directories"""
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if os.path.exists(backup_path):
            print(f"⚠️  Backup directory {backup_name} already exists. Overwriting...")
            shutil.rmtree(backup_path)
        
        os.makedirs(backup_path)
        
        print(f"📦 Creating backup: {backup_name}")
        
        for data_dir in self.data_dirs:
            source_path = os.path.join(self.base_dir, data_dir)
            if os.path.exists(source_path):
                dest_path = os.path.join(backup_path, data_dir)
                shutil.copytree(source_path, dest_path)
                print(f"  ✅ Backed up {data_dir}/")
            else:
                print(f"  ⚠️  {data_dir}/ not found, skipping...")
        
        # Create metadata
        metadata = {
            "backup_name": backup_name,
            "created_at": datetime.now().isoformat(),
            "data_dirs": self.data_dirs,
            "files_count": self._count_files(backup_path)
        }
        
        with open(os.path.join(backup_path, "backup_metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Backup created successfully: {backup_path}")
        return backup_path
    
    def restore_backup(self, backup_name):
        """Restore data from a backup"""
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            print(f"❌ Backup {backup_name} not found!")
            return False
        
        print(f"🔄 Restoring backup: {backup_name}")
        
        # Read metadata
        metadata_file = os.path.join(backup_path, "backup_metadata.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            print(f"  📅 Created: {metadata.get('created_at', 'Unknown')}")
        
        for data_dir in self.data_dirs:
            source_path = os.path.join(backup_path, data_dir)
            dest_path = os.path.join(self.base_dir, data_dir)
            
            if os.path.exists(source_path):
                # Remove existing directory if it exists
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                
                shutil.copytree(source_path, dest_path)
                print(f"  ✅ Restored {data_dir}/")
            else:
                print(f"  ⚠️  {data_dir}/ not found in backup, skipping...")
        
        print(f"✅ Backup restored successfully!")
        return True
    
    def list_backups(self):
        """List all available backups"""
        if not os.path.exists(self.backup_dir):
            print("No backups found.")
            return []
        
        backups = []
        for item in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, item)
            if os.path.isdir(backup_path):
                metadata_file = os.path.join(backup_path, "backup_metadata.json")
                if os.path.exists(metadata_file):
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                    backups.append({
                        "name": item,
                        "created_at": metadata.get("created_at", "Unknown"),
                        "files_count": metadata.get("files_count", 0)
                    })
        
        return backups
    
    def _count_files(self, directory):
        """Count files in a directory recursively"""
        count = 0
        for root, dirs, files in os.walk(directory):
            count += len(files)
        return count

def main():
    """Command line interface for backup operations"""
    import sys
    
    backup = DataBackup()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_data.py create [backup_name]  - Create a backup")
        print("  python backup_data.py restore <backup_name> - Restore a backup")
        print("  python backup_data.py list                  - List all backups")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        backup_name = sys.argv[2] if len(sys.argv) > 2 else None
        backup.create_backup(backup_name)
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Please specify a backup name to restore")
            return
        backup_name = sys.argv[2]
        backup.restore_backup(backup_name)
    
    elif command == "list":
        backups = backup.list_backups()
        if not backups:
            print("No backups found.")
        else:
            print("Available backups:")
            for b in backups:
                print(f"  📦 {b['name']} ({b['created_at']}) - {b['files_count']} files")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 