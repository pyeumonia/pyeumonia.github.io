# Initialize pyeumonia

## How to initialize pyeumonia

### Disable pyeumonia check update

```python
from pyeumonia import Covid19
covid = Covid19(check_upgradable=False)
```

### Set the language

- Set language from your system language
```python
from pyeumonia import Covid19
covid = Covid19(language='auto')
```

- Set language to Chinese
```python
from pyeumonia import Covid19
covid = Covid19(language='zh_CN')
```

- Set language to English
```python
from pyeumonia import Covid19
covid = Covid19(language='en_US')
```
