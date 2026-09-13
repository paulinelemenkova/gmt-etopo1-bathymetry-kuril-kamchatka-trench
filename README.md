# GMT Shaded-Relief Bathymetry of the Kuril-Kamchatka Trench from ETOPO1

GMT shell script producing a shaded-relief bathymetric map of the Kuril-Kamchatka Trench, north-west Pacific Ocean, from the ETOPO1 1-arc-minute global relief grid (region 140-170 E, 40-60 N), with contours, colour scale and map decorations.

## Associated publication

Lemenkova, P. (2019). Topographic surface modelling using raster grid datasets by GMT: example of the Kuril-Kamchatka Trench, Pacific Ocean. *Reports on Geodesy and Geoinformatics*, 108, 9-22. ISSN 2391-8365.

Indexed in Web of Science.

## Links

- Published paper (DOI): https://doi.org/10.2478/rgg-2019-0008
- Publisher (Sciendo): https://content.sciendo.com/view/journals/rgg/108/1/article-p9.xml
- Archived (Zenodo): https://zenodo.org/record/3530305
- Preprint (HAL): https://hal.science/hal-02351014
- Preprint (SSRN): https://ssrn.com/abstract=3481656
- LifeScience.net: https://www.lifescience.net/publications/17720/topographic-surface-modelling-using-raster-grid-da/
- Author ORCID: https://orcid.org/0000-0002-5759-1089

## Script

- `GMT-01-script-grid-JM-ETOPO1-KKT.sh`

## Output figures

- `BathymetryKKT-1grid.jpg`
- `BathymetryKKT.jpg`

## Data

The script reads the ETOPO1 1-arc-minute global relief grid (`earth_relief_01m`). The global grid is not bundled; GMT can download it automatically in modern mode (`@earth_relief_01m`) or you can supply your own copy.

## Requirements

GMT (Generic Mapping Tools) 6, and GDAL (`gdalinfo`).

## Author

Polina Lemenkova — ORCID: https://orcid.org/0000-0002-5759-1089

## License

MIT — see the LICENSE file (Copyright Polina Lemenkova).
