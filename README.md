# AgroNW DSS GUI

Prototype AgroNW Decision-Support System (DSS), based on the inference engine SEMPR. This DSS provides recommendations for pasture harvesting and fertilization using expert knowledge in combination with field and weather data.

The DSS was designed and developed by members of the Plan-Based Robot Control Group of the DFKI Niedersachsen, in the context of the Agro-Nordwest experimental field. This repository contains the source code for the DSS GUI, developed by Partha Pratim Kalita while working as an assistant in AgroNW.

The Agro-Nordwest project was funded by the Federal Ministry of Food and Agriculture (BMEL) Agriculture (BMEL) on the basis of a resolution of the German Bundestag via the Federal Agency for Agriculture and Food (BLE) within the framework of the innovation support program.

Many thanks to our colleagues from the UOS and the HSOS for their contribution.

## Related publications:
- Reuter, T., Saborío Morales, J. C., Tieben, C., Nahrstedt, K., Kraatz, F., Meemken, H., et al. (2023). Evaluation of a decision support system for the recommendation of pasture harvest date and form. In Hoffmann, C., Stein, A., et al. 43. GIL-Jahrestagung (GIL-2023), Resiliente Agri-Food-Systeme. Pp. 489-494, ISBN 978-3-88579-724-1, Gesellschaft für Informatik e.V. Bonn, 2/2023.
- Tieben, C., Reuter, T., Nahrstedt, K., Kraatz, F., Lingemann, K., Trautz, D., ... & Hertzberg, J. (2022). Auf dem Weg zu einem Entscheidungsunterstützungs-system zur Pflege und Ernte von Grünlandflächen. In Gandorfer et al., Künstliche Intelligenz in der Agrar- und Ernährungswirtschaft, LNI, 2022, Vol. P-317, pp. 289–294.
- Niemann, N., Tieben, C., Lingemann, K., & Hertzberg, J. (2021). Wissensverarbeitung in der Landwirtschaft mit regelbasierten Inferenzsystemen und Begründungsverwaltung. In
Meyer-Aurich et al., Informations- und Kommunikationstechnologien in kritischen Zeiten, LNI, 2021, Vol. P-309, pp. 229–234.

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
- Install Python and core, related libraries (e.g., pip)
- Obtain and set up (compile, install) the Python bindings for SEMPR (also in the [SEMPR Toolkit](https://github.com/sempr-tk))
- Install all the depedencies listed in the file "requirements.txt".
    - e.g., `pip install -r requirements.txt`
- Install the wetterdienst API: `pip install wetterdienst`
- To run the server: `python3 server.py`
- To run the client: `python3 client.py`
