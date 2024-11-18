# AgroNW-Py-GUI

Prototype Agro-NW client/server.

Developed by Partha Pratim Kalita, while working as an assistant at the DFKI Niedersachsen in Osnabrück.

The Agro-Nordwest project was funded by the Federal Ministry of Food and Agriculture (BMEL) Agriculture (BMEL) on the basis of a resolution of the German Bundestag via the Federal Agency for Agriculture and Food (BLE) within the framework of the innovation support program.

Many thanks to our colleagues from the UOS and the HSOS for their contribution.

## List of features
- Forward-chaining inference from input data, using logical rules
- Weather forecast retrieval through the wetterdienst API
- Results presented in simple text and a map
- Result explanation in plots
- Simple interface to edit and create new fields (with room for improvement)

## Requirements
The AgroNW DSS is built on the SEMPR inference engine, which depends on a number of system libraries that are no longer maintained or no longer available. We recommend running this project using **Ubuntu 20.04**.

Given the nature of this prototype, some knowlege of the Linux terminal and package management is expected.

## How to run
- Obtain and install "Rete", "Pegmatite" and "SEMPR" (most should be available within the [SEMPR Toolkit](https://github.com/sempr-tk))
- Obtain and set up (compile, install) the Python bindings for SEMPR
- Install python and core, related libraries (e.g., pip)
- Install all the depedencies listed in the file "requirements.txt".
    - e.g., `pip install -r requirements.txt`
- To run the server: `python3 server.py`
- To run the client: `python3 client.py`
