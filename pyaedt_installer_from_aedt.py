# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import os
import platform
import shutil
import sys

try:
    import subprocess  # nosec
except ImportError:
    import subprocessdotnet as subprocess  # nosec

is_iron_python = platform.python_implementation().lower() == "ironpython"
is_linux = os.name == "posix"
is_windows = not is_linux
VENV_DIR_PREFIX = ".pyaedt_env"
"""
It is possible create Python virtual environment in a specific directory by setting
variable VENV_DIR.
For example, VENV_DIR = "e:/pyaedt_env"
"""
VENV_DIR = None
if not VENV_DIR:
    if is_windows:
        VENV_DIR = os.path.join(os.environ["APPDATA"], VENV_DIR_PREFIX)
    else:
        VENV_DIR = os.path.join(os.environ["HOME"], VENV_DIR_PREFIX)

DISCLAIMER = (
    "This script will download and install certain third-party software and/or "
    "open-source software (collectively, 'Third-Party Software'). Such Third-Party "
    "Software is subject to separate terms and conditions and not the terms of your "
    "Ansys software license agreement. Ansys does not warrant or support such "
    "Third-Party Software.\n"
    "Do you want to proceed ?"
)


def _show_error_message(oDesktop, message):
    """Show error message in AEDT message window and in a message box."""
    from System.Windows.Forms import MessageBox
    from System.Windows.Forms import MessageBoxButtons
    from System.Windows.Forms import MessageBoxIcon

    err_msg = "There was an error while installing PyAEDT. Please check the log files."
    oDesktop.AddMessage("", "", 2, err_msg)
    err_msg = "There was an error while installing PyAEDT, below is the " \
              "associated stderr:\n\n{}".format(message)
    MessageBox.Show(err_msg, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)


