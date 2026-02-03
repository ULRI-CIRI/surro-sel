# SurroSel
## Publication
In progress.

### Abstract
Quantitative non-targeted analysis (qNTA) is an emerging field providing high-throughput detection and quantitation of contaminants in the environmental, biological, and consumer chemical milieu. The statistical accuracy, reliability, and precision of qNTA models depend on the selection of informative “surrogates,” which are chemical species selected to calibrate downstream modeling to the quantitative response of the experimental set-up. In a recently published work, our group described a theoretical and mathematical basis for surrogate selection and demonstrated its ability to improve the performance outcomes of models that make selections based on those insights. Here, we present SurroSel, a lightweight dashboard-style application providing a user interface for those methods to retrospectively assess and prospectively select sets of chemical surrogates. SurroSel is published open-source as a flexible and accessible solution that can be easily deployed by laboratories seeking to incorporate a rational, reproducible basis for their surrogate choices in qNTA workflows.

## Project Structure
### utils/
The ```utils/``` directory contains reusable calculation modules for ionization efficiency descriptor computation and surrogate selection algorithm implementation. These are intentionally well-modularized from the app structure and may be used as standalone modules or code snippets for scripting or further computational tool development.

### components/
The ```components/``` directory contains the structure of the application, written in Shiny for Python. The ```requirements.txt``` file lists package dependencies with versions.

The main app file is ```app.py```.

## Running the App
The Shiny app can be initialized from the command line using the command ```shiny run surro_sel.app```. There are no required environment variables or dependencies beyond the packages listed in ```requirements.txt```. Further information on command line arguments to run a Shiny app can be found in the [Shiny for Python tutorials](https://shiny.posit.co/py/get-started/create-run.html), [API reference](https://shiny.posit.co/py/api/core/run_app.html), or using the command ```shiny run --help```.

## Correspondence
Please contact gabriel@dashdashdot.org (@mrmsds) for deployment assistance, questions, or issues.
