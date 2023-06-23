# Developer README

## Distribution Steps

1. Install `twine'
   - `pip install twine`
2. Make sure you have accounts with both PyPI and Test PyPI
3. Generate distribution archives
   - `python3 setup.py sdist bdist_wheel`
4. Upload to Test PyPI to test if the distribution works
   - `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
   - Then, check if your package was uploaded successfully by visiting Test PyPI and searching for your package
5. Upload to PyPI
    - `twine upload dist/*`