def run_pyinstaller_from_c_python(oDesktop):
    import tempfile

    # Iron Python script to create the virtual environment and install PyAEDT

    # Get AEDT information
    version = oDesktop.GetVersion()[2:6].replace(".", "")
    # From AEDT 2023.2 the installed CPython version is 3.10
    # From AEDT 2027.1 the installed CPython version is 3.13
    if version <= "231":
        python_version = "3.7"
    elif version <= "271":
        python_version = "3.10"
    else:
        python_version = "3.13"
    python_version_new = python_version.replace(".", "_")

    # AEDT installation root
    edt_root = os.path.normpath(oDesktop.GetExeDir())

    # CPython interpreter executable
    if is_windows:
        python_exe = os.path.normpath(
            os.path.join(
                edt_root,
                "commonfiles",
                "CPython",
                python_version_new,
                "winx64",
                "Release",
                "python",
                "python.exe",
            )
        )
    else:
        python_exe = os.path.normpath(
            os.path.join(
                edt_root,
                "commonfiles",
                "CPython",
                python_version_new,
                "linx64",
                "Release",
                "python",
                "runpython",
            )
        )

    # Launch this script again from the CPython interpreter. This calls the
    # ``install_pyaedt()`` method, which creates a virtual environment and
    # installs PyAEDT and its dependencies
    command = [python_exe, os.path.normpath(__file__), "--version=" + version]
    if is_student_version(oDesktop):
        command.append("--student")
    if is_linux:
        command.extend([
            r"--edt_root={}".format(edt_root),
            '--python_version="{}"'.format(python_version),
        ])
    # wheelpyaedt must be a string, not a list
    if wheelpyaedt:
        command.extend([r"--wheel={}".format(wheelpyaedt)])

    oDesktop.AddMessage("", "", 0, "Installing PyAEDT...")

    # Redirect stdout and stderr to temporary files to avoid deadlocks on pipes
    stdout_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".out")
    stderr_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".err")

    oDesktop.AddMessage("", "", 0, "Log files associated with the installation:")
    oDesktop.AddMessage("", "", 0, "STDOUT: {}".format(stdout_file.name))
    oDesktop.AddMessage("", "", 0, "STDERR: {}".format(stderr_file.name))

    try:
        proc = subprocess.Popen(command, stdout=stdout_file, stderr=stderr_file)
        proc.wait()
    except Exception as e:
        _show_error_message(oDesktop, str(e))
        return
    finally:
        stdout_file.close()
        stderr_file.close()

    if proc.returncode != 0:
        message = "Installation process failed, please check the log files content."
        _show_error_message(oDesktop, message)
        return
    else:
        oDesktop.AddMessage("", "", 0, "PyAEDT virtual environment created.")

    # Add PyAEDT tabs in AEDT
    # Virtual environment path and Python executable
    if is_windows:
        venv_dir = os.path.join(VENV_DIR, python_version_new)
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_dir = os.path.join(VENV_DIR, python_version_new)
        python_exe = os.path.join(venv_dir, "bin", "python")

    # Create Toolkits in PersonalLib
    python_script = os.path.join(tempfile.gettempdir(), "configure_pyaedt.py")
    if os.path.isfile(python_script):
        os.remove(python_script)
    with open(python_script, "w") as f:
        f.write("from ansys.aedt.core.extensions.installer.version_manager import add_pyaedt_to_aedt\n")
        f.write('add_pyaedt_to_aedt(personal_lib=r"{}")\n'.format(oDesktop.GetPersonalLibDirectory()))

    oDesktop.AddMessage("", "", 0, "Configuring PyAEDT panels in automation tab.")

    # Reopen the log files to append configuration output
    stdout_file = open(stdout_file.name, "a")
    stderr_file = open(stderr_file.name, "a")

    try:
        proc = subprocess.Popen([python_exe, python_script], stdout=stdout_file, stderr=stderr_file)
        proc.wait()
    except Exception as e:
        oDesktop.AddMessage("", "", 2, "Error occurred configuring the PyAEDT panels: {}".format(str(e)))
        return
    finally:
        stdout_file.close()
        stderr_file.close()

    if proc.returncode != 0:
        message = "Configuration process failed, please check the log files content."
        oDesktop.AddMessage("", "", 2, message)
        return
    else:
        oDesktop.AddMessage("", "", 0, "PyAEDT panels configured successfully.")

    try:
        os.unlink(stdout_file.name)
        os.unlink(stderr_file.name)
    except Exception as e:
        oDesktop.AddMessage("", "", 1, "Error cleaning temp files: {}".format(str(e)))

    # Refresh UI
    oDesktop.CloseAllWindows()
    if version >= "232":
        oDesktop.RefreshToolkitUI()

    msg = "PyAEDT configuration complete."
    if is_linux:
        msg += (
            " Please ensure Ansys Electronics Desktop is launched in gRPC mode "
            "(i.e. launch ansysedt with -grpcsrv"
            " argument) to take advantage of the new toolkits."
        )

    if "GetIsNonGraphical" in oDesktop.__dir__() and not oDesktop.GetIsNonGraphical():
        from System.Windows.Forms import MessageBox
        from System.Windows.Forms import MessageBoxButtons
        from System.Windows.Forms import MessageBoxIcon

        oDesktop.AddMessage("", "", 0, msg)
        MessageBox.Show(msg, "Info", MessageBoxButtons.OK, MessageBoxIcon.Information)
        oDesktop.AddMessage("", "", 0, "Create a project if the PyAEDT panel is not visible.")


def parse_arguments_for_pyaedt_installer(args=None):
    parser = argparse.ArgumentParser(description="Install PyAEDT")
    if is_linux:
        parser.add_argument("--edt_root", help="AEDT's path (required for Linux)", required=True)
        parser.add_argument("--python_version", help="Python version (required for Linux)", required=True)
    parser.add_argument("--version", "-v", help="AEDT's 3 digit version", required=True)
    parser.add_argument("--student", "--student_version", "-sv", help="Is Student version", action="store_true")
    parser.add_argument("--wheel", "--wheel_house", "-whl", type=str, help="Wheel house path")
    args = parser.parse_args(args)
    if len(sys.argv[1:]) == 0 and args is None:
        parser.print_help()
        parser.error("No arguments given!")
    return args


