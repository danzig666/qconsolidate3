## QConsolidate3

QConsolidate3 is a fork of [OQ-Consolidate](https://github.com/gem/oq-consolidate), which is a modified version of [QConsolidate](https://github.com/alexbruy/qconsolidate), that:

- converts vector layers to GeoPackage or SHP (raster layers are copied as is)
- updated layer enumeration to use layer id (previously was parsing layer names, which can have duplicates in QGIS)
- saves every layer with a unique filename
- converts every dataset to UTF-8
- creates a project if it does not exist yet
- allows to give a customized (validated) name to the consolidated project
- allows to store all the project files in a zip file
WARNING: saving to GeoPackage deletes existing FID fields! (this is a workaroung for a bug in QGIS3)
