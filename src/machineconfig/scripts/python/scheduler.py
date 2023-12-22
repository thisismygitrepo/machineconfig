
"""cli for scheduler
"""

from machineconfig.utils.scheduling import P, Report, DEFAULT_CONFIG, read_task_from_dir, main


def main_parse():
    import argparse
    parser = argparse.ArgumentParser(description='Run tasks.')
    parser.add_argument('root', type=str, default=None, help='Root directory of tasks.')
    parser.add_argument('--ignore_conditions', "-i", action='store_true', help='Ignore conditions for running tasks.', default=False)
    parser.add_argument('--report', "-R", action='store_true', help='Print report.', default=False)
    parser.add_argument('--create_task', "-c", action='store_true', help='Add default config.', default=False)
    # print(parser)
    args = parser.parse_args()

    tmp = P(args.root).expanduser().absolute()
    if P(args.root).joinpath(".scheduler").exists():  # .search(files=False, folders=True)[0].joinpath("task.py").exists():
        root = P(args.root).joinpath(".scheduler")
    if tmp.name == ".scheduler":
        root = tmp
    else:
        root = tmp.joinpath(".scheduler").create()
        # raise ValueError(f"Could not find a task.py in {args.root} or {P(args.root).joinpath('.scheduler')}")
    print(f"✅ Running tasks in {root}")

    if args.report:
        reports: list[Report] = [Report.from_path(read_task_from_dir(x).report_path) for x in P(root).search("*").filter(lambda path: path.joinpath("task.py").exists())]
        import pandas as pd
        df_res = pd.DataFrame([r.__dict__ for r in reports])
        # root.joinpath("task_report.md").write_text(df_res.to_markdown(), encoding="utf-8")
        print(df_res.to_markdown())
        # df_res.to_
        return None

    if args.create_task:
        task_name = input("Enter task name: ")
        task_root = root.joinpath(task_name).create(exist_ok=False)
        # assert not root.joinpath("config.ini").exists(), f"Config file already exists in {root}"
        task_root.joinpath("config.ini").write_text(DEFAULT_CONFIG, encoding="utf-8")
        task_root.joinpath("task.py").write_text(f"""
# Scheduler Task.
""")
        print(f"✅ Task {task_name} created in {task_root}. Head there and edit the config.ini file & task.py file.")
        return None

    main(root=root.str, ignore_conditions=args.ignore_conditions)


if __name__ == "__main__":
    main_parse()
