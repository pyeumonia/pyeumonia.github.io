# Install pyeumonia

## Install pyeumonia

### How to install

Pyeumonia is a free and cross-platform api, you can use it on Microsoft Windows、macOS、Linux and even on FreeBSD.

- Install pyeumonia
```bash
pip install pyeumonia
```

>**Warning**:
>- Pyeumonia is only supported for python3.7 and above, if you are using python 3.6 or an older version, you can't install pyeumonia.

### How to update

- Enable auto update pyeumonia
```python
from pyeumonia import Covid19
covid = Covid19(auto_update=True)
```
If you installed the new version automatically, CovidException will be raised, then you should restart the program.

- Disable check upgradable

```python
from pyeumonia import Covid19
covid = Covid19(check_upgradable=False)
```

- Update the pyeumonia manually

If you want to update pyeumonia manually, you can run `pip install -U pyeumonia` to update the pyeumonia.
```bash
pip install -U pyeumonia
```