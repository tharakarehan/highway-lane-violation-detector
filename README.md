# highway-lane-violation-detector

<div align="justify">This is a desktop app for detecting highway lane violations. Illegal parking, Wrong direction, Illegal over taking can be detected. This can be implemented realtime on CPU thanks <a href="https://docs.openvino.ai/latest/index.html" target="_blank">OpenVino</a> model optimisation. To track objects (vehicles), SORT algorithm with Kalmann Filter (tracker) and Hungarian algorithm (data association) has been used. Pre-trained openvino vehicle detection model (MobileNetV2 SSD) has been used for detection. Tkinter library is used for GUI </div>


<p align="center">
  <img src="https://github.com/tharakarehan/highway-lane-violation-detector/blob/main/sample.gif">
</p>

## Installation

Create a new conda environment. If you dont have conda installed download [miniconda](https://docs.conda.io/en/latest/miniconda.html)

```bash
conda create -n hwlvd python=3.8 
```
Clone this repository to your computer and navigate to the directory.

Activate new enviroment
```bash
conda activate hwlvd  
```
Install all the libraries used
```bash
pip install -r requirements.txt  
```

Then run the model

```bash
python run_sort.py 
```

## Usage

<p align="center">
  <img wide=720 height=550 src="https://github.com/tharakarehan/highway-lane-violation-detector/blob/main/ss-min.png">
</p>

#### ① - Input Directory Button
<div align="justify">Select input video for monitoring.</div>

#### ② - Output Directory Button
<div align="justify">Select a directory for saving the output if necessary.</div>

#### ③ - Detection Threshold
<div align="justify">Insert the threshold value for detection model. </div>

#### ④ - Duration
<div align="justify">Insert the duration which is the limit that the program will allow a vehicle not be considered as parked. </div>

#### ⑤ - Standard Deviation
<div align="justify">Used for stabilizing the park detection. </div>

#### ⑥ - Direction
<div align="justify">Direction the vehicles are supposed to go legally.. </div>

#### ⑦ - Save Video Tick
<div align="justify">Whether to save the video or not. </div>

#### ⑧ - Load
<div align="justify">Load the model and other information (a window will pop out to manually draw the boundaries for lanes). </div>

#### ⑨ - Play
<div align="justify">Play the video. </div>

#### ⑩ - Stop
<div align="justify">Stop the video. </div>

#### ⑪ - Quit
<div align="justify">Quit the program. </div>

#### ⑫ - Illegal Parking Count
<div align="justify">Number of vehicles that are detected as illegally parked at the moment. </div>

#### ⑬ - Improper Lane Usage Count
<div align="justify">Number of vehicles that are detected as violated the lane discipline at the moment. </div>

#### ⑭ - Reverse Count
<div align="justify">Number of vehicles that are detected as driving at the wrong direction at the moment. </div>

#### ⑮ - Latency
<div align="justify">The amount of time(ms) that has been spent on processing one frame. </div>

## License
[MIT](https://choosealicense.com/licenses/mit/)
