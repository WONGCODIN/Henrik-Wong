#!/usr/bin/env python3
import os
import sys


def find_and_select_chk_files(search_path='.'):
    """
    Scans a directory for .chk files and returns a list of chosen files.
    The user can select one, or all of them.

    Args:
        search_path (str): The directory path to search in.

    Returns:
        list: A list of selected .chk filenames. Returns an empty list on failure.
    """
    try:
        # Find all files in the directory ending with .chk (case-insensitive)
        chk_files = sorted([f for f in os.listdir(search_path) if f.lower().endswith('.chk')])
    except FileNotFoundError:
        print(f"Error: The directory '{search_path}' was not found.")
        return []

    if not chk_files:
        print(f"Error: No .chk files found in the directory '{search_path}'.")
        return []

    if len(chk_files) == 1:
        selected_chk = chk_files[0]
        print(f"Found and automatically selected the only .chk file: {selected_chk}")
        return [selected_chk]  # Return as a list with one item
    else:
        print("Multiple .chk files found. Please choose which one(s) to use:")
        for i, filename in enumerate(chk_files):
            print(f"  {i + 1}: {filename}")
        print("\n  A: Process ALL listed files")  # The new 'All' option

        while True:
            choice = input(f"Enter your choice (1-{len(chk_files)} or A): ").strip().upper()

            if choice == 'A':
                print("Selected to process ALL files.")
                return chk_files  # Return the full list

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(chk_files):
                    selected_file = chk_files[choice_num - 1]
                    print(f"Selected: {selected_file}")
                    return [selected_file]  # Return as a list with one item
                else:
                    print("Invalid number. Please enter a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number from the list or 'A' for all.")


def parse_axes_input(axis_input):
    """
    Parse axis input into a list of unique axes in X/Y/Z order.

    Accepts single-axis input (e.g., "Y"), comma-separated lists
    (e.g., "Y,Z"), and "ALL" for all axes.
    """
    normalized = axis_input.strip().upper()
    if normalized == "ALL":
        return ["X", "Y", "Z"]

    tokens = [token.strip() for token in normalized.replace(" ", "").split(",") if token.strip()]
    if not tokens:
        raise ValueError("No axis provided")

    valid_axes = {"X", "Y", "Z"}
    if any(token not in valid_axes for token in tokens):
        raise ValueError("Invalid axis selection")

    ordered_unique = []
    for axis in ["X", "Y", "Z"]:
        if axis in tokens:
            ordered_unique.append(axis)

    return ordered_unique


