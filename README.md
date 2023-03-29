# Home Assistant RDTech UM series USB load meter integration

Home Assistant integration to control RDTech UM series USB load meters over
bluetooth.

## Hardware

The RDTech UM24C, UM25C and UM34C are USB load meters which can measure
various properties for USB devices including their voltage, amperage, wattage,
resistance, capacity, temperature, data line voltage, and charging mode.

## Installation

### HACS
- Go to your **HACS** view in Home Assistant and then to **Integrations**
- Open the **Custom repositories** menu
- Add this repository URL to the **Custom repositories** and select
**Integration** as the **Category**
- Click **Add**
- Close the **Custom repositories** menu
- Select **+ Explore & download repositories** and search for *RDTech UM series*
- Select **Download**
- Restart Home Assistant

### Manually
- Copy the `custom_components/rdtechum` directory of this repository into the
`config/custom_components/` directory of your Home Assistant installation
- Restart Home Assistant

##  Adding a new RDTech UM series USB load meter
New RDTech UM series devices will automatically be detected after the
integration has been installed.

## Credits
Special thanks go to William Vallet for creating the
[Python UM meter library](https://github.com/valletw/pyummeter) which this
integration heavily relies on.

Do you enjoy using this Home Assistant integration? Then consider supporting
my work:\
[<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >](https://www.buymeacoffee.com/rrooggiieerr)  