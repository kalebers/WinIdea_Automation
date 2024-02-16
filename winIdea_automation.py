import subprocess
import isystem.connect as ic
from ws_cfg import WorkspaceConfigurator
import glob
import keyboard
import os
import time
import py_canoe  # to use it need to do: pip install py_canoe --upgrade
import pandas as pd

# Paths for the .xjrf Workspace files to be used and the path for the .exe WinIdea.
# CHANGE THE PATHS FOR THE OTHER ODIS
ws_paths = []

winIdea_exe = ""


# CANoe configuration
canoe_config_file = ""  # Replace with CANoe configuration path file
ecu_node_name = "ECU_Node"  # Replace with the name of the ECU node in CANoe


# workspace opening and setup for the right workspace selection
def run_workspace(ws_path):
    subprocess.run([winIdea_exe, ws_path])


def prompt_user_for_workspace():
    print("Select a workspace:")
    for i, ws_path in enumerate(ws_paths, start=1):
        print(f"{i}. {ws_path}")

    user_input = input("Enter the number corresponding to the workspace: ")
    selected_workspace = (
        ws_paths[int(user_input) - 1] if 1 <= int(user_input) <= len(ws_paths) else None
    )
    return selected_workspace


def search_files(paths, extensions):
    result_files = []
    for path in paths:
        for extension in extensions:
            files = glob.glob(
                os.path.join(path, f"*.{extension}"), recursive=True
            )  # recursive=True makes possible to search files in subdirectories.
            result_files.extend(files)
    return result_files


# TODO: show a confirmation of which DS in being selected by the parcode and search the same DS inthe folders (or the hex file correspondent to the DS)
# List of parcodes and datasets for each car/project
# TODO: need to get a way to update the DS list without needing to do manually (see a possible list of DS and extract ta a file and use it here everytime when running this script)
# TODO: the list of DS inside the DS_Container folder from MEB and MQB are different. Try to get the .xlsx file correspondent to the CH type and read it here (ZipContainerList_BLorUNE_XXCH_XXXX.xlsx)
# TODO: idea to start looking for the excel file to read it and extract the exact parcode and DS value to be used
parcode_dict = {}


def read_parcode_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        parcode_dict = dict(zip(df["Parcode"], df["Dataset"]))
        return parcode_dict
    except Exception as e:
        print(f"Error reading Excel file: {e}")


# prompting the user to select the right parcode
def prompt_user_for_parcode():
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


def prompt_user_for_canoe():
    # Prompt the user to confirm CANoe configuration
    user_input = input(
        "Do you want to start CANoe for ECU information? (y/n): "
    ).lower()
    return user_input == "y"


def configure_canoe():
    # Configure and start CANoe
    canoe = py_canoe.CANoe()
    canoe.open_configuration(canoe_config_file)
    canoe.start_measurement()
    return canoe


def stop_canoe(canoe):
    # Stop CANoe
    canoe.stop_measurement()
    canoe.close_configuration()


def ecu_reset():
    debugCtrl.resetECU()


def ecu_mass_erase():
    debugCtrl.eraseECU()


def main():
    # Prompt the user to select the right software version
    software_folder_name = input("Enter the software folder name:")
    channel_type = input(
        "Enter the channel type(MEB_LOW_4CH, MEB_LOW, MEB_HIGH, UNE_04CH or 8CH or 12CH, BL_04CH or 8CH or 12CH_HIGH or 12CH_LOW 12CH or 8CH or 4CH_BL_High):"
    )
    car_platform = input("Enter car platform (e.g., MEB, MQB):")

    # Construct search paths based on the software version
    # TODO: for the cal_merge, need to get a input from user to select the wright car parcode. (INSIDE OF THE DS container, take the excel file with all the parcodes)
    search_paths = [
        # TODO: make sure that all folders for channel_type are the same name
        # wright SW path:
        # C:\0_SW\something
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_FBL\\4M\\{channel_type}\\Exe",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_FBL\\{channel_type}\\Exe",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_FBL\\{channel_type}\\Exec",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_OUT\\{channel_type}\\NVM",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_OUT\\{channel_type}\\CAL",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_OUT\\{channel_type}\\CAL_ML_MERGE",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_OUT\\{channel_type}\\BIN",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_OUT\\Data_Set_HEX\\{channel_type}\\CAL_ML_MERGE"
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\Internal\\SW_OUT\\Data_Set_HEX\\{channel_type}\\NVM"
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_FBL\\4M\\{channel_type}\\Exe",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_FBL\\{channel_type}\\Exe",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_FBL\\{channel_type}\\Exec",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_OUT\\{channel_type}\\NVM",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_OUT\\{channel_type}\\CAL",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_OUT\\{channel_type}\\CAL_ML_MERGE",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_OUT\\{channel_type}\\BIN",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_OUT\\Data_Set_HEX\\{channel_type}\\CAL_ML_MERGE"
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_OUT\\Data_Set_HEX\\{channel_type}\\NVM",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_OUT\\Data_Set_HEX\\{channel_type}\\CAL",
        f"C:\\0_SW\\{car_platform}\\{software_folder_name}\\INTERNAL\\SW_OUT\\Data_Set_HEX\\{channel_type}\\CAL_ML_MERGE",
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

    parcode_excel_path1 = "insert excel path"
    parcode_excel_path2 = "insert excel path"

    parcode_dict1 = read_parcode_excel(parcode_excel_path1)
    parcode_dict2 = read_parcode_excel(parcode_excel_path2)

    if not parcode_dict1 or not parcode_dict2:
        print("invalid parcode Excel. Exiting")
        return

    selected_parcode = prompt_user_for_parcode()
    if selected_parcode:
        print(f"Selected Parcode: {selected_parcode}")
        # Access the dataset name using selected_parcode as the key
        selected_dataset = parcode_dict[selected_parcode]
        print(f"Dataset Name: {selected_dataset}")

    wsCfg = WorkspaceConfigurator(ic.ConnectionMgr())

    selected_workspace = prompt_user_for_workspace()
    if selected_workspace:
        run_workspace(selected_workspace)
    else:
        print("Invalid selection. No workspace selected\ERROR")

    wsCfg.add_symbol_file("myApplication0", elf_file, "ELF")
    wsCfg.add_program_file(elf_file, "ELF")

    # TODO: add the function files for download
    # TODO: check if the download function is working
    # calling thereset and mass_erase functions
    ecu_reset()
    ecu_mass_erase()

    cmgr = ic.ConnectionMgr()
    cmgr.connectMRU("")
    wsCfg = WorkspaceConfigurator(cmgr)
    wsCfg.set_emulator_type("iC5000")
    wsCfg.set_USB_comm("iC5000 (SN 61174)")
    wsCfg.set_SoC("LS1012A")
    wsCfg.add_memory_space("memorySpace0", "Core0", "myApplication0")
    wsCfg.set_demo_mode(True)
    # Download
    debugCtrl = ic.CDebugFacade(cmgr)
    debugCtrl.download()

    # Start CANoe if the user wants to monitor ECU information
    if prompt_user_for_canoe():
        canoe = configure_canoe()

        # Wait for a while (adjust as needed) to allow monitoring during flashing
        time.sleep(10)

        # Stop CANoe after flashing is complete
        stop_canoe(canoe)

    wsCfg.save_workspace()
    wsCfg.close_workspace()


if __name__ == "__main__":
    main()
