# Vermont Fire Resource Area Coverage and Response Times (FRACTR) Project

### Abstract

This project provides a visual analysis of fire department resources and response time coverage across the state of Vermont, in order to support regional emergency planning. To achieve this, we created a web-based application that displays interactive, multi-layered maps. The first map consists of a network analysis of estimated fire department response times across the state of Vermont. The second map is the same as the first, however, the response times from every fire station are bounded by the fire department's emergency service zone. The third map highlights areas that are in close proximity to fire hydrants, which can be used to extinguish fires. These maps are used to assess speed and efficiency of response to 911 calls, and emergency planning commissions across the state can utilize these maps and their creation methods to assess optimal locations for the construction of new fire stations and hydrants.

### Response Times from Stations & Fire Hydrant Locations

We have generated a number of geoJson files which are displayed on the interactive maps on the [FRACTR website](https://smokenmaps.com). These geoJson files are available in the [data folder](https://github.com/This-blank-Is-On-Fire/Website/tree/master/data) of the [Website repository](https://github.com/This-blank-Is-On-Fire/Website).

### Workflow & Data Output

This repository contains all python files that perform the network analysis necessary to output the response time polygon geojson files
displayed on the [smokenmaps.com](https://smokenmaps.com) website. Every python file contains an introductory blurb describing its purpose as well as input and output files.
Currently, a GitHub Actions workflow has been set up to pull the latest data from the Vermont Open Geodata Portal, perform the network analysis, and push the generated data files directly into the `data` directory of the [Website repository](https://github.com/This-blank-Is-On-Fire/Website).  The workflow is scheduled to run once a week, however since GitHub Actions is [a little bit finnicky](https://upptime.js.org/blog/2021/01/22/github-actions-schedule-not-working/), we cannot assure that this will be the case. That being said, because fire stations do not change location nor are built very often, we do not expect this to be much of an issue, and new data is recomputed on every push event.

Please use the [GitHub Issues tab](https://github.com/This-blank-Is-On-Fire/FRACTR/issues) to submit any bugs you find or ask questions you may have.

### Ethical Implications of Our Work
 
These maps offer rough estimates of response times and should not be interpreted as exact (see the Limitations section).
A concern of ours is that future homeowners and insurance companies may seek to use our maps as a tool to discriminate between properties located near and far away from fire stations. Consequently, future homeowners may be less likely to purchase homes located outside of certain response time zones, and insurance companies could choose to raise insurance costs for homes in 
these areas. We recognize these possibilities and remind our users that these maps offer estimates and should be used for public governance, citizen awareness, and emergency planning. Our hope is that regional planning commissions and state emergency planners can use these maps to inform their work and increase coverage across the state.

If you have any issues with these maps, please reach out to us at [jcambefort@middlebury.edu](mailto:jcambefort@middlebury.edu) and [halcyonb@middlebury.edu](mailto:halcyonb@middlebury.edu), as we would be happy to hear your thoughts.

### Limitations of the Maps & Data
 - These maps offer rough estimates of response times and should not be interpreted as exact, reliable fact (the road network and speed data are fetched from openstreetmap.org).
 - Fire station response protocols vary and may impact response times.
 - Differences in fire station resources are not taken into account.
 - Any stations missing on the map were either missing in the original dataset, or misleadingly labeled (e.g., labeled strictly as a law enforcement station).
 - To compute a station's response polygons, a mapping is created between the fire station coordinates and the nearest node on the Open Street Maps network graph.
However, occasionally, the nearest node on the graph may be a few hundred feet away from the station and thus the polygon produced is slightly off-centered.
 - For a full list of the project limitations, please see the final report PDF linked on the [project website's homepage](smokenmaps.com).

### Acknowledgments

Thank you to Middlebury Fire Department Chief David Shaw and Andrew L'Roe at the Addison County Regional Planning Commission for their input on local datasets and the Vermont fire service, and for troubleshooting our website. Thank you very much to Bill Hegman, Prof. Holler, Prof. Kimambo, and Kufre Udoh from the Middlebury College Geography Department for their insights into network analysis and working with raster and vector data. Thank you to Prof. Vaccari for overseeing the Computer Science Senior Seminar course and guiding us through this process.

### Project Report

Please see our website for the link to our full project report and summarizing poster. 

### Tool References

Bellock, K., 2019. Alpha Shape Toolbox. Alpha Shape. URL https://alphashape.readthedocs.io/en/latest/index.html (accessed 5.11.21).

Boeing, G. 2017. "OSMnx: New Methods for Acquiring, Constructing, Analyzing, and Visualizing Complex Street Networks." Computers, Environment and Urban Systems 65, 126-139. https://doi.org/10.1016/j.compenvurbsys.2017.05.004

Build fast, responsive sites with Bootstrap, n.d. Bootstrap. URL https://getbootstrap.com/ (accessed 5.11.21).

Jordahl, K., 2014. GeoPandas: Python tools for geographic data. URL: https://github.com/geopandas/geopandas.

VT Open Geodata Portal, 2021. Vermont Official State Website. URL https://geodata.vermont.gov/ (accessed 5.11.21).