def unzip_if_zip(path):
    """Unzip path if it is a ZIP file into a temporary directory.
    If the zip contains nested zip files, extract them recursively until
    there are no more zip files inside.
    Returns the deepest directory that contains all the .whl files (common ancestor).
    If no .whl files are found but nested zip extraction occurred, returns the last extracted folder.
    If the provided path is not a zip file, the original Path is returned.
    """
    from pathlib import Path
    import tempfile
    import zipfile

    path = Path(path)

    # If not a zip file, return as-is
    if not path.is_file() or path.suffix.lower() != ".zip":
        return path

    # Create a dedicated temporary directory for extraction
    top_dir = Path(tempfile.mkdtemp(prefix="pyaedt_unzip_"))

    # Extract the top-level zip into the temp dir
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(top_dir)

    last_unzipped = None

    # Recursively find and extract any nested zip files until none remain
    while True:
        nested_zips = list(top_dir.rglob("*.zip"))
        if not nested_zips:
            break

        nested_zips.sort()

        for zpath in nested_zips:
            try:
                target_dir = zpath.with_suffix("")
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                with zipfile.ZipFile(zpath, "r") as zf:
                    zf.extractall(target_dir)
                last_unzipped = target_dir
            finally:
                try:
                    zpath.unlink()
                except Exception:  # nosec B110
                    pass

    # Find all wheel files under the extracted tree
    wheels = list(top_dir.rglob("*.whl"))
    if wheels:
        parents = [str(w.parent) for w in wheels]
        common = Path(os.path.commonpath(parents))
        try:
            common = common.resolve()
            top_dir_resolved = top_dir.resolve()
            if str(common).startswith(str(top_dir_resolved)):
                return common
        except Exception:
            return top_dir
        return top_dir

    if last_unzipped is not None and last_unzipped.exists():
        return last_unzipped

    return top_dir


