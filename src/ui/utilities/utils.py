from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog
import pandas as pd


def give_me_the_dummy_results():
    return """DUMMY TEXTSSS  1 @mins Unfortunately thats no longer correct. I swear this location changes every year –  West
                    Aug 18, 2022 at 7:14
                    Show 1 more comment
                    20 Answers
                    Sorted by:

                    Highest score (default)
                    53

                    If you are working in python virtual environment, in the command window

                    >>qt5-tools designer
                    can open designer window.

                    Share
                    Edit
                    Follow
                    answered Feb 4, 2021 at 6:48
                    Bhaskar's user avatar
                    Bhaskar
                    58811 gold badge44 silver badges99 bronze badges
                    1
                    This answer is a correct answer and deserves an up. – 
                    Edward Zhang
                    Apr 9, 2021 at 13:58
                    1
                    I'm not using venv, installed pyqt5-tools globally. This works. Thanks! – 
                    Omkar76
                    May 3, 2021 at 9:54
                    2
                    this works both in venv and in global enviorments. – 
                    Muneeb Ahmad Khurram
                    May 9, 2021 at 19:00
                    1
                    It works. Upvoted. – 
                    Neil T.
                    Jan 24, 2022 at 5:48
                    Add a comment
                    41

                    I struggled with this as well. The pyqt5-tools approach is cumbersome so I created a standalone installer for Qt Designer. It's only 40 MB. Maybe you will find it useful!

                    Share
                    Edit
                    Follow
                    answered Oct 28, 2018 at 14:45
                    Michael Herrmann's user avatar
                    Michael Herrmann
                    4,98333 gold badges3939 silver badges5353 bronze badges
                    7
                    This should be the top answer in my opinion. – 
                    Daniel Farrell
                    Mar 12, 2019 at 23:29
                    Can you update you installer is pretty old 5.11 :/ – 
                    emcek
                    Mar 29, 2021 at 20:24
                    2
                    This tool is seemingly for windows and mac only - do you have a solution for linux? – 
                    darthn
                    Dec 29, 2021 at 1:02
                    It is sad that it is not Open Source, could potentially contain spyware – 
                    satk0
                    May 17, 2023 at 16:32
                    Add a comment
                    26

                    The Qt designer is not installed with the pip installation.

                    You can either download the full download from sourceforge (probably won't be the last pyqt release, and might be buggy on presence of another installation, like yours) or install it with another (unofficial) pypi package - pyqt5-tools (pip install pyqt5-tools), then run the designer from the following subpath of your python directory:

                    ...\Python36\Lib\site-packages\qt5_applications\Qt\bin\designer.exe
                    or from (outdated):

                    ...\Python36\Lib\site-packages\pyqt5-tools\designer\designer.exe
                    Share
                    Edit
                    Follow
                    edited May 19, 2023 at 21:58
                    satk0's user avatar
                    satk0
                    41255 silver badges1414 bronze badges
                    answered Feb 7, 2017 at 13:24
                    Uriel's user avatar
                    Uriel
                    15.9k66 gold badges2727 silver badges4646 bronze badges
                    1
                    Thank you! pip install pyqt5-tools gave me a No matching distribution found, though, so I'll try sourceforge (kind of defeats the purpose of having pip, but ...). – 
                    User1291
                    Feb 7, 2017 at 13:32
                    4
                    Just tried again to install pyqt5-tools with pip, and all worked fine. – 
                    Uriel
                    Feb 7, 2017 at 13:34 
                    1
                    Yeah, browse the installations manually under the "files" tab (near "summary", under the title with the logo), then navigate to "PyQt5". – 
                    Uriel
                    Feb 7, 2017 at 14:05
                    1
                    @User1291. The current pyqt5-tools is for PyQt-5.7 not PyQt-5.7.1, so it's not compatible. However, you should be able to open the pyqt5-tools wheel like a zip file and extract the contents to a suitable location. You can then try running the designer.exe file in the pyqt5-tools/designer folder. – 
                    ekhumoro
                    Feb 7, 2017 at 21:10
                    4
                    I found it here: C:\Python37-32\Lib\site-packages\qt5_applications\Qt\bin – 
                    Captain Fantastic
                    Feb 22, 2021 at 5:07 
                    Show 8 more comments
                    23

                    The latest PyQt5 wheels (which can be installed via pip) only contain what's necessary for running applications, and don't include the dev tools. This applies to PyQt versions 5.7 and later. For PyQt versions 5.6 and earlier, there are binary packages for Windows that also include the dev tools, and these are still available at sourceforge. The maintainer of PyQt does not plan on making any further releases of such binary packages, though - only the runtime wheels will now be made available, and there will be no official wheels for the dev tools.

                    In light of this, someone has created an unofficial pyqt5-tools wheel (for Windows only). This appears to be in it's early stages, though, and so may not keep up with recent PyQt5 releases. This means that it may not always be possible to install it via pip. If that is the case, as a work-around, the wheel files can be treated as zip files and the contents extracted to a suitable location. This should then allow you to run the designer.exe file that is in the pyqt5-tools folder.

                    Finally, note that you will also see some zip and tar.gz files at sourceforge for PyQt5. These only contain the source code, though, so will be no use to you unless you intend to compile PyQt5 yourself. And just to be clear: compiling from source still would not give you all the Qt dev tools. If you go down that route, you would need to install the whole Qt development kit separately as well (which would then get you the dev tools).

                    Share
                    Edit
                    Follow
                    edited May 17, 2023 at 18:50
                    answered Feb 8, 2017 at 9:32
                    ekhumoro's user avatar
                    ekhumoro
                    119k2222 gold badges246246 silver badges356356 bronze badges
                    pyqt5-tools-wheel works from pip. After that, just start designer.exe from Python\Scripts folder. Thanks! – 
                    Hrvoje T
                    Jan 20, 2019 at 21:53
                    Add a comment
                    23

                    pip install pyqt5-tools
                    Then restart the cmd, just type "designer" and press enter.

                    Share
                    Edit
                    Follow
                    edited Jul 6, 2019 at 2:22
                    eyllanesc's user avatar
                    eyllanesc
                    241k1919 gold badges188188 silver badges265265 bronze badges
                    answered Jul 5, 2019 at 20:24
                    Sairaj Das's user avatar
                    Sairaj Das
                    23122 silver badges22 bronze badges
                    1
                    Thank you a thousand times! – 
                    Pedro Serpa
                    Aug 8, 2019 at 13:51
                    Add a comment
                    9

                    If you cannot see the Designer , just look into this path "Lib\site-packages\qt5_applications\Qt\bin" for designer.exe and run it.

                    Share
                    Edit
                    Follow
                    answered Jan 18, 2021 at 5:32
                    Saikiran Gutla's user avatar
                    Saikiran Gutla
                    13111 silver badge22 bronze badges
                    Thank you very much, I recently installed pyqt6-tools and was confused about this. This answer is perfect for me. IF you have already installed the tools and are unable to locate the designer then try this step. for QT6 look for Python39\Lib\site-packages\qt6_applications\Qt\bin and you will find the designer.exe – 
                    Abinash Tripathy
                    Jul 28, 2021 at 13:18
                    Add a comment
                    6

                    PyQt5 works after pip install PyQt5Designer

                    Share
                    Edit
                    Follow
                    answered Sep 5, 2020 at 18:29
                    user5816728's user avatar
                    user5816728
                    6111 silver badge33 bronze badges
                    This helped with Python 3.9 under Windows. Thanks. That got me QtDesigner. ... To get pyuic5 also going (to generate Python output) I had to also install pyuic5-tool with pip. – 
                    BarryM
                    Jan 15, 2021 at 6:08 
                    Add a comment
                    5

                    For anyone stumbling across this post in 2021+ and finding the answers outdated: QT Designer is now in the qt5-applications package, under Qt\bin\. On Windows this means the default path, for CPython 3.9 using the Python.org installer, is %APPDATA%\Python\Python39\site-packages\qt5_applications\Qt\bin\designer.exe.

                    Share
                    Edit
                    Follow
                    answered Jan 25, 2021 at 1:52
                    Ryan Plant's user avatar
                    Ryan Plant
                    1,03711 gold badge1111 silver badges1818 bronze badges
                    I wish there was a way to move posts to the top when the old ones are out of date. May 2022, Visual Studio Code - this is exactly where designer.exe now sits. – 
                    Andy Brown
                    May 24, 2022 at 8:40
                    Add a comment
                    5

                    pip install pyqt5-tools

                    working in python 3.7.4

                    wont work in python 3.8.0

                    Share
                    Edit
                    Follow
                    answered Nov 27, 2019 at 21:14
                    dima_showstopper's user avatar
                    dima_showstopper
                    5111 silver badge22 bronze badges
                    Add a comment
                    5

                    For Qt Designer 6 this worked for me thanks for that protip from @Bhaskar

                    pip install pyqt6-tools
                    Then started:

                    qt6-tools designer
                    End up with nice working lightweight Qt Designer 6.0.1 version enter image description here

                    @ pip install pyqt6-tools
                    Collecting pyqt6-tools
                    Using cached pyqt6_tools-6.1.0.3.2-py3-none-any.whl (29 kB)
                    Collecting pyqt6-plugins<6.1.0.3,>=6.1.0.2.2
                    Downloading pyqt6_plugins-6.1.0.2.2-cp39-cp39-manylinux2014_x86_64.whl (77 kB)
                        |████████████████████████████████| 77 kB 492 kB/s            
                    Collecting python-dotenv
                    Using cached python_dotenv-0.19.2-py2.py3-none-any.whl (17 kB)
                    Collecting pyqt6==6.1.0
                    Downloading PyQt6-6.1.0-cp36.cp37.cp38.cp39-abi3-manylinux_2_28_x86_64.whl (6.8 MB)
                        |████████████████████████████████| 6.8 MB 1.0 MB/s            
                    Requirement already satisfied: click in ./.pyenv/versions/3.9.6/lib/python3.9/site-packages (from pyqt6-tools) (8.0.1)
                    Collecting PyQt6-sip<14,>=13.1
                    Downloading PyQt6_sip-13.2.0-cp39-cp39-manylinux1_x86_64.whl (307 kB)
                        |████████████████████████████████| 307 kB 898 kB/s            
                    Collecting PyQt6-Qt6>=6.1.0
                    Using cached PyQt6_Qt6-6.2.2-py3-none-manylinux_2_28_x86_64.whl (50.0 MB)
                    Collecting qt6-tools<6.1.0.2,>=6.1.0.1.2
                    Downloading qt6_tools-6.1.0.1.2-py3-none-any.whl (13 kB)
                    Collecting click
                    Downloading click-7.1.2-py2.py3-none-any.whl (82 kB)
                        |████████████████████████████████| 82 kB 381 kB/s            
                    Collecting qt6-applications<6.1.0.3,>=6.1.0.2.2
                    Downloading qt6_applications-6.1.0.2.2-py3-none-manylinux2014_x86_64.whl (80.5 MB)
                        |████████████████████████████████| 80.5 MB 245 kB/s            
                    Installing collected packages: qt6-applications, PyQt6-sip, PyQt6-Qt6, click, qt6-tools, pyqt6, python-dotenv, pyqt6-plugins, pyqt6-tools
                    Attempting uninstall: click
                        Found existing installation: click 8.0.1
                        Uninstalling click-8.0.1:
                        Successfully uninstalled click-8.0.1
                    Successfully installed PyQt6-Qt6-6.2.2 PyQt6-sip-13.2.0 click-7.1.2 pyqt6-6.1.0 pyqt6-plugins-6.1.0.2.2 pyqt6-tools-6.1.0.3.2 python-dotenv-0.19.2 qt6-applications-6.1.0.2.2 qt6-tools-6.1.0.1.2

                    Share
                    Edit
                    Follow
                    answered Jan 20, 2022 at 13:54
                    Mike R's user avatar
                    Mike R
                    8191010 silver badges1414 bronze badges
                    Add a comment
                    5

                    You can also install Qt Designer the following way:

                    Install latest Qt (I'm using 5.8) from Qt main site
                    Make sure you include "Qt 5.8 MinGW" component
                    Qt Designer will be installed in C:\Qt\5.8\mingw53_32\bin\designer.exe
                    Note that the executable is named "designer.exe"
                    Share
                    Edit
                    Follow
                    edited Jul 6, 2019 at 2:23
                    eyllanesc's user avatar
                    eyllanesc
                    241k1919 gold badges188188 silver badges265265 bronze badges
                    answered Apr 5, 2017 at 11:46
                    akej74's user avatar
                    akej74
                    1,2241111 silver badges99 bronze badges
                    Add a comment
                    4

                    Download the module using pip:

                    pip install PyQt5Designer"

                    def select_directory_from_pc():
                        # Klasör seçme dialogu açılır
                        folder_path = QFileDialog.getExistingDirectory(caption="Select Data Directory")

                        if folder_path:
                            # # Seçilen klasörün yolu
                            # path = Path(str(folder_path))

                            # # Klasör yolunu döndür
                            # return path

                            return folder_path

                        return None"""


def select_directory_from_pc():
    # Klasör seçme dialogu açılır
    folder_path = QFileDialog.getExistingDirectory(caption="Select Data Directory")

    if folder_path:
        # # Seçilen klasörün yolu
        # path = Path(str(folder_path))

        # # Klasör yolunu döndür
        # return path

        return folder_path

    return None


def show_error_message(message):
    error_message_box = QMessageBox()
    error_message_box.setIcon(QMessageBox.Critical)
    error_message_box.setText(str(message))
    error_message_box.setWindowTitle("Error")
    error_message_box.setStandardButtons(QMessageBox.Ok)
    error_message_box.exec_()


def show_info_message(message):
    info_message_box = QMessageBox()
    info_message_box.setIcon(QMessageBox.Information)
    info_message_box.setText(str(message))
    info_message_box.setWindowTitle("Info")
    info_message_box.setStandardButtons(QMessageBox.Ok)
    info_message_box.exec_()


def notification_message(message):
    message_object = QMessageBox()
    message_object.setText(message)
    message_object.setWindowTitle("Dataset Deletiond!")
    message_object.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    message_object.setEscapeButton(QMessageBox.No)
    result = message_object.exec_()

    if result == QMessageBox.Yes:
        return True

    return False
