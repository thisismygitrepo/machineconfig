"""
CPU Specification Helper.

This module provides utilities to detect the CPU model and fetch Geekbench scores
using the geekbench-browser-python tool.
"""

import platform
import re
import subprocess


def get_cpu_name() -> str:
    """
    Detect the CPU model name across different operating systems.

    Returns:
        str: The detected CPU model name or 'Unknown CPU'.
    """
    system = platform.system()

    if system == "Linux":
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":", 1)[1].strip()
        except FileNotFoundError:
            pass

    elif system == "Windows":
        try:
            # shell=True might be needed for wmic depending on environment,
            # but usually check_output with string list is safer if executable is in path.
            # User provided: wmic cpu get name
            output = subprocess.check_output("wmic cpu get name", shell=True).decode()
            lines = output.strip().split("\n")
            if len(lines) > 1:
                return lines[1].strip()
        except (subprocess.CalledProcessError, IndexError):
            pass

    elif system == "Darwin":
        try:
            return subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"]
            ).decode().strip()
        except subprocess.CalledProcessError:
            pass

    return "Unknown CPU"


def clean_cpu_name(cpu_name: str) -> str:
    """
    Clean the CPU name to improve Geekbench search results.

    Removes extra details like 'w/ Radeon Graphics', frequency, etc.

    Args:
        cpu_name (str): The raw CPU name string.

    Returns:
        str: A cleaned CPU name suitable for searching.
    """
    # Remove "w/ ..." or "with ..."
    # Example: AMD Ryzen 7 8745HS w/ Radeon 780M Graphics -> AMD Ryzen 7 8745HS
    cleaned = re.split(r"\s+(w/|with)\s+", cpu_name, flags=re.IGNORECASE)[0]

    # Remove (R) and (TM) symbols which confuse regex search and are often noisy
    cleaned = re.sub(r"\([RT]M?\)", "", cleaned, flags=re.IGNORECASE)

    # Remove clock speed like " @ 3.00GHz", " 3.00GHz", " 3.2GHz"
    cleaned = re.sub(r"\s+@?\s*\d+(\.\d+)?\s*GHz", "", cleaned, flags=re.IGNORECASE)

    # Remove "12-Core Processor" etc if present (some linux distros add this)
    cleaned = re.sub(r"\s+\d+-Core\s+Processor", "", cleaned, flags=re.IGNORECASE)

    # Remove trailing "Processor" word if it's there
    cleaned = re.sub(r"\s+Processor", "", cleaned, flags=re.IGNORECASE)

    # Collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def run_geekbench_lookup(search_term: str) -> bool:
    """
    Run the geekbench search using uvx.

    Args:
        search_term (str): The CPU name to search for (supports Regex).

    Returns:
        bool: True if results were found, False otherwise.
    """
    # Note: uvx caches the tool so subsequent runs are fast.
    # The 'gbr' tool uses pandas.str.contains(regex=True), so we can use regex patterns.
    # We quote the search term to ensure it's treated as a single pattern containing spaces.
    cmd = [
        "uvx",
        "--from",
        "geekbench-browser-python",
        "gbr",
        search_term,
        "--verbose",
    ]
    printable_cmd = " ".join(f'"{x}"' if " " in x else x for x in cmd)
    print(f"Running: {printable_cmd}")
    try:
        # Capture output to check for results
        # We enforce utf-8 encoding because 'geekbench-browser-python' likely outputs
        # Unicode characters (Rich tables, box drawing) which can fail to decode or
        # appear as garbage on Windows (default cp1252) if not handled.
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout

        # Check if we have data rows.
        # Check iteratively for lines that look like data rows (Unicode or ASCII).
        lines = output.splitlines()
        has_data = False
        for line in lines:
            line_stripped = line.strip()
            # Unicode table data row start (Light Vertical)
            if "│" in line:
                has_data = True
                break
            # ASCII table data row start (Pipe)
            # Must exclude headers and separators which also start with pipe in ASCII mode.
            if line_stripped.startswith("|"):
                lower_line = line.lower()
                # Skip header/separator lines
                if "description" in lower_line or "single" in lower_line or "---" in line:
                    continue
                has_data = True
                break
        
        if has_data:
            print(output)
            return True
        else:
            # If verbose debugging is needed, we could print output here.
            # But normally if no table is found, the tool might have just printed log info to stderr.
            # If it did print something to stdout that isn't a table, we probably shouldn't show it
            # as a "result", but it might be helpful for debugging why it failed.
            if output.strip():
                 # Only print debug info if it's NOT just an empty table structure to avoid noise
                 if not ("description" in output.lower() and ("---" in output or "│" in output)):
                     print(f"Debug output from tool:\n{output}")
            
            print(f"No results found for '{search_term}'.")
            return False

    except subprocess.CalledProcessError:
        print("Failed to retrieve Geekbench scores (command failed).")
        return False
    except FileNotFoundError:
        print("Error: 'uvx' command not found. Please ensure 'uv' is installed.")
        return False


