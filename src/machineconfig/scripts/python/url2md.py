
from crocodile.core import randstr
from pathlib import Path
import subprocess
import multiprocessing
import time

cwd = Path.cwd()

url = input("Enter the URL: ")
op_dir = cwd.joinpath(".website", url.split("/")[-1])
op_dir.mkdir(exist_ok=True, parents=True)
urls_file = op_dir.joinpath("urls.txt")
if urls_file.exists(): urls_file.unlink()


command = f"""xcrawl3r --url {url} --depth 10 --concurrency 20 --parallelism 5 --output {urls_file} """
subprocess.run(command, shell=True, check=True)

all_urls = urls_file.read_text().splitlines()
relevant_urls = [a_url for a_url in all_urls if a_url.startswith(url)]
relevant_urls = list(set(relevant_urls))  # remove duplicates


commands: list[str] = []
for a_url in relevant_urls:
    commands.append(f"""curl {a_url} | html2markdown --output {op_dir.joinpath(a_url.split('/')[-1] + "_" + randstr(5) + ".md")} """)

# run 20 commands in parallel, should work in both Linux and Windows
def run_command(cmd):
    try:
        _result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"Completed: {cmd[:60]} ...")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error with command: {cmd[:60]}...\n{str(e)}")
        return False

def main():
    # Determine number of parallel processes (use at most 20)
    cpu_count = multiprocessing.cpu_count()
    max_processes = min(20, cpu_count)
    print(f"Running commands with {max_processes} parallel processes...")

    start_time = time.time()

    # Create a pool of workers
    with multiprocessing.Pool(processes=max_processes) as pool:
        results = pool.map(run_command, commands)

    # Report results
    successful = results.count(True)
    failed = results.count(False)
    elapsed_time = time.time() - start_time

    print(f"\nCompleted in {elapsed_time:.2f} seconds")
    print(f"Successfully processed: {successful} files")
    if failed > 0:
        print(f"Failed to process: {failed} files")

    print(f"Output saved to: {op_dir}")


if __name__ == "__main__":
    main()

