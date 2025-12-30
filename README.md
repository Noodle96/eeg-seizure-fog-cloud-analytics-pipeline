# eeg-seizure-fog-cloud-analytics-pipeline
![arquitectura](docs/screenshots/arquitectura.png)
Terminal 1
python run_room.py --room room_A
Lee room_assignments.yaml
Ve que Room A tiene P01 y P02
Procesa P01 -> luego P02


Terminal 2
python run_room.py --room room_B
Lee room_assignments.yaml
Ve que Room B tiene P03 y P04
Procesa P03 -> luego P04


Desde la raiz
python -m fog.room_simulators.run_room --room room_B    