def install_pyaedt():
    """Install PyAEDT in CPython."""
    from pathlib import Path

    args = parse_arguments_for_pyaedt_installer()
    python_version = "3_13"
    if args.version <= "231":
        python_version = "3_7"
    elif args.version <= "261":
        python_version = "3_10"

    if is_windows:
        venv_dir = Path(VENV_DIR, python_version)
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        uv_exe = venv_dir / "Scripts" / "uv.exe"
    else:
        venv_dir = Path(VENV_DIR, python_version)
        pip_exe = venv_dir / "bin" / "pip"
        uv_exe = venv_dir / "bin" / "uv"

    os.environ["ANSYSEM_ROOT{}".format(args.version)] = args.edt_root
    if is_linux:
        os.environ["TK_LIBRARY"] = r"{}/commonfiles/CPython/{}/linx64/Release/python/lib/tk8.5".format(
            args.edt_root, args.python_version.replace(".", "_")
        )
        os.environ["TCL_LIBRARY"] = r"{}/commonfiles/CPython/{}/linx64/Release/python/lib/tcl8.5".format(
            args.edt_root, args.python_version.replace(".", "_")
        )

    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv_dir)
    env["PATH"] = str(venv_dir / "Scripts") + os.pathsep + env.get("PATH", "")
    env["UV_HTTP_TIMEOUT"] = "1000"

    if not venv_dir.exists():
        print("Creating the virtual environment in {}".format(venv_dir))
        if args.version <= "231":
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir), "--system-site-packages"], check=True)  # nosec
        else:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)  # nosec

    if args.wheel and Path(args.wheel).exists():
        unzipped_path = unzip_if_zip(Path(args.wheel))
        print("Installing PyAEDT using provided wheels argument with pip")
        command = [str(pip_exe), "install", "--no-cache-dir", "--find-links", str(unzipped_path), "pyaedt[all]"]
        subprocess.run(command, check=True, env=env)  # nosec
    else:
        try:
            print("Installing uv in the virtual environment...")
            subprocess.run([str(pip_exe), "--default-timeout=1000", "install", "uv"], check=True, env=env)  # nosec
            print("Installing PyAEDT using online sources with uv...")
            subprocess.run([str(uv_exe), "pip", "install", "--upgrade", "pip"], check=True, env=env)  # nosec
            subprocess.run([str(uv_exe), "pip", "install", "wheel"], check=True, env=env)  # nosec
            if args.version <= "231":
                subprocess.run([str(uv_exe), "pip", "install", "pyaedt[all]=='0.9.0'"], check=True, env=env)  # nosec
                subprocess.run([str(uv_exe), "pip", "install", "jupyterlab"], check=True, env=env)  # nosec
                subprocess.run([str(uv_exe), "pip", "install", "ipython", "-U"], check=True, env=env)  # nosec
                subprocess.run([str(uv_exe), "pip", "install", "ipyvtklink"], check=True, env=env)  # nosec
            else:
                subprocess.run([str(uv_exe), "pip", "install", "pyaedt[all]"], check=True, env=env)  # nosec
        except subprocess.CalledProcessError as e:
            print("uv installation failed with error: {}".format(e))
            print("Falling back to pip for package installation...")
            subprocess.run([str(pip_exe), "--default-timeout=1000", "install", "--upgrade", "pip"], check=True, env=env)  # nosec
            subprocess.run([str(pip_exe), "--default-timeout=1000", "install", "wheel"], check=True, env=env)  # nosec
            if args.version <= "231":
                subprocess.run(
                    [str(pip_exe), "--default-timeout=1000", "install", "pyaedt[all,dotnet]=='0.9.0'"],
                    check=True,
                    env=env,
                )  # nosec
                subprocess.run([str(pip_exe), "--default-timeout=1000", "install", "jupyterlab"], check=True, env=env)  # nosec
                subprocess.run([str(pip_exe), "--default-timeout=1000", "install", "ipython", "-U"], check=True, env=env)  # nosec
                subprocess.run([str(pip_exe), "--default-timeout=1000", "install", "ipyvtklink"], check=True, env=env)  # nosec
            else:
                subprocess.run([str(pip_exe), "--default-timeout=1000", "install", "pyaedt[all]"], check=True, env=env)  # nosec

    if args.version <= "231":
        try:
            subprocess.run([str(uv_exe), "pip", "uninstall", "pywin32"], check=True, env=env)  # nosec
        except subprocess.CalledProcessError:
            pass
    sys.exit(0)


def is_student_version(oDesktop):
    edt_root = os.path.normpath(oDesktop.GetExeDir())
    if is_windows and os.path.isdir(edt_root):
        if any("ansysedtsv" in fn.lower() for fn in os.listdir(edt_root)):
            return True
    return False


def validate_disclaimer():
    """Display dialog box and evaluate the response to the disclaimer."""
    from System.Windows.Forms import DialogResult
    from System.Windows.Forms import MessageBox
    from System.Windows.Forms import MessageBoxButtons

    response = MessageBox.Show(DISCLAIMER, "Disclaimer", MessageBoxButtons.YesNo)
    return response == DialogResult.Yes


if __name__ == "__main__":
    if is_iron_python:
        if "GetIsNonGraphical" in oDesktop.__dir__() and oDesktop.GetIsNonGraphical():
            print("When using IronPython, this script is expected to be run in graphical mode.")
            sys.exit(1)

        if validate_disclaimer():
            oDesktop.AddMessage("", "", 0, "Disclaimer accepted.")

            # FIX: wheelpyaedt must be a string, not a list
            wheelpyaedt = ""

            # Retrieve the script arguments. ScriptArgument may be undefined in
            # some IronPython/AEDT configurations, so guard with try/except.
            try:
                script_args = ScriptArgument.split()
            except NameError:
                script_args = []

            if len(script_args) == 1:
                wheelpyaedt = script_args[0]

            # FIX: safe existence check (wheelpyaedt is a string here)
            if not wheelpyaedt or not os.path.exists(wheelpyaedt):
                wheelpyaedt = ""

            run_pyinstaller_from_c_python(oDesktop)
        else:
            oDesktop.AddMessage("", "", 1, "Disclaimer refused, installation canceled.")
    else:
        install_pyaedt()