def main() -> None:
    """Main entry point."""
    cpu_name = get_cpu_name()
    print(f"Detected CPU: {cpu_name}")

    if cpu_name == "Unknown CPU":
        print("Could not detect CPU name. Exiting.")
        return

    full_search_term = clean_cpu_name(cpu_name)
    
    # Retry logic: remove last word until we find something or run out of words
    # We escape each word to ensure regex special characters (like +, (), etc) in the name
    # are treated as literals, while preserving our ability to use regex wildcards later.
    words = [re.escape(w) for w in full_search_term.split()]
    
    while words:
        current_term = " ".join(words)
        
        # Heuristic: Don't search for extremely short generic terms if possible,
        # but "AMD" or "Intel" might be what we end up with if nothing else works.
        # Let's try at least length 2 words unless it's just 1 word left.
        if len(words) > 1 and len(current_term) < 4:
             words.pop()
             continue

        print(f"Search Term: {current_term}")
        if run_geekbench_lookup(current_term):
            return
        
        last_word = words[-1]
        numeric_part = None

        # Check if the last word starts with digits (e.g. 8745HS or 8745)
        # We want to both strip suffix AND try wildcards.
        match_digits = re.match(r"^(\d+)([a-zA-Z].*)?$", last_word)
        
        if match_digits:
            numeric_part = match_digits.group(1)
            suffix_part = match_digits.group(2) # May be None

            # Intermediate Try 1: Strip suffix (e.g. 8745HS -> 8745)
            if suffix_part and len(numeric_part) >= 3:
                 intermediate_term = " ".join(words[:-1] + [numeric_part])
                 if intermediate_term != current_term:
                     print(f"Search Term: {intermediate_term} (stripped suffix)")
                     if run_geekbench_lookup(intermediate_term):
                        return
            
            # Intermediate Try 2: Wildcard/Regex search (e.g. 8745 -> 87..)
            # The tool uses Regex, so we use dots '.' to match any character instead of '?'
            if numeric_part and len(numeric_part) >= 3:
                # If 4+ digits (e.g. 8745), replace last 2 with .. -> 87..
                # If 3 digits (e.g. 780), replace last 1 with . -> 78.
                if len(numeric_part) >= 4:
                    wildcard_model = numeric_part[:-2] + ".."
                else:
                    wildcard_model = numeric_part[:-1] + "."
                
                wildcard_term = " ".join(words[:-1] + [wildcard_model])
                
                # Check duplication against current_term and the stripped version
                stripped_term = " ".join(words[:-1] + [numeric_part])
                if wildcard_term != current_term and wildcard_term != stripped_term:
                     print(f"Search Term: {wildcard_term} (regex wildcard)")
                     if run_geekbench_lookup(wildcard_term):
                        return

        # Remove last word for next iteration
        words.pop()

    print("Could not find any matching Geekbench scores.")


if __name__ == "__main__":
    main()
