# **Oil Spill Simulation in Bay City**

---

## **Overview**

This project simulates the movement of an oil spill in a coastal region, specifically designed for "Bay City." The simulation evaluates the impact of the spill on fishing grounds, offering insights to help mitigate environmental and economic damage.

The software employs object-oriented programming and numerical simulation techniques to track the oil distribution across a two-dimensional computational mesh over time.

---

## **Features**

1. **Oil Spill Simulation**:
   - Models oil movement based on the provided velocity field and computational mesh.
   - Supports restarting simulations from saved states.

2. **Visualization**:
   - Generates plots of the oil distribution at the final simulation time.
   - Creates animations of the oil's movement over time.

3. **Configuration**:
   - Reads simulation parameters from TOML configuration files.
   - Supports running multiple configurations in batch mode.

4. **Error Handling**:
   - Validates inputs and provides meaningful error messages for missing or inconsistent configuration files.

5. **Extensibility**:
   - Designed for easy integration of new features, such as additional cell types or flow fields.

---

## **Technical Details**

### **Input and Output**
- **Input**: 
  - Computational mesh file (`bay.msh`).
  - Configuration files in TOML format specifying simulation parameters.
- **Output**:
  - Simulation logs, plots, animations, and solution files for restarting simulations.

### **Key Components**
- **Mesh Representation**: 
  - Divides the domain into triangular and line cells, computing properties such as midpoints, neighbors, and outward normals.
- **Simulation Engine**:
  - Calculates oil fluxes between neighboring cells over time steps.
- **Visualization Tools**:
  - Generates plots and animations for better analysis and presentation.

---

## **Project Structure**

```
├── config_files/        # Contains TOML configuration files
├── data/mesh/           # Contains the computational mesh file
├── results/             # Stores simulation outputs (plots, animations, logs)
├── src/                 # Source code organized into modules
│   ├── cell/            # Cell representations and computations
│   ├── io/              # Input-output operations (e.g., config readers)
│   ├── simulation/      # Simulation engine
│   └── visualization/   # Plotting and animation tools
├── tests/               # Unit tests for all components
├── requirements.txt     # List of required Python packages
├── main.py              # Main entry point for the simulation
└── README.md            # Project overview and usage instructions
```

---

## **Installation**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/username/oil-spill-simulation.git
   cd oil-spill-simulation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Usage**

### **Run a Single Configuration**
Run the simulation using a specified configuration file:
```bash
python main.py --config_file config_files/example.toml
```

### **Run Multiple Configurations**
Run all configurations in a folder:
```bash
python main.py --find all --folder config_files/
```

### **Generate Plots and Animations**
Output results, including final plots and animations, in the `results/` folder.

---

## **Testing**

Run the unit tests using `pytest`:
```bash
pytest tests/
```
The code achieves over 90% test coverage and ensures functionality for all major components.

---

## **Documentation**

The project is extensively documented:
- **Docstrings**: Available for all classes, methods, and modules.
- **Report**: A detailed technical report is included in the repository.

---
