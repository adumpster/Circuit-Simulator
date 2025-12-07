# Circuit Simulator & Analyzer

![Course](https://img.shields.io/badge/Course-EE204-blue) ![Institution](https://img.shields.io/badge/IIT-Guwahati-red) ![Language](https://img.shields.io/badge/Python-MATLAB-green)

**Circuit Simulator & Analyzer** is a tool developed as a course project for **EE204: Analog Electronics** at **IIT Guwahati**. The project combines a user-friendly Python-based GUI for designing circuits with a robust MATLAB backend for performing Modified Nodal Analysis (MNA) and transient response simulations.

---

## 📋 Table of Contents
- [Features](#-features)
- [Theoretical Background](#-theoretical-background)
  - [Frontend: Netlist Generation & DSU](#frontend-netlist-generation--dsu)
  - [Backend: Modified Nodal Analysis (MNA)](#backend-modified-nodal-analysis-mna)
- [How to Run](#-how-to-run)
- [Project Structure](#-project-structure)


---

## 🚀 Features

### Frontend (Python)
* **Interactive GUI:** Built with `tkinter`, allowing drag-and-drop placement of components.
* **Component Library:** Supports Resistors, Capacitors, Inductors, DC/AC Voltage Sources, DC/AC Current Sources, and Ground.
* **Smart Wiring:** "Point-to-point" wiring system.
* **Netlist Generation:** Automatically converts the visual graph into a SPICE-like netlist format (`output.txt`).

### Backend (MATLAB)
* **Modified Nodal Analysis (MNA):** Solves for node voltages and branch currents.
* **Symbolic Solver:** Uses MATLAB's Symbolic Math Toolbox to construct and solve circuit equations.
* **Transient Analysis:** Capable of solving reactive circuits (RC, RL, RLC) and time-varying sources using the `ode15i` solver for Differential-Algebraic Equations (DAEs).
* **Visualization:** Automatically generates plots for:
    * Node Voltages vs. Time.
    * Currents through Sources & Inductors.
    * Currents through Resistors & Capacitors.

---

## 📚 Theoretical Background

### Frontend: Netlist Generation & DSU
The Python frontend handles the task of converting a 2D visual drawing into a logical electrical graph. To achieve this effectively, it utilizes the **Disjoint Set Union (DSU)** (or Union-Find) data structure.

1.  **Node Identification:** Every time a wire connects two terminals, the algorithm treats them as a set.
2.  **Union Operation:** When multiple wires meet, their sets are "unioned" together.
3.  **Path Compression:** The DSU algorithm creates a unique "parent" representative for every electrically connected node, effectively handling complex, multi-wire junctions.
4.  **Renaming:** Finally, all connected components are mapped to unique integer node numbers (0 for Ground, 1, 2, 3... for others) to generate the standard Netlist format.

### Backend: Modified Nodal Analysis (MNA)

The MATLAB script implements **Modified Nodal Analysis (MNA)**, the industry-standard algorithm used in SPICE simulators. Unlike basic Nodal Analysis, which only solves for node voltages and struggles with ideal voltage sources, MNA solves for both voltages and specific branch currents simultaneously.

#### 1. System Variables
The MNA algorithm builds a state vector **x** comprising two types of variables:

<p align="center">
  <img src="https://latex.codecogs.com/svg.latex?\mathbf{x}%20=%20\begin{bmatrix}%20\mathbf{v}%20\\%20\mathbf{i}%20\end{bmatrix}" alt="State Vector" />
</p>

* **Node Voltages (v):** The voltage at every node (except ground).
* **Branch Currents (i):** The currents flowing through elements that cannot be represented by simple admittance (e.g., Voltage Sources and Inductors).

#### 2. Equation Formulation
The system of equations is constructed by combining Kirchhoff's Current Law (KCL) and Constitutive Element Equations.

**A. KCL at Nodes (Row Equations):**
For every node $n$, the sum of currents leaving the node must equal zero.
* **Resistors:** Contribution is $G(v_n - v_m)$, where $G = 1/R$.
* **Current Sources:** Added directly to the Right-Hand Side (RHS) vector.
* **Voltage Sources/Inductors:** The current variables ($i_{Vsrc}$, $i_L$) are added explicitly to the equation.
* **Capacitors:** Contribution is dynamic: $C \frac{d(v_n - v_m)}{dt}$.

**B. Auxiliary Equations (Branch Equations):**
For elements where current is a variable, an additional equation is needed:
* **Voltage Source:** $v_n - v_m = V_{source}$
* **Inductor:** $v_n - v_m = L \frac{di_L}{dt}$

#### 3. Differential Algebraic Equations (DAE)
Including capacitors and inductors transforms the system from linear algebra into a system of **Differential Algebraic Equations (DAEs)** of the form:
$$\mathbf{F}(t, \mathbf{y}, \mathbf{y}') = 0$$
Where $\mathbf{y}$ represents our state vector of voltages and currents.

#### 4. The Solution Strategy (ode15i)
* **Symbolic Generation:** The script first generates these KCL and Branch equations symbolically using MATLAB's Symbolic Math Toolbox (e.g., creating strings like `'v_1 - v_2 - L*diff(i_L, t) = 0'`).
* **Function Handle Conversion:** These symbolic equations are converted into a MATLAB function handle using `daeFunction`.
* **Numerical Integration:** We use **`ode15i`**, a variable-order solver for fully implicit differential equations. This solver is chosen because circuit equations are often **stiff** (containing time constants that vary by orders of magnitude), which standard explicit solvers (like `ode45`) handle poorly.

---

## 💻 How to Run

### Step 1: Design the Circuit
1.  Navigate to the project directory.
2.  Run the Python GUI:
    ```bash
    python frontend.py
    ```
3.  **Place Components:** Click the buttons on the top toolbar (Resistor, Source, etc.) and place them on the canvas.
4.  **Wire Them:** Click "Wire", click a component terminal (anchor), and click another terminal to connect them.
5.  **Set Values:** Enter values like `100` (Ohms), `10E-6` (Farads), or `SIN(0, 10, 50)` (for AC: Offset, Amplitude, Freq).
6.  **Simulate:** Click the **Simulate** button. This creates a file named `output.txt` in the directory.

### Step 2: Analyze the Circuit
1.  Open MATLAB.
2.  Run the script `Circuit_Analysis.m`.
3.  When prompted in the Command Window:
    ```text
    Enter circuit netlist file (.txt or .cir) - output.txt
    ```
4.  **Simulate:**
    * If the circuit contains L/C or AC sources, enter the final simulation time ($t_f$) when prompted.
5.  **View Results:**
    * MATLAB will generate plots for Voltages and Currents.
    * Numerical results are saved to `Results.txt`.

---

## 📂 Project Structure

```text
.
├── frontend.py      # Python source code for the GUI and Netlist generator
├── Circuit_Analysis.m    # MATLAB source code for MNA and Simulation
├── logo.ico              # (Optional) Icon for the GUI
├── output.txt            # Generated Netlist (intermediate file)
├── Results.txt           # Final calculation results generated by MATLAB
└── README.md             # Project Documentation
