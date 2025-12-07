import tkinter as tk
from tkinter import simpledialog


class DisjointSet:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        if rootX != rootY:
            if self.rank[rootX] > self.rank[rootY]:
                self.parent[rootY] = rootX
            elif self.rank[rootX] < self.rank[rootY]:
                self.parent[rootX] = rootY
            else:
                self.parent[rootY] = rootX
                self.rank[rootX] += 1

    def add(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0


def rename_columns_with_dsu(first_array, second_array):
    dsu = DisjointSet()

    for pair in second_array:
        for element in pair:
            dsu.add(element)

    for pair in second_array:
        dsu.union(pair[0], pair[1])

    root_ground = dsu.find('Ground')
    dsu.parent['Ground'] = 'Ground'
    dsu.parent[root_ground] = 'Ground'

    root_to_number = {}
    current_number = 0
    for element in dsu.parent:
        root = dsu.find(element)
        if root not in root_to_number:
            if root == "Ground":
                root_to_number[root] = 0
            else:
                current_number += 1
                root_to_number[root] = current_number

    renamed_array = []
    for row in first_array:
        renamed_row = row[:]
        renamed_row[1] = str(root_to_number[dsu.find(row[1])])
        renamed_row[2] = str(root_to_number[dsu.find(row[2])])
        renamed_array.append(renamed_row)

    return renamed_array


class Component:
    def __init__(self, component_id, terminals, value=None):
        self.component_id = component_id
        self.terminals = terminals
        self.value = value


class CircuitGraph:
    def __init__(self):
        self.components = []
        self.connections = []

    def add_component(self, component):
        self.components.append(component)

    def add_connection(self, comp1_id, term1, comp2_id, term2):
        self.connections.append((comp1_id, term1, comp2_id, term2))

    def generate_netlist(self):
        netlist = []
        nodal = []
        final_netlist = []
        final_nodal = []
        ff_netlist = []

        for component in self.components:
            if component.component_id[0] != "G":
                entry = f"{component.component_id} " + " ".join(component.terminals)
                if component.value:
                    entry += f" {component.value}"
                netlist.append(entry)

        for comp1, term1, comp2, term2 in self.connections:
            nodal.append(f"{term1} connected to {term2}")

        for entry in netlist:
            final_netlist.append(entry.split(" "))

        for entry in nodal:
            final_nodal.append(entry.split(" connected to "))

        ff_netlist = rename_columns_with_dsu(final_netlist, final_nodal)
        return ff_netlist


class CircuitGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GSpice V_2.0.4")
        try:
            self.iconbitmap("logo.ico")
        except Exception:
            pass

        self.geometry("1000x650")
        self.configure(bg="#f3f4f6")

        self.status_var = tk.StringVar(value="Ready.")

        # -------- Top toolbar --------
        self.toolbar = tk.Frame(self, bg="#e5e7eb", padx=8, pady=4)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        common_btn_kwargs = {
            "master": self.toolbar,
            "padx": 8,
            "pady": 4,
            "bd": 0,
            "relief": tk.FLAT,
            "font": ("Segoe UI", 9, "bold"),
            "cursor": "hand2",
        }

        self.add_resistor_button = tk.Button(
            **common_btn_kwargs,
            text="Resistor",
            bg="#fee2e2",
            activebackground="#fecaca",
            command=self.select_resistor
        )
        self.add_resistor_button.pack(side=tk.LEFT, padx=(0, 4))

        self.add_capacitor_button = tk.Button(
            **common_btn_kwargs,
            text="Capacitor",
            bg="#e0f2fe",
            activebackground="#bae6fd",
            command=self.select_capacitor
        )
        self.add_capacitor_button.pack(side=tk.LEFT, padx=4)

        self.add_inductor_button = tk.Button(
            **common_btn_kwargs,
            text="Inductor",
            bg="#fef3c7",
            activebackground="#fde68a",
            command=self.select_inductor
        )
        self.add_inductor_button.pack(side=tk.LEFT, padx=4)

        self.add_voltage_source_button = tk.Button(
            **common_btn_kwargs,
            text="Voltage Source",
            bg="#dcfce7",
            activebackground="#bbf7d0",
            command=self.select_voltage_source
        )
        self.add_voltage_source_button.pack(side=tk.LEFT, padx=4)

        self.add_current_source_button = tk.Button(
            **common_btn_kwargs,
            text="Current Source",
            bg="#fee2e2",
            activebackground="#fecaca",
            command=self.select_current_source
        )
        self.add_current_source_button.pack(side=tk.LEFT, padx=4)

        self.add_ground_button = tk.Button(
            **common_btn_kwargs,
            text="Ground",
            bg="#e5e7eb",
            activebackground="#d1d5db",
            command=self.select_ground
        )
        self.add_ground_button.pack(side=tk.LEFT, padx=4)

        self.add_wire_button = tk.Button(
            **common_btn_kwargs,
            text="Wire",
            bg="#ede9fe",
            activebackground="#ddd6fe",
            command=self.toggle_wire_mode
        )
        self.add_wire_button.pack(side=tk.LEFT, padx=4)

        self.generate_simulate_button = tk.Button(
            **common_btn_kwargs,
            text="Simulate",
            bg="#4ade80",
            activebackground="#22c55e",
            fg="black",
            command=self.simulate
        )
        self.generate_simulate_button.pack(side=tk.RIGHT, padx=(4, 0))

        # -------- Canvas area --------
        self.canvas_frame = tk.Frame(self, bg="#f3f4f6", padx=10, pady=10)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="white",
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Background image (Modi ji)
        self.bg_image = None
        try:
            self.bg_image = tk.PhotoImage(file="modi_bg.png")
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        except Exception:
            pass

        # -------- Status bar --------
        self.status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            bg="#e5e7eb",
            fg="#111827",
            padx=10,
            pady=3,
            font=("Segoe UI", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # -------- Circuit data --------
        self.circuit = CircuitGraph()
        self.component_counter = 1
        self.selected_component_type = None
        self.wire_mode = False
        self.nodes = {}              # component_id -> {terminal_name: (x,y)}
        self.wires = []              # (line_id, comp1, term1, comp2, term2)
        self.component_labels = {}   # component_id -> {"value": text_id}

        # wiring anchor for multi-node joins
        self.wire_anchor = None      # (comp_id, terminal_name)

        # drag data
        self.drag_data = {
            "item": None,
            "component_id": None,
            "start_x": 0,
            "start_y": 0,
        }

        # context menu targets
        self.context_target_component = None
        self.context_target_wire = None

        # Mouse bindings
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.do_drag_component)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag_component)
        self.canvas.bind("<Button-3>", self.on_right_click)

    # ------------------- Mode selection ------------------- #
    def select_resistor(self):
        self.selected_component_type = "resistor"
        self.wire_mode = False
        self.wire_anchor = None
        self.status_var.set("Resistor placement mode.")

    def select_capacitor(self):
        self.selected_component_type = "capacitor"
        self.wire_mode = False
        self.wire_anchor = None
        self.status_var.set("Capacitor placement mode.")

    def select_inductor(self):
        self.selected_component_type = "inductor"
        self.wire_mode = False
        self.wire_anchor = None
        self.status_var.set("Inductor placement mode.")

    def select_voltage_source(self):
        self.selected_component_type = "voltage_source"
        self.wire_mode = False
        self.wire_anchor = None
        self.status_var.set("Voltage source placement mode.")

    def select_current_source(self):
        self.selected_component_type = "current_source"
        self.wire_mode = False
        self.wire_anchor = None
        self.status_var.set("Current source placement mode.")

    def select_ground(self):
        self.selected_component_type = "ground"
        self.wire_mode = False
        self.wire_anchor = None
        self.status_var.set("Ground placement mode.")

    def toggle_wire_mode(self):
        self.wire_mode = not self.wire_mode
        self.selected_component_type = "wire" if self.wire_mode else None
        self.wire_anchor = None
        if self.wire_mode:
            self.status_var.set("Wiring ON: click a terminal as anchor, then others to join.")
        else:
            self.status_var.set("Wiring OFF.")

    # ------------------- Canvas click router ------------------- #
    def on_canvas_click(self, event):
        if self.selected_component_type and self.selected_component_type != "wire":
            self.place_component(event)
        elif not self.wire_mode:
            self.start_drag_component(event)
        # wiring mode left-click on terminals handled by select_terminal

    # ------------------- Component placement ------------------- #
    def place_component(self, event):
        if not self.selected_component_type or self.selected_component_type == "wire":
            return

        if self.selected_component_type == "inductor":
            component_id = f"L{self.component_counter}"
            self.component_counter += 1
            value = None
        elif self.selected_component_type == "current_source":
            component_id = f"I{self.component_counter}"
            self.component_counter += 1
            value = None
        else:
            component_id = f"{self.selected_component_type[0].upper()}{self.component_counter}"
            self.component_counter += 1
            value = None

        x, y = event.x, event.y
        font_comp = ("Segoe UI", 9, "bold")
        value_text_id = None

        # ----- Resistor (symbol) -----
        if self.selected_component_type == "resistor":
            value = simpledialog.askstring(
                "Resistor Value",
                "Enter resistor value (e.g., 1E3 for 1kohm):"
            )
            if value is None:
                return

            self.canvas.create_rectangle(
                x, y, x + 60, y + 24,
                fill="",
                outline="",
                tags=(component_id,)
            )
            mid_y = y + 12
            points = [
                x, mid_y,
                x + 10, mid_y - 8,
                x + 20, mid_y + 8,
                x + 30, mid_y - 8,
                x + 40, mid_y + 8,
                x + 50, mid_y - 8,
                x + 60, mid_y
            ]
            self.canvas.create_line(*points, width=2, tags=(component_id,))

            self.canvas.create_text(
                x + 30, y - 8,
                text=component_id,
                font=font_comp,
                tags=(component_id,)
            )
            value_text_id = self.canvas.create_text(
                x + 30, y + 32,
                text=value,
                font=("Segoe UI", 7),
                tags=(component_id,)
            )

            terminals = {
                f"{component_id}.n1": (x, mid_y),
                f"{component_id}.n2": (x + 60, mid_y)
            }

        # ----- Capacitor (symbol) -----
        elif self.selected_component_type == "capacitor":
            value = simpledialog.askstring(
                "Capacitor Value",
                "Enter capacitor value (e.g., 10E-9 for 10nF):"
            )
            if value is None:
                return

            self.canvas.create_rectangle(
                x, y, x + 60, y + 24,
                fill="",
                outline="",
                tags=(component_id,)
            )

            mid_y = y + 12
            plate1_x = x + 22
            plate2_x = x + 38

            self.canvas.create_line(
                x, mid_y, plate1_x, mid_y,
                width=2,
                tags=(component_id,)
            )
            self.canvas.create_line(
                plate2_x, mid_y, x + 60, mid_y,
                width=2,
                tags=(component_id,)
            )
            self.canvas.create_line(
                plate1_x, y + 4, plate1_x, y + 20,
                width=2,
                tags=(component_id,)
            )
            self.canvas.create_line(
                plate2_x, y + 4, plate2_x, y + 20,
                width=2,
                tags=(component_id,)
            )

            self.canvas.create_text(
                x + 30, y - 8,
                text=component_id,
                font=font_comp,
                tags=(component_id,)
            )
            value_text_id = self.canvas.create_text(
                x + 30, y + 32,
                text=value,
                font=("Segoe UI", 7),
                tags=(component_id,)
            )

            terminals = {
                f"{component_id}.n1": (x, mid_y),
                f"{component_id}.n2": (x + 60, mid_y)
            }

        # ----- Inductor ----- 
        elif self.selected_component_type == "inductor":
            value = simpledialog.askstring(
                "Inductor Value",
                "Enter inductor value (e.g., 1E-3 for 1mH):"
            )
            if value is None:
                return

            self.canvas.create_rectangle(
                x, y, x + 60, y + 24,
                fill="#fed7aa",
                outline="#9a3412",
                width=1.5,
                tags=(component_id,)
            )
            self.canvas.create_text(
                x + 30, y + 8,
                text=component_id,
                font=font_comp,
                tags=(component_id,)
            )
            value_text_id = self.canvas.create_text(
                x + 30, y + 18,
                text=value,
                font=("Segoe UI", 7),
                tags=(component_id,)
            )
            terminals = {
                f"{component_id}.n1": (x, y + 12),
                f"{component_id}.n2": (x + 60, y + 12)
            }

        # ----- Voltage source (DC / AC) -----
        elif self.selected_component_type == "voltage_source":
            src_type = simpledialog.askstring(
                "Voltage Source Type",
                "Source type? (dc / ac) [default: dc]:",
                initialvalue="dc"
            )
            display_value = ""
            if src_type and src_type.lower().startswith("a"):
                v0 = simpledialog.askstring("AC Voltage Source", "Enter DC offset V0 (e.g., 0):")
                if v0 is None:
                    return
                va = simpledialog.askstring("AC Voltage Source", "Enter amplitude VA (e.g., 10):")
                if va is None:
                    return
                freq = simpledialog.askstring("AC Voltage Source", "Enter frequency F in Hz (e.g., 50):")
                if freq is None:
                    return
                value = f"SIN({v0},{va},{freq})"
                display_value = value
            else:
                value = simpledialog.askstring(
                    "Voltage Source Value",
                    "Enter DC voltage value (e.g., 5 for 5V):"
                )
                if value is None:
                    return
                display_value = value

            self.canvas.create_rectangle(
                x, y, x + 60, y + 24,
                fill="#bbf7d0",
                outline="#15803d",
                width=1.5,
                tags=(component_id,)
            )
            self.canvas.create_text(
                x + 30, y + 8,
                text=component_id,
                font=font_comp,
                tags=(component_id,)
            )
            value_text_id = self.canvas.create_text(
                x + 30, y + 18,
                text=display_value,
                font=("Segoe UI", 7),
                tags=(component_id,)
            )
            self.canvas.create_text(
                x + 8, y + 12,
                text="+",
                font=("Segoe UI", 9, "bold"),
                fill="#166534",
                tags=(component_id,)
            )
            self.canvas.create_text(
                x + 52, y + 12,
                text="-",
                font=("Segoe UI", 9, "bold"),
                fill="#b91c1c",
                tags=(component_id,)
            )

            terminals = {
                f"{component_id}.n1": (x, y + 12),
                f"{component_id}.n2": (x + 60, y + 12)
            }

        # ----- Current source (DC / AC) -----
        elif self.selected_component_type == "current_source":
            src_type = simpledialog.askstring(
                "Current Source Type",
                "Source type? (dc / ac) [default: dc]:",
                initialvalue="dc"
            )
            display_value = ""
            if src_type and src_type.lower().startswith("a"):
                i0 = simpledialog.askstring("AC Current Source", "Enter DC offset I0 (e.g., 0):")
                if i0 is None:
                    return
                ia = simpledialog.askstring("AC Current Source", "Enter amplitude IA (e.g., 0.01):")
                if ia is None:
                    return
                freq = simpledialog.askstring("AC Current Source", "Enter frequency F in Hz (e.g., 50):")
                if freq is None:
                    return
                value = f"SIN({i0},{ia},{freq})"
                display_value = value
            else:
                value = simpledialog.askstring(
                    "Current Source Value",
                    "Enter DC current value (e.g., 5 for 5A):"
                )
                if value is None:
                    return
                display_value = value

            self.canvas.create_rectangle(
                x, y, x + 60, y + 24,
                fill="#fecaca",
                outline="#b91c1c",
                width=1.5,
                tags=(component_id,)
            )
            self.canvas.create_text(
                x + 30, y + 8,
                text=component_id,
                font=font_comp,
                tags=(component_id,)
            )
            value_text_id = self.canvas.create_text(
                x + 30, y + 18,
                text=display_value,
                font=("Segoe UI", 7),
                tags=(component_id,)
            )
            terminals = {
                f"{component_id}.n1": (x, y + 12),
                f"{component_id}.n2": (x + 60, y + 12)
            }

        # ----- Ground -----
        elif self.selected_component_type == "ground":
            self.canvas.create_oval(
                x - 10, y - 10, x + 10, y + 10,
                fill="#a8a29e",
                outline="#44403c",
                width=1.5,
                tags=(component_id,)
            )
            self.canvas.create_text(
                x, y + 20,
                text=component_id,
                font=font_comp,
                tags=(component_id,)
            )
            terminals = {"Ground": (x, y)}

        else:
            return

        component = Component(component_id, terminals, value)
        self.circuit.add_component(component)
        self.nodes[component_id] = terminals

        if value_text_id is not None:
            self.component_labels[component_id] = {"value": value_text_id}

        # terminal pins
        for term, (tx, ty) in terminals.items():
            terminal_tag = f"{component_id}_{term}"
            self.canvas.create_oval(
                tx - 3, ty - 3, tx + 3, ty + 3,
                fill="black",
                outline="black",
                tags=(terminal_tag, component_id)
            )
            self.canvas.tag_bind(
                terminal_tag,
                "<Button-1>",
                lambda event, cid=component_id, t=term: self.select_terminal(cid, t)
            )

        self.selected_component_type = None
        self.status_var.set(f"Placed {component_id}.")

    # ------------------- Wiring with multi-node join ------------------- #
    def select_terminal(self, component_id, terminal):
        if self.wire_mode:
            if self.wire_anchor is None:
                self.wire_anchor = (component_id, terminal)
                self.status_var.set(
                    f"Anchor set at {terminal}. Click other terminals to join this node. Click again to clear."
                )
            else:
                if (component_id, terminal) == self.wire_anchor:
                    self.status_var.set("Anchor cleared.")
                    self.wire_anchor = None
                else:
                    comp1, term1 = self.wire_anchor
                    comp2, term2 = component_id, terminal
                    x1, y1 = self.nodes[comp1][term1]
                    x2, y2 = self.nodes[comp2][term2]

                    line_id = self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill="#111827",
                        width=2
                    )
                    self.wires.append((line_id, comp1, term1, comp2, term2))
                    self.circuit.add_connection(comp1, term1, comp2, term2)

                    self.status_var.set(
                        f"Connected {term1} to {term2}. Anchor still at {self.wire_anchor[1]}."
                    )

            return "break"

    # ------------------- Dragging components ------------------- #
    def start_drag_component(self, event):
        if self.wire_mode or self.selected_component_type:
            return

        item = self.canvas.find_withtag("current")
        if not item:
            return

        tags = self.canvas.gettags("current")
        comp_id = None
        for t in tags:
            if t in self.nodes:
                comp_id = t
                break

        if not comp_id:
            return

        self.drag_data["item"] = item[0]
        self.drag_data["component_id"] = comp_id
        self.drag_data["start_x"] = event.x
        self.drag_data["start_y"] = event.y
        self.status_var.set(f"Moving {comp_id}...")

    def do_drag_component(self, event):
        comp_id = self.drag_data["component_id"]
        if not comp_id:
            return

        dx = event.x - self.drag_data["start_x"]
        dy = event.y - self.drag_data["start_y"]
        self.drag_data["start_x"] = event.x
        self.drag_data["start_y"] = event.y

        self.canvas.move(comp_id, dx, dy)

        for term in self.nodes[comp_id]:
            x, y = self.nodes[comp_id][term]
            self.nodes[comp_id][term] = (x + dx, y + dy)

        for (line_id, c1, term1, c2, term2) in self.wires:
            if c1 == comp_id or c2 == comp_id:
                x1, y1 = self.nodes[c1][term1]
                x2, y2 = self.nodes[c2][term2]
                self.canvas.coords(line_id, x1, y1, x2, y2)

    def end_drag_component(self, event):
        if self.drag_data["component_id"]:
            self.status_var.set(f"Moved {self.drag_data['component_id']}.")
        self.drag_data["item"] = None
        self.drag_data["component_id"] = None

    # ------------------- Right-click context menu ------------------- #
    def on_right_click(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return

        item_id = item[0]
        menu = tk.Menu(self, tearoff=0)

        # Check if clicked on wire
        wire_info = None
        for w in self.wires:
            if w[0] == item_id:
                wire_info = w
                break

        if wire_info is not None:
            self.context_target_wire = wire_info
            menu.add_command(label="Delete Wire", command=self.delete_selected_wire)
        else:
            # Maybe a component
            tags = self.canvas.gettags(item_id)
            comp_id = None
            for t in tags:
                if t in self.nodes:
                    comp_id = t
                    break

            if not comp_id:
                return

            self.context_target_component = comp_id
            ctype = comp_id[0]
            if ctype in ("R", "C", "L", "V", "I"):
                menu.add_command(label="Edit Value", command=self.edit_selected_component_value)
            menu.add_command(label="Delete Component", command=self.delete_selected_component)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def edit_selected_component_value(self):
        comp_id = self.context_target_component
        if not comp_id:
            return

        comp = next((c for c in self.circuit.components if c.component_id == comp_id), None)
        if not comp:
            return

        initial = str(comp.value) if comp.value is not None else ""
        new_val = simpledialog.askstring(
            "Edit Component Value",
            f"Enter new value for {comp_id} (e.g., 1E3 or SIN(0,10,50)):",
            initialvalue=initial
        )
        if new_val is None:
            return

        comp.value = new_val
        label_info = self.component_labels.get(comp_id)
        if label_info and "value" in label_info:
            self.canvas.itemconfigure(label_info["value"], text=new_val)

        self.status_var.set(f"Updated value of {comp_id} to {new_val}.")

    def delete_selected_component(self):
        comp_id = self.context_target_component
        if not comp_id:
            return

        # remove drawing of component + terminals (all have comp_id tag)
        self.canvas.delete(comp_id)

        # delete wires connected to this component
        remaining_wires = []
        for (line_id, c1, term1, c2, term2) in self.wires:
            if c1 == comp_id or c2 == comp_id:
                self.canvas.delete(line_id)
                if (c1, term1, c2, term2) in self.circuit.connections:
                    self.circuit.connections.remove((c1, term1, c2, term2))
            else:
                remaining_wires.append((line_id, c1, term1, c2, term2))
        self.wires = remaining_wires

        # remove from nodes and components
        self.nodes.pop(comp_id, None)
        self.circuit.components = [
            c for c in self.circuit.components if c.component_id != comp_id
        ]
        self.component_labels.pop(comp_id, None)

        # clear anchor if needed
        if self.wire_anchor and self.wire_anchor[0] == comp_id:
            self.wire_anchor = None

        self.status_var.set(f"Deleted {comp_id}.")

    def delete_selected_wire(self):
        wire = self.context_target_wire
        if not wire:
            return
        line_id, c1, term1, c2, term2 = wire
        self.canvas.delete(line_id)
        self.wires = [w for w in self.wires if w[0] != line_id]
        if (c1, term1, c2, term2) in self.circuit.connections:
            self.circuit.connections.remove((c1, term1, c2, term2))
        self.status_var.set("Wire deleted.")

    # ------------------- Simulation ------------------- #
    def simulate(self):
        netlist = self.circuit.generate_netlist()
        with open("output.txt", "w") as file:
            for entry in netlist:
                for component in entry:
                    print(component, end=" ")
                    file.write(str(component) + " ")
                print("\n")
                file.write("\n")
        self.status_var.set("Simulation netlist generated: output.txt")


if __name__ == "__main__":
    app = CircuitGUI()
    app.mainloop()
