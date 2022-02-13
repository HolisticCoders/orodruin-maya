# Orodruin Maya
An [Orodruin](https://github.com/HolisticCoders/orodruin) implementation  for Autodesk Maya.

# Prerequisites
- [Poetry](https://python-poetry.org/) must be installed.
- Python 3.7+ must be installed.  
    If you use pyenv, run `pyenv install 3.7.9` and poetry will pick up on the proper version automatically
- [Orodruin](https://github.com/HolisticCoders/orodruin) must already be cloned.
- The [Orodruin Editor](https://github.com/HolisticCoders/orodruin-editor) must be cloned as well, next to the orodruin repository.
- The [Orodruin Node Library](https://github.com/HolisticCoders/orodruin-library) should also be cloned and registered (see repo readme)  
    This is not strictly necessary but without that, you won't have any node to create

# Installation
- Clone this repository next to orodruin's repository (this is imperative, poetry uses a relative path to orodruin's folder to use it as a dependency.)
- cd in `orodruin-maya`
- Run poetry install --no-dev to create a new virtual env and install all the dependencies.  
    Remove the --no-dev argument if you want the dev dependencies.
- Register the Maya module. This can be done in one of two ways:
    1. Add `/path/to/orodruin-maya/modules` to the environment variable `MAYA_MODULE_PATH`
    2. Move the file `/path/to/orodruin-maya/modules/OrodruinMaya.mod` to `C:/Users/<username>/Documents/maya/modules` (on Windows) and edit its content like so:
        ```
        + MAYAVERSION:2022 OrodruinMaya any /path/to/orodruin-maya/
        scripts: scripts
        ```
- Open the orodruin editor with the following snippet:  
    ```python
    from orodruin_maya.ui.editor_window import OrodruinMayaWindow
    OrodruinMayaWindow.open()
    ```