# Orodruin Maya
An implementation [Orodruin](https://github.com/HolisticCoders/orodruin) for Autodesk Maya.

# Prerequisites
- [Poetry](https://python-poetry.org/) must be installed.
- Python 3.7+ must be installed.  
    If you use pyenv, run `pyenv install 3.7.9` and poetry will pick up on the proper version automatically
- [Orodruin](https://github.com/HolisticCoders/orodruin) must already be cloned.
- The [Orodruin Editor](https://github.com/HolisticCoders/orodruin-editor) must be cloned as well, next to the orodruin repository.
- The [Orodruin Component Library](https://github.com/HolisticCoders/orodruin-library) should also be cloned and registered (see repo readme)  
    This is not strictly necessary but without that, you won't have any component to create

# Installation
- Clone this repository next to orodruin's repository (this is imperative, poetry uses a relative path to orodruin's folder to use it as a dependency.)
- cd in `orodruin-maya`
- Run poetry config virtualenvs.in-project true --local to make sure poetry will create the virtualenv inside the project folder.  
    Note: Skip the --local argument if you want that behavior in every project.
- Run poetry install --no-dev to create a new virtual env and install all the dependencies.  
    Remove the --no-dev argument if you want the dev dependencies.
- Open the orodruin editor with the following snippet:  
    ```python
    from orodruin_maya.ui.editor_window import OrodruinMayaWindow
    OrodruinMayaWindow.open()
    ```
