from pywinauto.application import Application
import os
import wget
import requests
import zipfile
import json


confirm = False
while not confirm:
    install = False
    device = "E"
    secure_boot = False
    partition_style = "GPT"

    windows = "10"
    bypass = False
    if windows == "11":
        bypass = True
    if bypass == True:
        bypass = "1"
    else:
        bypass = "0"
        
    release = "Latest"
    edition = "Pro"
    language = "English"
    arch = "x64"
    
    post_tweaks = True
    
    confirm = True
    
iso_dir = f"{device}:/ISO/"
ventoy_dir = f"{device}:/ventoy/"
scripts_dir = ventoy_dir + "script/"

ventoy_config = {
        'control': [{'VTOY_DEFAULT_MENU_MODE': '1'},
                    {'VTOY_WIN11_BYPASS_CHECK': bypass},
                    {'VTOY_DEFAULT_SEARCH_ROOT': iso_dir.removeprefix(device + ":/")}],
        'auto_install': [{'parent': iso_dir.removeprefix(device + ":/"), 'template': [scripts_dir.removeprefix(device + ":/") + 'unattend.xml']}]
}

def ventoy():    
    response = requests.get("https://api.github.com/repos/ventoy/Ventoy/releases/latest").json()
    url = response["assets"][3]["browser_download_url"]
    filename = wget.filename_from_url(url)
    ventoy_dir = "ventoy/"
    
    def download():
        wget.download(url)
        with zipfile.ZipFile(filename) as zip:
            for file in zip.namelist():
                check = False
                for exception in ["VentoyPlugson.exe", "VentoyVlnk.exe", "altexe", "FOR_X64_ARM.txt"]:
                    if exception in file:
                        check = True
                        continue
                if check:
                    continue
                zip.extract(file)
        os.rename(zip.namelist()[0], ventoy_dir)
        os.remove(filename)
        
    if not os.path.exists(ventoy_dir):
        print("\nDownloading Ventoy...")
        download()
    else:
        with open(ventoy_dir + "ventoy/version", "r") as f:
            if f.read().replace("\n", "") not in response["tag_name"]:
                print("\nUpdating Ventoy...")
                os.remove(ventoy_dir)
                download()
    
    print("\nInstalling Ventoy on your device...")
    os.chdir(ventoy_dir)
    app = Application(backend="uia").start("Ventoy2Disk.exe")

    window = app.Ventoy2Disk
    window.wait('visible')

    devices = window.ComboBox.wrapper_object()
    devices.click_input()
    while True:
        if device.upper() in devices.selected_text():
            break
        devices.type_keys("{DOWN}")

    window.Option.click_input()
    if secure_boot:
        window.SecureBootSupport.click_input()
        window.Option.click_input()

    window.PartitionStyle.click_input()
    window.child_window(best_match=partition_style).click_input()

    if install:
        window.Install.click_input()
    else:
        window.Update.click_input()
    window.Yes.click_input()

    while True:
        if window.OK.exists():
            window.OK.click_input() 
            break

    window.close()
    os.chdir("..")
    print("\nVentoy installed!")


def fido():
    url = "https://raw.githubusercontent.com/pbatard/Fido/master/Fido.ps1"
    filename = wget.filename_from_url(url)
    
    if not os.path.exists(filename):
        print("\nDownloading Fido script...")
        wget.download(url)
    
    windows_url = os.popen(f"powershell -ExecutionPolicy Bypass -File {filename} -Win {windows} -Rel {release} -Ed {edition} -Lang {language} -Arch {arch} -GetUrl").read()
    windows_filename = wget.filename_from_url(windows_url)
    
    if not os.path.exists(iso_dir + windows_filename):
        print(f"\nInstalling {windows_filename} on your device...")
        os.makedirs(iso_dir)
        wget.download(windows_url, out=iso_dir)

def script():
    response = requests.get("https://api.github.com/repos/ArtanisInc/Post-Tweaks/releases/latest").json()
    url = response["zipball_url"]
    filename = wget.filename_from_url(url)
    
    if not os.path.exists(scripts_dir + filename):
        print(f"\nInstalling PostTweaks script on your device...")
        wget.download(url, out=scripts_dir)
        with zipfile.ZipFile(scripts_dir + filename) as zip:
            for file in zip.namelist():
                check = False
                for exception in ["LICENSE.md", "README.md"]:
                    if exception in file:
                        check = True
                        continue
                if check:
                    continue
                zip.extract(file)
        os.rename(zip.namelist()[0], "PostTweaks/")
        os.remove(filename)
        
    if not os.path.exists(ventoy_dir + "script.json", "w"):
        with open(ventoy_dir + "script.json", "w") as f:
            json.dump(ventoy_config, f, indent=4)
    
ventoy()
fido()
script()
