from machineconfig.cluster.sessions_managers.windows_terminal.wt_local_manager import WTLocalManager
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig


def run_demo() -> None:
    sample_sessions: list[LayoutConfig] = [
        {
            "layoutName": "DevelopmentEnv",
            "layoutTabs": [
                {"tabName": "🚀Frontend", "startDir": "~/code/myapp/frontend", "command": "bun run dev"},
                {"tabName": "⚙️Backend", "startDir": "~/code/myapp/backend", "command": "python manage.py runserver"},
                {"tabName": "📊Monitor", "startDir": "~", "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"},
            ],
        },
        {
            "layoutName": "TestingEnv",
            "layoutTabs": [
                {"tabName": "🧪Tests", "startDir": "~/code/myapp", "command": "pytest --watch"},
                {"tabName": "🔍Coverage", "startDir": "~/code/myapp", "command": "python -m coverage run --source=. -m pytest"},
                {"tabName": "📝Logs", "startDir": "~/logs", "command": "Get-Content app.log -Wait"},
            ],
        },
        {
            "layoutName": "DeploymentEnv",
            "layoutTabs": [
                {"tabName": "🐳Docker", "startDir": "~/code/myapp", "command": "docker-compose up"},
                {"tabName": "☸️K8s", "startDir": "~/k8s", "command": "kubectl get pods --watch"},
                {"tabName": "📈Metrics", "startDir": "~", "command": 'Get-Counter "\\Processor(_Total)\\% Processor Time" -SampleInterval 2 -MaxSamples 30'},
            ],
        },
    ]

    try:
        local_manager = WTLocalManager(sample_sessions, session_name_prefix="DevEnv")
        print(f"✅ Local manager created with {len(local_manager.managers)} sessions")

        print(f"📋 Sessions: {local_manager.get_all_session_names()}")

        print("\n📎 Attachment commands:")
        print(local_manager.attach_to_session())

        print("\n🔍 Current status:")
        local_manager.print_status_report()

        print("\n🖥️  Windows Terminal Overview:")
        overview = local_manager.get_wt_overview()
        if overview["success"]:
            print(f"   Total WT windows: {overview['total_windows']}")
            print(f"   Managed sessions: {overview['managed_sessions']}")
        else:
            print(f"   Error: {overview.get('error', 'Unknown')}")

        print("\n💾 Demonstrating save/load...")
        saved_session_id = local_manager.save()
        print(f"✅ Saved session: {saved_session_id}")

        saved_sessions = WTLocalManager.list_saved_sessions()
        print(f"📋 Saved sessions: {saved_sessions}")

        loaded_manager = WTLocalManager.load(saved_session_id)
        print(f"✅ Loaded session with {len(loaded_manager.managers)} sessions")

        print("\n⏰ To start monitoring, run:")
        print("local_manager.run_monitoring_routine(wait_ms=30000)  # 30 seconds")

    except Exception as ex:
        print(f"❌ Error: {ex}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_demo()
