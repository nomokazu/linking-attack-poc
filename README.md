# Attack

This is a PoC for Linking Attack against GAEN.

"attack" folder contains all files.

## Requirement (Hardware)

The following hardware devices are required  
Please connect each device.

- Ubertooth One

https://greatscottgadgets.com/ubertoothone/

- Parabolic Antenna

https://www.amazon.com/dp/B005M8KU3W/

- Web Camera (two sets)

https://www.amazon.com/dp/B07YWDP7PD/

## Requirement (Software)
- Python3

- Python Library

You need to install the following Python libraries.

    - cycler==0.11.0
    - fonttools==4.33.3
    - jarowinkler==1.0.2
    - kiwisolver==1.4.2
    - Levenshtein==0.18.1
    - matplotlib==3.5.2
    - numpy==1.22.4
    - opencv-python==4.5.5.64
    - packaging==21.3
    - Pillow==9.1.1
    - pyparsing==3.0.9
    - python-dateutil==2.8.2
    - rapidfuzz==2.0.11
    - scapy==2.4.5
    - scipy==1.8.1
    - six==1.16.0

You can install all libraries by executing the following command.

```
pip3 install -r ./attack/requirements.txt
```

- Ubertooth One

Set up the Ubertooth software to allow BLE packet capture.

Official Documentation : https://ubertooth.readthedocs.io/en/latest/index.html

## How to use

Go to "attack" folder.

### Capture images and BLE

You open two terminal A and terminal B.

#### Terminal A

Start capturing the camera by executing the following command

```
python3 mainAll.py
```

The following is a description of each parameter that is required to be entered after program execution.

- Experiment Number : Experiment Number. You can decide freely.
- Run Time : Capture execution time.
- Camera Number Side : The ID assigned by OpenCV to the camera installed on the antenna side. (In most cases, it is one of 1, 2, or 3.)
- Camera Number Front : The ID assigned by OpenCV to the camera installed on the front side. (In most cases, it is one of 1, 2, or 3.)

#### Terminal B

Start capturing BLE by executing the following command

```
ubertooth-btle -n -q [experiment number].pcap
```

#### After execution

When execution is finished, BLE receiving in Terminal B must be stopped.  
Please use "Ctrl+C" to top BLE receiving in Terminal B.  
After exiting with "Ctrl+C", type y as instructed by Terminal A.  

### Draw graph

Draw a graph by executing the following command.  
A graph is displayed. Click on the graph to see the image at the matching time.


```
python3 drawGraph.py
```

The following is a description of each parameter that is required to be entered after program execution.

- Experiment Number : Experiment Number. Enter the experiment number entered in the Capture Phase.

## Data Saving

The data recorded by this PoC is stored in the "data" and "result" folders for each experiment number.

# Simulation

This is a simulation to evaluate the attack success rate of a linking attack against GAEN.

"simulation" folder contains all files.


## Requirement (Software)
- Python3

- Python Library

You need to install the following Python libraries.

    - cycler==0.11.0
    - fonttools==4.33.3
    - joblib==1.1.0
    - kiwisolver==1.4.2
    - matplotlib==3.5.2
    - numpy==1.22.4
    - opencv-python==4.5.5.64
    - packaging==21.3
    - Panda3D
    - pandas==1.4.2
    - Pillow==9.1.1
    - pyparsing==3.0.9
    - python-dateutil==2.8.2
    - pytz==2022.1
    - scipy==1.8.1
    - six==1.16.0

You can install all libraries by executing the following command.

```
pip3 install -r ./simulation/requirements.txt
```

- Panda3D

This simulation uses Panda3D, a 3D rendering & game engine, to render the images.  
Please install Panda3D based on the official documentation.

https://www.panda3d.org/

- Panda3D Official assets

The simulation uses the background model distributed by the official Panda3D.

In the "model" folder, download the assets by executing the following command.

```
# In the directory containing main.py
cd ./simulation/model/
git clone https://github.com/panda3d/panda3d
```

- Open data

The CSV data stored under "personpositioncoord" folder is the data of "Open Data on Human Flow in Otemachi, Marunouchi, and Yurakucho Area" and is distributed under the CCBY license.

URL : https://www.geospatial.jp/ckan/dataset/human-flow-marunouchi


## How to use

Go to "simulation" folder.


### Run a simulation

Running the simulation is very simple.  
Simply run the Python program with the command shown below to run the simulation.

```
python main.py
```

After the run, you can select the type of simulation.  
Please choose from the following options: 0, 1, 2, 3, 5, 6, and 7.

```
Please input experiment type.
0 : Number of pedestrians
1 : Number of attacking devices
2 : Signal transmission frequency
3 : Pedestrians walk in groups
5 : Use of Open Data
6 : Same conditions as Open Data
7 : Various road widths
experiment type :
```

Each experimental number corresponds to a section in the paper.
- 0 : Section 5.2
- 1 : Section 5.3
- 2 : Section 6.2
- 3 : None
- 5 : Section 5.4
- 6 : Section 5.4
- 7 : Appendix C

In addition, you can try simulations under various conditions by changing the following variables (flags).

In the second and subsequent runs, please be sure to delete the directories corresponding to the respective experiment numbers before running the experiment.

If you experiment with the parameters of the paper, it will take longer to run the simulation.
To test the running of the simulation, specify 1 for targetFlag in the main() function.

Running a simulation with 10,000 pedestrians per hour is excluded from the default settings because it would take an enormous amount of time to run the simulation.
If you want to set it to 10,000, you can try the simulation by adding it to the perTimeList list. 

```
targetFlag = 0
```

By doing so, the number of pedestrians per hour will be reduced and the simulation will be completed in a relatively short time.

#### Flag in main()
- graphFlag : Do you want to draw a graph?
- modelFlag :  Do you output 3D modeling?
- mixFlag : Mix signal strength of two different devices?
- directionFlag : Walking direction of pedestrians

#### Parameters in prepareXXXX()
- perTimeList : List of number of pedestrians per hour
- rpiSendFrequencyList : Transmission frequency of RPI
- widthOfRoad : Witdth of street
- receiverSettings : List of receivers
- reSend : Number of consecutive transmissions during intermittent transmission


### Parse Result

Experiment results are stored in a directory corresponding to the number of each experiment type.

We provide a parser of the experimental results.
You can parse the results and review the results by executing the following command and selecting the type of experiment.

```
python3 parseResult.py
```

### Draw graph

You can draw a graph of the relationship between time and signal strength calculated within the simulation after running the simulation with graphFlag = 1.
You can draw the graph by executing the following command and specifying the experiment number and target ID.

```
python3 graphViewer.py.py
```

# Contact

If you have any questions or operational problems, feel free to contact Nomoto Kazuki at the e-mail address given in the paper.
