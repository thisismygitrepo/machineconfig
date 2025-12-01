import subprocess
import time

from machineconfig.scripts.python.helpers.helpers_network.address import get_public_ip_address


def switch_public_ip_address(max_trials: int = 10, wait_seconds: float = 4.0) -> None:
    print("🔁 Switching IP ... ")
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing
    install_if_missing("warp-cli")

    current_ip: str | None = None
    try:
        current_data = get_public_ip_address()
        current_ip = current_data.get("ip")
    except Exception as e:
        print(f"⚠️ Could not get current IP: {e}")

    print(f"Current IP: {current_ip}")

    for attempt in range(1, max_trials + 1):
        print(f"\n--- Attempt {attempt}/{max_trials} ---")

        print("🔻 Deactivating current connection ... ")
        # We use check=False because if it's already deleted it might return non-zero
        subprocess.run(["warp-cli", "registration", "delete"], check=False)

        print(f"😴 Sleeping for {wait_seconds} seconds ... ")
        time.sleep(wait_seconds)

        print("🔼 Registering new connection ... ")
        res_reg = subprocess.run(["warp-cli", "registration", "new"], check=False)
        if res_reg.returncode != 0:
            print("⚠️ Registration failed, retrying loop...")
            continue

        print("🔗 Connecting ... ")
        subprocess.run(["warp-cli", "connect"], check=False)

        print(f"😴 Sleeping for {wait_seconds} seconds ... ")
        time.sleep(wait_seconds)

        print("🔍 Checking status of warp ... ")
        subprocess.run(["warp-cli", "status"], check=False)

        print("🔍 Checking new IP ... ")
        new_ip: str | None = None
        # Retry getting IP a few times before giving up on this connection attempt
        for ip_check_attempt in range(5):
            try:
                new_data = get_public_ip_address()
                new_ip = new_data["ip"]
                if new_ip:
                    break
            except Exception as e:
                print(f"⚠️ Error checking new IP (attempt {ip_check_attempt+1}/5): {e}")
                time.sleep(wait_seconds)

        if new_ip:
            print(f"New IP: {new_ip}")

            if current_ip and new_ip != current_ip:
                print("✅ Done ... IP Changed.")
                return
            elif current_ip is None:
                print("✅ Done ... IP obtained (was unknown).")
                return
            else:
                print("❌ IP did not change.")
        else:
            print("⚠️ Could not retrieve new IP after multiple attempts.")

    print("❌ Failed to switch IP after max trials.")


if __name__ == "__main__":
    switch_public_ip_address()

