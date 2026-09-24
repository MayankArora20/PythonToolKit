import os
import re

def rename_files_in_folder(folder_path):
    """
    Rename files in the specified folder by moving everything before "Dharma" to the end.
    Ignores hyphens in the process.
    """
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return
    
    files = os.listdir(folder_path)
    
    for filename in files:
        if "Dharma" in filename:
            # Split the filename at "Dharma"
            parts = filename.split("Dharma", 1)
            
            if len(parts) == 2:
                before_dharma = parts[0].rstrip(" -")  # Remove trailing spaces and hyphens
                after_dharma = "Dharma" + parts[1]
                
                # Construct new filename
                if before_dharma.strip():
                    new_filename = f"{after_dharma.strip()} - {before_dharma.strip()}.mp3"
                else:
                    new_filename = f"{after_dharma.strip()}.mp3"
                
                # Get full paths
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_filename)
                
                # Rename the file
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed: {filename}")
                    print(f"  To: {new_filename}")
                    print()
                except Exception as e:
                    print(f"Error renaming {filename}: {e}")
        else:
            print(f"Skipped (no 'Dharma' found): {filename}")

if __name__ == "__main__":
    folder_path = r"c:\Users\mkaro\Desktop\python\Youtube\PlaylistMp3Download\NavratriDay2"
    
    print("File Renaming Tool")
    print("==================")
    print(f"Processing files in: {folder_path}")
    print()
    
    rename_files_in_folder(folder_path)
    
    print("Renaming complete!")
