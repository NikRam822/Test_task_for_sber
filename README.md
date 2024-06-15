# Test_task_for_sber
Test task for SBER for the vacancy of it-auditor

## Sberbank procurement analysis
This project is designed to analyze the procurement of Sberbank subsidiaries. It collects data on Sberbank's subsidiaries from Wikipedia, obtains information on their purchases from zakupki.gov.ru, builds a graph of relationships between companies and their purchases, and performs clustering of companies based on their procurement statistics.

## Requirements
 - Python 3.6 or higher
 - Installed dependencies from the requirements.txt file
 - 
## Installation with venv (recommended)
1. Clone this repository.
2. Navigate to the project directory.
3. Run the command to create a virtual environment in the project directory:
```
python -m venv venv
```
4. Activate the created virtual environment:

- On Windows:
```
venv\Scripts\activate
```

- On macOS and Linux:
```
source venv/bin/activate
```
5. Install dependencies from the requirements.txt file:
```
pip install -r requirements.txt
```
## Installation without venv
1. Clone this repository.
2. Navigate to the project directory.
3. Install dependencies from the requirements.txt file:
```
pip install -r requirements.txt
```
## Startup
Run the following command to start the project:
```
python main.py
```

This will start data collection, graph building and clustering of companies. Upon completion of the script, the results will be displayed in the console, and a graphical window with visualization of the graph and clusters will be opened.

## Startup with Docker

1. Build the Docker image by running the following command in the root directory of the project:
```
docker build -t sber-procurement-analysis .
```
2. Start the Docker container with the built image:

 - For Linux:
```
docker run --env="DISPLAY" --env="QT_X11_NO_MITSHM=1" --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" sber-procurement-analysis
```
 - For Windows (using VcXsrv or Xming):
```
docker run --env="DISPLAY=host.docker.internal:0.0" sber-procurement-analysis

```

If you want to run the application without visualizing the graphics, use:
```
docker run sber-procurement-analysis
```

## Documents

A detailed description of the solution in Russian can be found at: https://nikram822.github.io/Test_task_for_sber/#overview