# Setup
```
python setup.py clean --all bdist_wheel
```

## (Re)Install **common** package
```
pip uninstall common -y
pip install ..\common\dist\common-1.0-py3-none-any.whl
```
