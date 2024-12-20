from pathlib import Path
import os

def Set_WD(base_folder: str, *args: str) -> str:
    """
    Creates a path using the given base folder and additional folder names, and sets it as the working directory. 

    Parameters:
    - base_folder (str): The base path for setting the working directory. This should be an existing directory.
    - *args (str): Additional folder names to be appended to the base folder. These can be any number of strings representing folder names.

    Returns:
    - str: The full path of the new working directory.

    Example:
        base_folder = 'C:/Users/YGKim_IBS/Documents' 
        Set_WD(base_folder, "test1", "test2")
        =========================================================================
        Directory C:/Users/YGKim_IBS/Documents\test1\test2 created.
        The working directory is set to C:/Users/YGKim_IBS/Documents\test1\test2.
    """

    full_path = os.path.join(base_folder, *args)

    try:
        full_path.mkdir(parents=True, exist_ok=True)
        os.chdir(full_path)
        if full_path.exists():
            print(f"Directory {full_path} already exists.")
        else:
            print(f"Directory {full_path} created.")
        print(f"The working directory is set to {full_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return str(full_path)

################################################################################################################

def Grab_files_in_folder(folder_path: str, ext: str="") -> list:
    """
    Returns the paths of files with the specified extension present in the given folder.

    Parameters:
    - folder_path (str): The path of the directory where you want to start the search. This should be an existing directory.
    - ext (str): The file extension you are looking for (e.g., '.txt' for text files, '.py' for Python files). If no extension is provided, all files in the folder will be returned.

    Returns:
    - list: A list of file paths that match the specified extension within the given folder.

    Example:
        base = "C:/Users/YGKim_IBS/Documents/Github/Jupyter_notebook/FiberPhotometry"
        Grab_files_in_folder(base, ext='.ipynb')
        =========================================================================
        This will return a list of all Jupyter Notebook files (.ipynb) in the specified folder.
    """

    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError(f"The provided path {folder_path} is not a valid directory.")

    return [str(file) for file in folder.glob(f'*{ext}') if file.is_file()]

################################################################################################################

def Grab_files_in_all_subfolder(folder_path: str, ext: str="") -> list:
    """
    Return the paths of files with the specified extension present in the given folder including *all sub-foler*.

    Parameters:
    - folder (str): The path of the directory where you want to start the search
    - ext   : The file extension you are looking for (e.g., '.txt' for text files, '.py' for Python files) 
    
    Example:
    base = "C:/Users/YGKim_IBS/Documents/Github/Jupyter_notebook/FiberPhotometry"
    Grab_files_in_folder(base, ext='.ipynb')
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError(f"The provided path {folder_path} is not a valid directory.")
    
    return[os.path.join(root, name) 
            for root, dirs, files in os.walk(folder_path)
            for name in files 
            if name.endswith(ext)]