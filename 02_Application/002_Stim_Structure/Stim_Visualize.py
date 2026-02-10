import stim
import cairosvg

# 1. Load the circuit
file_path = "ideal_surface_code.stim"
try:
    with open(file_path, "r") as f:
        circuit = stim.Circuit(f.read())
    print(f"Successfully loaded '{file_path}'")
except FileNotFoundError:
    print(f"Error: '{file_path}' not found.")
    exit()

# 2. Function to save diagram as PNG
def save_as_png(diagram_helper, output_filename):
    # Convert the DiagramHelper to an SVG string
    svg_data = str(diagram_helper)
    
    # Convert SVG string to PNG file
    # scale=2.0 increases the resolution for better quality
    cairosvg.svg2png(bytestring=svg_data, write_to=output_filename, scale=2.0)
    print(f"Saved: {output_filename}")

# 3. Save Timeline (Gate Sequence) as PNG
print("Converting Timeline to PNG...")
save_as_png(circuit.diagram(type="timeline-svg"), "circuit_timeline.png")

# 4. Save Qubit Layout (2D Grid) as PNG
# We use 'detector-slice-svg' at tick 0 to get the physical layout
print("Converting Layout to PNG...")
save_as_png(circuit.diagram(type="detector-slice-svg", tick=0), "qubit_layout.png")

print("\nProcessing complete. Check your folder for .png files.")