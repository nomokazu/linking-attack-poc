# Artifact

This repository is an artifact of "On the Feasibility of Linking Attack to Google/Apple Exposure Notification Framework
(Kazuki Nomoto, Mitsuaki Akiyama, Masashi Eto, Atsuo Inomata, and Tatsuya Mori)" in PoPETS 2022 (to appear).

I will place a link to the paper here when it is publicly available.

This repository includes the code of a PoC implementation for conducting a Linking Attack against GAEN and a simulation program to evaluate the attack success rate.

This artifact provides a proof-of-concept implementation to demonstrate a linking attack against GAEN and a simulation to evaluate the attack success rate of a linking attack.　The attack implementation allows a third party to evaluate the feasibility of a linking attack.　Several pieces of hardware are required to run this attack PoC implementation.　Specifically, an Ubertooth One, two USB-connected webcams, and an antenna that can be connected to the Ubertooth One.

In addition, the simulation allows a third party to evaluate the attack success rate of the linking attack.
By publishing the simulation programs used in the paper, we help third parties carefully check our implementation.

We hope that these the code of a PoC implementations will be used by third parties to enhance the security of GAEN and other BLE applications.

# Attack

This is the code of a PoC implementation for Linking Attack against GAEN.

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
    - matplotlib==3.5.1
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

To avoid conflicts with existing Python environments, it is recommended to use a virtual environment using venv.
You can install all libraries by executing the following command.

(Mac/Linux user)
```
python3 -m venv venv
. ./venv/bin/activate
pip3 install -r ./attack/requirements.txt
```

(Windows user)
```
python3 -m venv venv
.\venv\Scripts\activate
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

- Experiment Number : The experiment number is used to distinguish the results of each experiment. You must enter an experiment number that does not duplicate a number already in the experiment. The experiment number must be 0 or positive integer.
- Run Time : The length of time for which the attacking program is executed. For example, if you specify 30, the camera captures images and Ubertooth receives BLE for 30 seconds.
- Camera Number Side : The device ID assigned by OpenCV to the camera installed on the antenna side. (In most cases, it is one of 1, 2, or 3.)
- Camera Number Front : The device ID assigned by OpenCV to the camera installed on the front side. (In most cases, it is one of 1, 2, or 3.)

#### Terminal B

Start capturing BLE by executing the following command

```
ubertooth-btle -n -q [experiment number].pcap
```

#### After execution

When execution is finished, BLE receiving in Terminal B must be stopped.  
Please use "Ctrl+C" to stop BLE receiving in Terminal B.  
After exiting with "Ctrl+C" in Terminal B, type y as instructed by Terminal A.  

### Draw graph

Draw a graph by executing the following command.  
A graph is displayed. Click on the graph to see the image at the matching time.


```
python3 drawGraph.py
```

The following is a description of each parameter that is required to be entered after program execution.

- Experiment Number : Enter the experiment number for which the graph is to be plotted. You must enter the experiment number that matches the experiment number entered in the Capture Phase. This means that if you specified the experiment number = 0 in mainAll.py, you must specify the experiment number = 0 here as well.

## Data Saving

The data recorded by this PoC implementation is stored in the "data" and "result" folders for each experiment number.

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
    - matplotlib==3.5.1
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
7 : Road widths
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

If you just want to make sure the program works, I suggest you choose the experimental type 6.

In the second and subsequent runs, please be sure to delete the directories corresponding to the respective experiment numbers before running the experiment.

Running a simulation with 10,000 pedestrians per hour is excluded from the default settings because it would take an enormous amount of time to run the simulation. If you want to set it to 10,000, you can try the simulation by adding it to the "perTimeList" list. 

#### Flag in main()
- graphFlag : Do you want to draw a graph? If graphFlag = 1, then graph data showing the relationship between time and signal strength is stored.
- modelFlag : Do you output 3D modeling? If modelFlag = 1, then the image of the 3D model at the time when the signal strength corresponding to each RPI reached its maximum is stored.
- mixFlag : Do you want to simulate a mix of smartphones with different signal strengths? If mixFlag = 1, then the simulation is run under the condition of a mix of smartphones with two different signal strengths.

Note that if graphFlag or ModelFlag is set to 1, the simulation is performed using only the first parameter.

#### Parameters in prepareXXXX()
You can try simulations under various conditions by changing the following parameters.

- perTimeList : The number of pedestrians per hour is stored. For example, if a value of 1200 is specified, a simulation of 1200 pedestrians per hour walking in front of the attacking device is run.
- rpiSendFrequencyList : The signal transmission frequency of the RPI is stored. For example, if a value of 0.270 is specified, each smartphone advertises an RPI on BLE every 0.270 seconds.
- widthOfRoad : Width of the street where pedestrians walk. For example, if the value is 3, the pedestrian walks on a 3 m wide street.
- receiverSettings : Receiver settings such as receiver location and antenna angle are stored.

### Parse Result

Experiment results are stored in a directory corresponding to the number of each experiment type.

We provide a parser of the experimental results.
You can parse the results and review the results by executing the following command and selecting the type of experiment.

```
python3 resultParser.py
```

### Draw graph

You can draw a graph of the relationship between time and signal strength calculated within the simulation after running the simulation with graphFlag = 1.
You can draw the graph by executing the following command and specifying the experiment number and target ID.

```
python3 graphViewer.py
```

# Contact

If you have any questions or operational problems, feel free to contact Nomoto Kazuki at the e-mail address given in the paper.

# How to test our code
PoC implementation of Attack requires hardwares. If you want to test the code at a minimum, an Ubertooth One, a common monopolar antenna and a webcam are all you need to test. If you have a computer with an Ubertooth One environment, you can easily build a PoC environment by simply installing the Python libraries listed in "./attack/requirements.txt". Note that Ubertooth One is sensitive to USB communication and may not work well in a virtual environment.

For testing PoC implementation of Simulation, you only need to install the Python libraries listed in "./simulation/requirements.txt", and you can easily build the environment without any other dependencies. If you just want to make sure the program works, I suggest you choose the experimental type six.