def generate_scripts():
    """
    Generates Gaussian input files for electric field calculations
    based on one or more user-selected checkpoint files.
    """
    # --- Part 1: Find and select the base .chk file(s) ---
    chk_search_path = input("Enter the directory containing the source .chk file(s) (press Enter for current directory): ") or "."
    source_chk_files = find_and_select_chk_files(chk_search_path)

    # If no files were selected, exit the script.
    if not source_chk_files:
        print("\nNo .chk files selected. Aborting script generation.")
        sys.exit()

    print("-" * 40)

    # --- Part 2: Get user inputs for the electric field ONCE ---
    print("Please define the electric field parameters to apply to all selected files.")
    while True:
        axis_choice = input(
            "Question 1: What axis for the electric field?\n"
            "- Enter one: X, Y, or Z\n"
            "- Enter multiple (comma-separated): X,Y  or Y,Z  or X,Z\n"
            "- Enter ALL for X,Y,Z\n"
        )
        try:
            axes = parse_axes_input(axis_choice)
            break
        except ValueError:
            print("Invalid axis selection. Use X, Y, Z, comma-separated combinations, or ALL.")
    start_strength = int(input("Question 2: What is the starting field strength (e.g., -50)?\n"))
    end_strength = int(input("Question 3: What is the ending field strength (e.g., 50)?\n"))
    step_size = int(input("Question 4: What are the steps of field strength (e.g., 10)?\n"))
    output_directory = input("Enter the path for the output directory (e.g., 'output_files'): ")

    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created output directory: {output_directory}")

    # Generate field strengths based on input
    field_strengths = range(start_strength, end_strength + step_size, step_size)

    # --- Part 3: Define the template ---
    script_template = """%oldchk={old_chk_name}
%chk={chk_name}.chk
%mem=80GB
#p M062X/Gen gfinput gfoldprint 5d test scf=(novaracc,xqc) Int=(UltraFine,Acc2E=12) nosymm Temperature=298.15 scrf=(SMD,solvent=Water) pop=full Guess=read Geom=check Field={field}

TITLE: {title} / 6-Nitronorleucine / M06-2X/ SMD WATER / H C N O - Def2TZVPPD/  Electric Field Effect on {field} @Generated by Van der WONG

0 1

H     0
S    3   1.00
     34.0613410              0.60251978D-02
      5.1235746              0.45021094D-01
      1.1646626              0.20189726
S    1   1.00
      0.32723041             1.0000000
S    1   1.00
      0.10307241             1.0000000
P    1   1.00
      1.40700000             1.0000000
P    1   1.00
      0.38800000             1.0000000
P    1   1.00
      0.95774129632D-01      1.0000000
D    1   1.00
      1.05700000             1.0000000
****
C     0
S    6   1.00
  13575.3496820              0.22245814352D-03
   2035.2333680              0.17232738252D-02
    463.22562359             0.89255715314D-02
    131.20019598             0.35727984502D-01
     42.853015891            0.11076259931
     15.584185766            0.24295627626
S    2   1.00
      6.2067138508           0.41440263448
      2.5764896527           0.23744968655
S    1   1.00
      0.57696339419          1.0000000
S    1   1.00
      0.22972831358          1.0000000
S    1   1.00
      0.95164440028D-01      1.0000000
S    1   1.00
      0.48475401370D-01      1.0000000
P    4   1.00
     34.697232244            0.53333657805D-02
      7.9582622826           0.35864109092D-01
      2.3780826883           0.14215873329
      0.81433208183          0.34270471845
P    1   1.00
      0.28887547253           .46445822433
P    1   1.00
      0.10056823671           .24955789874
D    1   1.00
      1.09700000             1.0000000
D    1   1.00
      0.31800000             1.0000000
D    1   1.00
      0.90985336424D-01      1.0000000
F    1   1.00
      0.76100000             1.0000000
****
N     0
S    6   1.00
  19730.8006470              0.21887984991D-03
   2957.8958745              0.16960708803D-02
    673.22133595             0.87954603538D-02
    190.68249494             0.35359382605D-01
     62.295441898            0.11095789217
     22.654161182            0.24982972552
S    2   1.00
      8.9791477428           0.40623896148
      3.6863002370           0.24338217176
S    1   1.00
      0.84660076805          1.0000000
S    1   1.00
      0.33647133771          1.0000000
S    1   1.00
      0.13647653675          1.0000000
S    1   1.00
      0.68441605847D-01      1.0000000
P    4   1.00
     49.200380510            0.55552416751D-02
     11.346790537            0.38052379723D-01
      3.4273972411           0.14953671029
      1.1785525134           0.34949305230
P    1   1.00
      0.41642204972           .45843153697
P    1   1.00
      0.14260826011           .24428771672
D    1   1.00
      1.65400000             1.0000000
D    1   1.00
      0.46900000             1.0000000
D    1   1.00
      0.12829642058          1.0000000
F    1   1.00
      1.09300000             1.0000000
****
O     0
S    6   1.00
  27032.3826310              0.21726302465D-03
   4052.3871392              0.16838662199D-02
    922.32722710             0.87395616265D-02
    261.24070989             0.35239968808D-01
     85.354641351            0.11153519115
     31.035035245            0.25588953961
S    2   1.00
     12.260860728            0.39768730901
      4.9987076005           0.24627849430
S    1   1.00
      1.1703108158           1.0000000
S    1   1.00
      0.46474740994          1.0000000
S    1   1.00
      0.18504536357          1.0000000
S    1   1.00
      0.70288026270D-01      1.0000000
P    4   1.00
     63.274954801            0.60685103418D-02
     14.627049379            0.41912575824D-01
      4.4501223456           0.16153841088
      1.5275799647           0.35706951311
P    1   1.00
      0.52935117943           .44794207502
P    1   1.00
      0.17478421270           .24446069663
P    1   1.00
      0.51112745706D-01      1.0000000
D    1   1.00
      2.31400000             1.0000000
D    1   1.00
      0.64500000             1.0000000
D    1   1.00
      0.14696477366          1.0000000
F    1   1.00
      1.42800000             1.0000000
****











"""

    # --- Part 4: Loop through each source CHK file and generate scripts ---
    total_files_generated = 0
    print("-" * 40)
    print("Generating scripts...")

    for old_chk_name in source_chk_files:
        # Use the name of the chk file (without extension) as the base for new files
        base_filename = os.path.splitext(old_chk_name)[0]
        print(f"\nProcessing base file: {old_chk_name}")

        for axis in axes:
            for strength in field_strengths:
                # Create a clean string for filenames (e.g., X+0050, Z-0010)
                field_strength_str = f"{axis}{strength:+05d}"

                # The new filename is based on the source chk file's name
                chk_name = f"{base_filename}_EF{field_strength_str}_UB3LYP"
                title = f"{chk_name}.gjf"

                # Format the field keyword for Gaussian input
                field_keyword = f"{axis}{strength}"

                new_script = script_template.format(
                    old_chk_name=old_chk_name,
                    chk_name=chk_name,
                    field=field_keyword,
                    title=title
                )

                # Save the new script in the output directory
                new_script_path = os.path.join(output_directory, f"{chk_name}.gjf")
                with open(new_script_path, 'w') as file:
                    file.write(new_script)

                print(f"  - Created: {new_script_path}")
                total_files_generated += 1

    print("-" * 40)
    print(f"Script generation complete. Total files created: {total_files_generated}")


# Call the function to start the process
if __name__ == "__main__":
    generate_scripts()
