import subprocess
import time
from typing import Any

from machineconfig.scripts.python.helpers_network.address import get_public_ip_address


def switch_public_ip_address(max_trials: int = 10) -> None:
    print("🔁 Switching IP ... ")

    current_ip: str | None = None
    try:
        current_data: dict[str, Any] = get_public_ip_address()
        current_ip = current_data.get("ip")
    except Exception as e:
        print(f"⚠️ Could not get current IP: {e}")

    print(f"Current IP: {current_ip}")

    for attempt in range(1, max_trials + 1):
        print(f"\n--- Attempt {attempt}/{max_trials} ---")

        print("🔻 Deactivating current connection ... ")
        # We use check=False because if it's already deleted it might return non-zero
        subprocess.run(["warp-cli", "registration", "delete"], check=False)

        print("😴 Sleeping for 2 seconds ... ")
        time.sleep(2)

        print("🔼 Registering new connection ... ")
        res_reg = subprocess.run(["warp-cli", "registration", "new"], check=False)
        if res_reg.returncode != 0:
            print("⚠️ Registration failed, retrying loop...")
            continue

        print("🔗 Connecting ... ")
        subprocess.run(["warp-cli", "connect"], check=False)

        print("😴 Sleeping for 2 seconds ... ")
        time.sleep(2)

        print("🔍 Checking status of warp ... ")
        subprocess.run(["warp-cli", "status"], check=False)

        print("🔍 Checking new IP ... ")
        try:
            new_data: dict[str, Any] = get_public_ip_address()
            new_ip = new_data.get("ip")
            print(f"New IP: {new_ip}")

            if current_ip and new_ip != current_ip:
                print("✅ Done ... IP Changed.")
                return
            elif current_ip is None and new_ip:
                print("✅ Done ... IP obtained (was unknown).")
                return
            else:
                print("❌ IP did not change.")
        except Exception as e:
            print(f"⚠️ Error checking new IP: {e}")

    print("❌ Failed to switch IP after max trials.")


if __name__ == "__main__":
    switch_public_ip_address()

