from crocodile.core import randstr
from pathlib import Path
import subprocess
import multiprocessing
import time

cwd = Path.cwd()

print("\n" + "=" * 50)
print("🌐 Welcome to the URL to Markdown Converter")
print("=" * 50 + "\n")

tools_needed = ["xcrawl3r", "html2markdown"]


url = input("🔗 Enter the URL: ")
depth = input("🔍 Enter the crawl depth (default: 4): ") or "4"

website_name_as_valid_filename = url.split("//")[-1].split("/")[0].replace(".", "_").replace(":", "_")
op_dir = cwd.joinpath(".website", website_name_as_valid_filename)
op_dir.mkdir(exist_ok=True, parents=True)
urls_file = op_dir.joinpath("urls", "urls.txt")
urls_file.parent.mkdir(exist_ok=True, parents=True)
if urls_file.exists():
    urls_file.unlink()

print("🌐 Crawling the website to extract URLs...")
command = f"""xcrawl3r --url {url} --domain {url} --depth {depth} --concurrency 20 --parallelism 10 --output {urls_file} """
subprocess.run(command, shell=True, check=True)

all_urls = urls_file.read_text().splitlines()
relevant_urls = [a_url for a_url in all_urls if a_url.startswith(url)]
relevant_urls = list(set(relevant_urls))  # remove duplicates

print(f"✅ Found {len(relevant_urls)} relevant URLs. Preparing to convert to Markdown...\n")

commands: list[str] = []
for a_url in relevant_urls:
    commands.append(f"""curl {a_url} | html2markdown --output {op_dir.joinpath(a_url.split('/')[-1] + "_" + randstr(5) + ".md")} """)

def run_command(cmd):
    try:
        _result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Completed: {cmd[:60]} ...")
        return True
    except subprocess.SubprocessError as e:
        print(f"❌ Error with command: {cmd[:60]}...\n{str(e)}")
        return False

def main():
    cpu_count = multiprocessing.cpu_count()
    max_processes = min(20, cpu_count)
    print(f"🚀 Running commands with {max_processes} parallel processes...\n")

    start_time = time.time()

    with multiprocessing.Pool(processes=max_processes) as pool:
        results = pool.map(run_command, commands)

    successful = results.count(True)
    failed = results.count(False)
    elapsed_time = time.time() - start_time

    print(f"\n⏱️ Completed in {elapsed_time:.2f} seconds")
    print(f"✅ Successfully processed: {successful} files")
    if failed > 0:
        print(f"❌ Failed to process: {failed} files")

    print(f"📂 Output saved to: {op_dir}\n")

if __name__ == "__main__":
    main()

