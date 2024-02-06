import subprocess
import isystem.connect as ic
from ws_cfg import WorkspaceConfigurator
import glob
import keyboard
import os

# Paths for the .xjrf Workspace files to be used and the path for the .exe WinIdea.
# CHANGE THE PATHS FOR THE OTHER ODIS
ws_paths = [
   
]

winIdea_exe = ""


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


# TODO: show a confirmation of which DS in being selected by the parcode.
# List of parcodes and datasets for each car/project
# TODO: need to get a way to update the DS list without needing to do manually (see a possible list of DS and extract ta a file and use it here everytime when running this script)
parcode_dict = {
    
}


# pronpting the suer to select the right parcode
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


def main():
    # Prompt the user to select the right software version
    software_version = input("Enter the software version (e.g., MEB_UNECE, MQB): ")
    channel_type = input(
        "Enter the channel type(MEB_LOW_4CH, MEB_LOW, MEB_HIGH, UNE_04CH 8CH 12CH, BL_04CH 8CH 12CH_HIGH 12CH_LOW): "
    )
    car_platform = input("Enter car platform (e.g., MEB, MQB): ")

    # Construct search paths based on the software version
    # TODO: for the cal_merge, need to get a input from user to select the wright car parcode. (INSIDE OF THE DS container, take the excel file with all the parcodes)
    search_paths = [
        # f"C:\\_01_SW\\00_MEB_UNECE\\{software_version}\\Internal\\SW_FBL\\4M\\12CH_BL_High\\Exe",
        # f"C:\\_01_SW\\00_MEB_UNECE\\{software_version}\\Internal\\SW_OUT\\UNE_12CH\\NVM",
        # f"C:\\_01_SW\\00_MEB_UNECE\\{software_version}\\Internal\\SW_OUT\\UNE_12CH\\CAL_ML_MERGE",
        # TODO: map all the different paths for the extension files, and insert a input field for user select different channels (4CH, 8CH or 12CH low HIGH),
        #
        # wright SW path:
        # C:\0_SW\something
        f"C:\\0_SW\\{car_platform}\\{software_version}\\Internal\\SW_FBL\\4M\\{channel_type}\\Exe",
        f"C:\\0_SW\\{car_platform}\\{software_version}\\Internal\\SW_FBL\\{channel_type}\\Exe",
        f"C:\\0_SW\\{car_platform}\\{software_version}\\Internal\\SW_OUT\\{channel_type}\\NVM",
        f"C:\\0_SW\\{car_platform}\\{software_version}\\Internal\\SW_OUT\\{channel_type}\\CAL_ML_MERGE",
        f"C:\\0_SW\\{car_platform}\\{software_version}\\Internal\\SW_OUT\\Data_Set_HEX\\{channel_type}\\CAL_ML_MERGE"
        f"C:\\0_SW\\{car_platform}\\{software_version}\\Internal\\SW_OUT\\Data_Set_HEX\\{channel_type}\\NVM"
        "path/to/your/files2",
        # Add more paths as needed
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

    cmgr = ic.ConnectionMgr()
    cmgr.connectMRU("")
    wsCfg = WorkspaceConfigurator(cmgr)
    # WORKSPACE_NAME = "PP6_VW_MEB.xjrf"
    # wsCfg.create_workspace(WORKSPACE_NAME)
    wsCfg.set_emulator_type("iC5000")
    wsCfg.set_USB_comm("iC5000 (SN 12345)")
    # wsCfg.set_TCP_comm(IP='12.34.56.78', port='1234')
    wsCfg.set_SoC("LS1012A")
    # wsCfg.add_application("myApplication0")
    # wsCfg.add_symbol_file("myApplication0", "program.elf", "ELF")
    wsCfg.add_memory_space("memorySpace0", "Core0", "myApplication0")
    # wsCfg.add_program_file("program.elf", "ELF")
    wsCfg.set_demo_mode(True)
    # Download
    debugCtrl = ic.CDebugFacade(cmgr)
    debugCtrl.download()
    wsCfg.save_workspace()
    wsCfg.close_workspace()


if __name__ == "__main__":
    main()
