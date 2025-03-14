# Mecha-01-Romi-Term-Project

## Overview
Throughout this term, every lab and homework assignment has contributed to the development of our final project: assembling and programming a Pololu Romi robot. Our goal was to enable Romi to follow a line and autonomously navigate a predetermined course as quickly and efficiently as possible. This required integrating various sensors, implementing cascaded chassis and motor control, and designing a navigation algorithm for path planning and obstacle avoidance. To achieve this, we applied concepts from dynamics, control theory, embedded systems, and priority scheduling in task-oriented programming to ensure Romi could complete the challenge successfully.

## Hardware Components
We were supplied with a Romi chassis kit, a differential-drive platform with a 6.5-inch diameter and an integrated battery holder for six AA batteries. The two drive wheels, located on the outer edges of the chassis, use 70 mm Pololu wheels connected to Mini Plastic Gearmotors with quadrature encoders for position feedback. Two fixed ball casters at the front and rear provide additional stability. The chassis includes a motor driver and power distribution board that powers the motor encoders and our microcontroller.

Our microcontroller was a Nucleo board featuring an STM32 MCU with 76 pins available for powering and communicating with sensors. We used Python and the MicroPython library to program Romi, process sensor data, control the motors, and determine the robot’s path. Additionally, we incorporated a BNO055 Inertial Measurement Unit (IMU) to track orientation using an accelerometer, magnetometer, and gyroscope. Since Romi operates on a flat track, we were primarily concerned with its heading (rotation about the z-axis).

Beyond the supplied components, we purchased a Bluetooth module and infrared reflection line sensors to detect the black lines on the white track. Bump sensors were also integrated to detect collisions with walls or obstacles.

## Software Architecture
The majority of our work focused on designing, implementing, debugging, and fine-tuning the code that allowed Romi to navigate the maze quickly and reliably. Our code is structured into three levels of abstraction:

1. **High Level:** This includes the main file, `cotask`, and `taskshare`. The main file runs the scheduler, determining which task executes next. `Cotask` implements the scheduler, defining priority and frequency for each task. `Taskshare` provides shared data structures, including shares and queues, to facilitate communication between tasks.
2. **Middle Level:** This consists of tasks that divide the robot's functionality into manageable sections. Our project runs five concurrent tasks: `nav`, `user`, `sensor`, `motor`, and `controller`. Each task operates as a finite state machine, transitioning between states based on flags and shared variables.
3. **Low Level:** This consists of classes for individual components such as sensors, motors, and the grid representation of the track. These classes include methods for initializing attributes and modifying states to facilitate Romi’s movement and control.

## Task Descriptions
### Navigation Task
The `nav` task is responsible for determining Romi’s path through the maze. It continuously updates the robot's desired heading based on its current position, the next target point, and the drive mode. The task ensures Romi follows the correct path using feedback from the IMU, encoders, and line sensors. It transitions between states such as line following, pivoting, and straight-line driving based on the current mode and environmental conditions.

### User Task
The `user` task handles user inputs and settings. It processes commands sent via Bluetooth and allows users to start, stop, and calibrate the robot. Additionally, it updates the base motor effort (`V`) and mode selection (`Run` flag) based on user input. This task ensures that Romi can be easily controlled and adjusted during testing and operation.

### Sensor Task
The `sensor` task collects and processes data from all onboard sensors, including the line sensor array, IMU, encoders, and bump sensors. It updates shared variables such as `Centroid` (line position), `e` (error value for heading control), and `Psat` (mean sensor reading). By continuously monitoring sensor inputs, this task enables Romi to adjust its movements dynamically and react to environmental changes.

### Motor Task
The `motor` task directly controls the speed and direction of Romi’s motors. It sets motor efforts (`L_eff` and `R_eff`) based on feedback from the navigation and controller tasks. This task ensures smooth movement transitions and maintains stability while following the line or executing pivots. It also prevents erratic behavior by enforcing effort limits and handling emergency stops.

### Controller Task
The `controller` task implements closed-loop control algorithms for both heading and speed adjustments. It calculates correction values based on the error (`e`) and updates the motor efforts accordingly. For line-following, it adjusts motor speeds to keep Romi centered on the track, while in pivot mode, it ensures accurate turns based on IMU data. The controller task is essential for maintaining precision and efficiency in Romi’s movements.

## Shared Variables
To facilitate inter-task communication, we implemented ten shared variables:
- `calibrateb`, `calibratew`: Flags to trigger line sensor calibration for black and white backgrounds.
- `V`: Base effort input by the user.
- `L_eff`, `R_eff`: Motor efforts set based on sensor feedback.
- `Centroid`: Current center of the line reading (range: 1 to 13).
- `e`: Error value used for heading and straight-line control.
- `Psat`: Mean sensor reading from the line sensor array.
- `Run`: Flag determining whether Romi is active or idle.
- `Mode`: Determines the current drive mode (1 = line following, 2 = pivot, 3 = straight-line driving).

## Conclusion
The Mecha-01 Romi Term Project was a culmination of multiple engineering principles and hands-on development. By systematically designing the software and hardware, implementing robust control strategies, and fine-tuning our approach, we successfully created an autonomous Romi capable of navigating the maze efficiently. This project not only reinforced our understanding of embedded systems and robotics but also provided valuable experience in integrating sensors, real-time task scheduling, and control algorithms.

