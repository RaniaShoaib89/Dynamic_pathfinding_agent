# Smart Navigator Probe

An advanced, interactive route-planning visualization tool developed with Python and Pygame. This application showcases foundational pathfinding algorithms like the A-Star (A*) and Greedy Best-First Search, giving users the freedom to construct layouts, spawn random barriers, and observe firsthand how various computational methods determine the most efficient trajectory from an origin to a destination.

A standout capability is the **Real-time Adjust Mode** wherein a virtual probe traverses the calculated route. As it moves, random impediments can surface dynamically, compelling the probe to instantly recalculate and adapt its trajectory to reach the endpoint.

## 🌟 Key Highlights

- **Dynamic Grid Interface**: Intuitively map out boundaries, designate your starting point, and position your target using simple mouse actions.
- **Algorithm Comparison**: Directly contrast the operational behaviors of different pathfinding techniques (A-Star vs. Greedy Best-First).
- **Customizable Metrics**: Switch between Manhattan and Euclidean formulas for heuristic estimations.
- **Live Telemetry**: Monitor ongoing statistics including calculation time, total tiles explored, and the final route expense.
- **Adaptive Probe**: Observe an autonomous entity follow the generated path while reacting and replanning around spontaneously appearing obstacles.
- **Instant Layouts**: Populate the environment with a randomized distribution of barriers (30% density) at the push of a button.

## 🛠️ System Requirements

Ensure you have a recent version of Python installed on your machine.

Core packages required:
- `pygame`
- `pygame_gui`

## 🚀 Setup Instructions

1. **Obtain the Source Code**: Clone or download this repository to your local machine.
2. **Access Project Directory**: Open your terminal and change into the project folder:
   ```sh
   cd path/to/project
   ```
3. **Install Dependencies**:
   It's generally considered best practice to operate within a virtual environment. Use pip to install the necessary libraries:
   ```sh
   pip install pygame pygame_gui
   ```

## 🎮 Launching the Application

Run the central script to initiate the visualizer:
```sh
python main.py
```

## 🖱️ Interaction Guide

**Mouse Inputs:**
- **Primary Click (Left)**: 
  - First input sets the **Origin** node (Green).
  - Second input sets the **Destination** node (Red).
  - Subsequent inputs or dragging will construct **Barriers** (Gray).
- **Secondary Click (Right)**: Clears the state of any specific tile (removes walls or path markings, though start/goal tiles remain intact unless explicitly changed).

**Dashboard Elements:**
- **Algorithm Selection**: Browse and pick the active search methodology.
- **Heuristic Measure**: Toggle the internal formula used for distance prediction.
- **Create Layout**: Randomly scatters walls across the grid topology.
- **Begin Navigation**: Triggers the visual execution of the selected algorithm.
- **Wipe Board**: Entirely resets the grid, stripping all walls, paths, origin, and destination inputs.
- **Wipe Route**: Eliminates just the calculated pathways and explored states, preserving your custom layout.
- **Real-time Adjust Toggle**: Activates or deactivates the responsive probe entity.

## 🧠 Core Concepts

### Methodologies
- **A-Star Route**: Ensures finding the shortest possible path by weighing both the accumulated cost $g(n)$ and the predicted remaining cost $h(n)$.
- **Greedy Search Route**: Generally evaluates faster but without the guarantee of an optimal path length. It relies exclusively on the heuristic estimate $h(n)$.

### Heuristics
- **Manhattan**: Ideal for standard 4-way grid configurations, it tabulates the absolute differences in axis coordinates.
- **Euclidean**: Computes the direct straight-line distance, which is particularly relevant if diagonal traversal is factored into the routing costs.
