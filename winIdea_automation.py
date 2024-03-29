import click
import subprocess
import os
import glob
import pandas as pd
import py_canoe
from typing import Dict, Optional

# Paths for the .xjrf Workspace files to be used and the path for the .exe WinIdea.
# CHANGE THE PATHS FOR THE OTHER ODIS
ws_paths = []
winIdea_exe = ""
canoe_config_file = ""  # Replace with CANoe configuration path file
ecu_node_name = "ECU_Node"  # Replace with the name of the ECU node in CANoe

parcode_dict = {}  # type: Dict[str, str]


def search_files(paths: list, extensions: list) -> list:
    """
    Search for files with given extensions in specified paths.
    
    Args:
        paths (list): List of paths to search.
        extensions (list): List of file extensions to search for.
        
    Returns:
        list: List of file paths found.
    """
    result_files = []  # type: list
    for path in paths:
        for extension in extensions:
            files = glob.glob(os.path.join(path, f"*.{extension}"), recursive=True)
            result_files.extend(files)
    return result_files


def read_parcode_excel(file_path: str) -> Optional[Dict[str, str]]:
    """
    Read parcode information from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file.
        
    Returns:
        dict: Dictionary mapping variant names to ZIP container names.
        None: If an error occurs during file reading.
    """
    try:
        df = pd.read_excel(file_path)
        parcode_dict = dict(zip(df["Variant Name"], df["ZIP Container Name"]))
        return parcode_dict
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


@click.group()
def main() -> None:
    pass


@main.command()
@click.option("--software-folder", prompt="Enter the software folder name")
@click.option("--channel-type", prompt="Enter the channel type")
@click.option("--car-platform", prompt="Enter car platform")
def configure(software_folder: str, channel_type: str, car_platform: str) -> None:
    """
    Configure the software environment.
    
    Args:
        software_folder (str): Name of the software folder.
        channel_type (str): Type of communication channel.
        car_platform (str): Car platform identifier.
    """
    # Construct search paths based on the software version
    search_paths = [
        # Complete the search paths based on your requirements
    ]

    # Define the list of file extensions to search for
    file_extensions = ["*B_dev.Hex", "*R.Hex", "*E_dev.Hex", "*P_dev.Hex", "*CRC.elf"]

    # Find ELF and HEX files in the specified directories with different extensions
    elf_files = search_files(search_paths, ["elf"] + file_extensions)
    hex_files = search_files(search_paths, ["hex"] + file_extensions)

    if not elf_files or not hex_files:
        print("Error: ELF or HEX files not found in the specified directories.")
        return

    # Use the first ELF and HEX files found
    elf_file = elf_files[0]
    hex_file = hex_files[0]

    # Accessing parcode excel paths
    parcode_excel_path1 = f"C:\\0_SW\\{car_platform}\\{software_folder}\\EXTERNAL\\{channel_type}\\DS_CONTAINER\\ZipContainer_UNE_12CH.xlsx"
    parcode_excel_path2 = "insert excel path"  # Insert the second path

    parcode_dict1 = read_parcode_excel(parcode_excel_path1)
    parcode_dict2 = read_parcode_excel(parcode_excel_path2)

    if not parcode_dict1 or not parcode_dict2:
        print("Invalid parcode Excel. Exiting")
        return

    selected_parcode = prompt_user_for_parcode(parcode_dict)
    if selected_parcode:
        print(f"Selected Parcode: {selected_parcode}")
        # Access the dataset name using selected_parcode as the key
        selected_dataset = parcode_dict[selected_parcode]
        print(f"Dataset Name: {selected_dataset}")

    # Other configuration steps...


@main.command()
def run_workspace() -> None:
    """
    Run the workspace.
    """
    selected_workspace = prompt_user_for_workspace()
    if selected_workspace:
        run_workspace(selected_workspace)
    else:
        print("Invalid selection. No workspace selected")


@main.command()
def prompt_user_for_canoe() -> bool:
    """
    Prompt user to start CANoe for ECU information.
    
    Returns:
        bool: True if user wants to start CANoe, False otherwise.
    """
    # Prompt the user to confirm CANoe configuration
    user_input = input("Do you want to start CANoe for ECU information? (y/n): ").lower()
    return user_input == "y"


def prompt_user_for_parcode(parcode_dict: Dict[str, str]) -> Optional[str]:
    """
    Prompt the user to select a parcode.
    
    Args:
        parcode_dict (Dict[str, str]): Dictionary mapping variant names to ZIP container names.
        
    Returns:
        str: Selected parcode.
        None: If invalid input or no parcode selected.
    """
    print("Select a parcode:")
    for i, parcode in enumerate(parcode_dict, start=1):
        print(f"{i}. {parcode}")

    user_input = input("Enter the number corresponding to the parcode: ")
    selected_parcode = (
        list(parcode_dict.keys())[int(user_input) - 1]
        if 1 <= int(user_input) <= len(parcode_dict)
        else None
    )
    return selected_parcode


def prompt_user_for_workspace() -> Optional[str]:
    """
    Prompt the user to select a workspace.
    
    Returns:
        str: Selected workspace path.
        None: If invalid input or no workspace selected.
    """
    print("Select a workspace:")
    for i, ws_path in enumerate(ws_paths, start=1):
        print(f"{i}. {ws_path}")

    user_input = input("Enter the number corresponding to the workspace: ")
    selected_workspace = (
        ws_paths[int(user_input) - 1] if 1 <= int(user_input) <= len(ws_paths) else None
    )
    return selected_workspace


if __name__ == "__main__":
    main()
