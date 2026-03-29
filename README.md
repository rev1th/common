# Setup
```
python setup.py clean --all
python -m build --wheel
```

## (Re)Install **common** package
```
pip install --force-reinstall --no-deps git+https://github.com/rev1th/common.git@main#egg=lib_common
```
