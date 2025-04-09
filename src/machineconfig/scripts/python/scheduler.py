"""cli for scheduler
"""

from machineconfig.utils.scheduling import P, Report, DEFAULT_CONFIG, read_task_from_dir, main

def main_parse():
    import argparse
    print("\n" + "=" * 50)
    print("📅 Welcome to the Scheduler CLI")
    print("=" * 50 + "\n")

    parser = argparse.ArgumentParser(description='Run tasks.')
    parser.add_argument('root', type=str, default=None, help='📁 Root directory of tasks.')
    parser.add_argument('--ignore_conditions', "-i", action='store_true', help='🚫 Ignore conditions for running tasks.', default=False)
    parser.add_argument('--report', "-R", action='store_true', help='📊 Print report.', default=False)
    parser.add_argument('--create_task', "-c", action='store_true', help='🆕 Add default config.', default=False)
    args = parser.parse_args()

    tmp = P(args.root).expanduser().absolute()
    if P(args.root).joinpath(".scheduler").exists():
        root = P(args.root).joinpath(".scheduler")
    elif tmp.name == ".scheduler":
        root = tmp
    else:
        root = tmp.joinpath(".scheduler").create()

    print(f"\n✅ Running tasks in {root}\n")

    if args.report:
        print("📊 Generating report...")
        reports: list[Report] = [Report.from_path(read_task_from_dir(x).report_path) for x in P(root).search("*").filter(lambda path: path.joinpath("task.py").exists())]
        import pandas as pd
        df_res = pd.DataFrame([r.__dict__ for r in reports])
        print(df_res.to_markdown())
        print("\n✅ Report generated successfully!\n")
        return None

    if args.create_task:
        task_name = input("📝 Enter task name: ")
        task_root = root.joinpath(task_name).create(exist_ok=False)
        task_root.joinpath("config.ini").write_text(DEFAULT_CONFIG, encoding="utf-8")
        task_root.joinpath("task.py").write_text("""
# Scheduler Task.
""")
        print(f"\n✅ Task '{task_name}' created in {task_root}. Head there and edit the config.ini file & task.py file.\n")
        return None

    print("🚀 Executing tasks...")
    main(root=root.to_str(), ignore_conditions=args.ignore_conditions)
    print("🎉 All tasks executed successfully!\n")

if __name__ == "__main__":
    main_parse()
