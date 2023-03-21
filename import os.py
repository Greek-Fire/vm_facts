import os
import tempfile
import json
from ansible_runner.interface import init_runner, run

def execute_playbook(playbook_path, inventory_path, target_host, bastion_host, private_key_path):
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create ansible.cfg
        ansible_cfg = f"""
            [defaults]
            host_key_checking = False
            scp_if_ssh = True

            [paramiko_connection]
            record_host_keys = False

            [ssh_connection]
            ssh_args = -o ProxyJump={bastion_host} -o ForwardAgent=yes -o ControlMaster=auto -o ControlPersist=60s
            """

        with open(os.path.join(tmp_dir, "ansible.cfg"), "w") as f:
            f.write(ansible_cfg)

        # Prepare Ansible runner
        runner = init_runner(
            playbook=playbook_path,
            inventory=inventory_path,
            private_data_dir=tmp_dir,
            cmdline="--private-key {}".format(private_key_path),
            host_pattern=target_host,
        )

        # Execute the playbook
        result = run(runner)

        return result

def main():
    playbook_path = "path/to/your/playbook.yml"
    inventory_path = "path/to/your/inventory.ini"
    target_host = "your_target_host"
    bastion_host = "your_bastion_host"
    private_key_path = "path/to/your/private_key.pem"

    result = execute_playbook(playbook_path, inventory_path, target_host, bastion_host, private_key_path)

    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
