# Get data from the world

## Get the data from pyeumonia api

### Get the latest data from the world:

<!-- tabs:start -->

<!-- tab:command -->

- Get the latest data in English and save to `data.json`

```python
from pyeumonia import Covid19
import json
covid = Covid19(language='en_US')
data = covid.world_covid_data()
json.dump(data, open('data.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
```

<!-- tab:result -->

- Json file `data.json`:

This data has been got in `2022`-`07`-`14`, it's not the latest data, if you want to get the latest data, please get the data manually.

```json
[
  {
    "currentConfirmedCount": 32091590,
    "confirmedCount": 32609987,
    "curedCount": 368023,
    "deadCount": 150374,
    "continents": "Europe",
    "countryName": "France"
  },
  {
    "currentConfirmedCount": 24837561,
    "confirmedCount": 29308100,
    "curedCount": 4328400,
    "deadCount": 142139,
    "continents": "Europe",
    "countryName": "Germany"
  },
  "Some country are hidden",
  {
    "currentConfirmedCount": 2,
    "confirmedCount": 29,
    "curedCount": 27,
    "deadCount": 0,
    "continents": "Europe",
    "countryName": "Holy See"
  },
  {
    "currentConfirmedCount": 0,
    "confirmedCount": 515645,
    "curedCount": 490920,
    "deadCount": 24725,
    "continents": "Africa",
    "countryName": "Egypt"
  },
  {
    "currentConfirmedCount": 0,
    "confirmedCount": 34658,
    "curedCount": 34630,
    "deadCount": 28,
    "continents": "Europe",
    "countryName": "Faroe Islands"
  },
  {
    "currentConfirmedCount": 0,
    "confirmedCount": 11971,
    "curedCount": 11950,
    "deadCount": 21,
    "continents": "North America",
    "countryName": "Greenland"
  }
]
```

<!-- tabs:end -->

### Get timeline data from your country:

<!-- tabs:start -->

<!-- tab:command -->

- Get the latest data in past 3 days from your country in English and save to `data.json`

```python
from pyeumonia import Covid19
import json
covid = Covid19(language='en_US')
# Get covid-19 data from your country in the last 30 days
data = covid.country_covid_data(country='auto', show_timeline=3)
json.dump(data, open('data.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
```

> **Warning**:
>
> - If you are using a proxy, you need to turn off the proxy in your device, or the result will be wrong.

<!-- tab:result -->

- Json file `data.json`:

This data has been got in `2022`-`07`-`14`, it's not the latest data, if you want to get the latest data, please get the data manually.

```json
{
  "countryName": "China",
  "data": [
    {
      "dateId": 20220711,
      "confirmedCount": 4670968,
      "curedCount": 299417,
      "deadCount": 22367,
      "currentConfirmedCount": 4349184
    },
    {
      "dateId": 20220712,
      "confirmedCount": 4702869,
      "curedCount": 299611,
      "deadCount": 22429,
      "currentConfirmedCount": 4380829
    },
    {
      "dateId": 20220713,
      "confirmedCount": 4733481,
      "curedCount": 299812,
      "deadCount": 22481,
      "currentConfirmedCount": 4411188
    },
    {
      "currentConfirmedCount": 4438739,
      "confirmedCount": 4761120,
      "curedCount": 299812,
      "deadCount": 22569,
      "dateId": 20220714
    }
  ]
}
```

<!-- tabs:end -->
