# NPS Parks — Home Assistant Integration

Track your visits to US National Parks and NPS sites directly in Home Assistant.

This integration connects to the [National Park Service API](https://www.nps.gov/subjects/developer/api-documentation.htm) and creates a sensor entity for every NPS site, letting you mark parks as visited, filter by designation, and build automations and dashboards around your park visits.

---

## Features

- **One sensor per NPS site** — 470+ parks, monuments, historic sites, and more
- **Visited/unvisited state** — mark parks via a searchable dropdown on the device card, or via service calls in automations
- **Persistent storage** — visited state survives restarts and option changes
- **Designation filtering** — show only National Parks, Monuments, Battlefields, etc.
- **Rich attributes** — latitude, longitude, description, designation, state(s), URL, and park image
- **Aggregate sensors** — total parks, visited count, parks remaining, and percentage visited
- **Configurable update interval** — hourly to monthly (park data rarely changes)
- **Manual refresh button** — force a data pull at any time

---

## Prerequisites

- Home Assistant 2025.1 or later
- A free [NPS API key](https://www.nps.gov/subjects/developer/get-started.htm) (instant, no approval needed)

---

## Installation

### HACS (recommended)

1. In Home Assistant, go to **HACS → Custom repositories**
2. Paste your GitHub repo URL and set category to **Integration**, then click **Add**
3. Search for **NPS Parks** in HACS and install it
4. Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration** and search for **NPS Parks**

### Manual

1. Download or clone this repository
2. Copy the `custom_components/nps_parks` folder into your HA config directory:
   ```
   <config>/custom_components/nps_parks/
   ```
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → Add Integration** and search for **NPS Parks**

---

## Custom Lovelace Card

A companion Lovelace card is in development that will display your visited and unvisited parks on an interactive map. Once released it will be available as a separate HACS repository.

---

## Configuration

On first setup you will be prompted for your **NPS API key**. The integration will validate the key before saving.

### Options

After setup, click **Configure** on the integration card to adjust:

| Option | Description | Default |
|---|---|---|
| Update Frequency | How often to refresh park data | Weekly |
| Park Designations | Filter which site types to track (empty = all) | All |

Available designations include National Park, National Monument, National Historic Site, National Battlefield, National Memorial, National Seashore, National Parkway, National Preserve, National Lakeshore, National Trail, National River / Waterway, International, and Other.

---

## Marking Parks Visited

The easiest way to mark parks is directly from the device card:

1. Use the **Select Park** dropdown — start typing a park name to search (e.g. "Rocky Moun...") and select it from the filtered list
2. Press **Mark Selected Visited** or **Mark Selected Unvisited**

You can also mark parks via service calls, which is useful for automations:

### `nps_parks.mark_visited`

```yaml
service: nps_parks.mark_visited
data:
  park_code: yose
```

### `nps_parks.mark_unvisited`

```yaml
service: nps_parks.mark_unvisited
data:
  park_code: yose
```

**Finding park codes:** Typically the first two letters of the first and second word in the site name (e.g. `Capitol Reef National Park` → `care`). You can also look them up on the [NPS website](https://www.nps.gov/articles/000/historic-listing-of-nps-park-codes.htm).

---

## Entities

### Park Sensors

One sensor per NPS site. State is `visited` or `unvisited`.

**Attributes:**

| Attribute | Description |
|---|---|
| `latitude` | Park latitude |
| `longitude` | Park longitude |
| `description` | Short park description |
| `designation` | NPS designation (e.g. "National Park") |
| `states` | US state(s) the park is located in |
| `url` | Link to the park's NPS page |
| `image` | Dict with `url`, `credit`, `alt_text`, `caption` |

### Aggregate Sensors

| Entity | Description |
|---|---|
| NPS Parks Total Parks | Total number of tracked NPS sites |
| NPS Parks Parks Visited | Number of sites marked as visited |
| NPS Parks Parks Remaining | Number of sites not yet visited |
| NPS Parks Percentage Visited | Percentage of tracked sites visited |

### Controls

| Entity | Description |
|---|---|
| NPS Parks Select Park | Searchable dropdown to select a park by name |
| NPS Parks Mark Selected Visited | Mark the selected park as visited |
| NPS Parks Mark Selected Unvisited | Mark the selected park as unvisited |
| NPS Parks Refresh | Manually trigger a data refresh from the NPS API |

---

## Example Automation

Mark a park as visited based on your location (requires a GPS tracking integration such as the HA Companion App):

```yaml
automation:
  - alias: "Mark Yosemite visited on arrival"
    trigger:
      - platform: zone
        entity_id: person.your_name
        zone: zone.yosemite
        event: enter
    action:
      - service: nps_parks.mark_visited
        data:
          park_code: yose
```

> **Note:** This requires creating a Zone in HA (**Settings → Areas & Zones → Zones**) centered on the park, and replacing `person.your_name` with your actual person entity.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
