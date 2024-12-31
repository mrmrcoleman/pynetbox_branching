import requests
import time
import contextlib

class Branch:
    DEFAULT_TIMEOUT = 30  # Timeout in seconds for waiting on branch readiness

    def __init__(self, netbox_api, netbox_token, branch_name, create=False, wait_on_ready=False):
        """
        Initializes a Branch object.

        :param netbox_api: The NetBox API URL.
        :param netbox_token: The API token for authenticating with NetBox.
        :param branch_name: The name of the branch to manage.
        :param create: If True, create the branch if it does not exist.
        :param wait_on_ready: If True, wait until the branch status becomes 'ready' after creation.
        :raises ValueError: If the branch does not exist and create is False.
        :raises TimeoutError: If waiting on readiness exceeds the TIMEOUT seconds.
        """
        self.netbox_api = netbox_api.rstrip("/")
        self.netbox_token = netbox_token
        self.branch_name = branch_name
        self.headers = {
            "Authorization": f"Token {self.netbox_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.status = None
        self.name = None
        self.schema_id = None

        if not create:
            # Check if branch exists
            branch_info = self._get_branch_info()
            if not branch_info:
                raise ValueError(f"Branch '{branch_name}' does not exist.")
            self._set_branch_attributes(branch_info)
        else:
            # Create the branch if it does not exist
            branch_info = self._get_branch_info()
            if not branch_info:
                branch_info = self._create_branch(wait_on_ready)
            self._set_branch_attributes(branch_info)

    def _get_branch_info(self):
        """
        Retrieve branch information.

        :return: Branch information dictionary or None if the branch does not exist.
        """
        url = f"{self.netbox_api}/api/plugins/branching/branches/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        branches = response.json().get("results", [])
        for branch in branches:
            if branch["name"] == self.branch_name:
                return branch
        return None

    def _create_branch(self, wait_on_ready):
        """
        Create a new branch.

        :param wait_on_ready: If True, wait until the branch status becomes 'ready'.
        :return: Created branch information.
        :raises TimeoutError: If the branch does not become 'ready' within the timeout period.
        """
        url = f"{self.netbox_api}/api/plugins/branching/branches/"
        data = {"name": self.branch_name, "status": "provisioning"}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        branch = response.json()

        if wait_on_ready:
            start_time = time.time()
            print(f"Waiting for branch '{self.branch_name}' to become ready...")
            while time.time() - start_time < self.DEFAULT_TIMEOUT:
                branch_info = self._get_branch_info()
                if branch_info and branch_info.get("status").get("value") == "ready":
                    print(f"Branch '{self.branch_name}' is now ready.")
                    return branch_info
                print("Branch not ready yet. Checking again...")
                time.sleep(1)
            raise TimeoutError(f"Branch '{self.branch_name}' did not become 'ready' within {self.DEFAULT_TIMEOUT} seconds.")

        return branch

    def _set_branch_attributes(self, branch_info):
        """
        Set branch attributes from branch information.

        :param branch_info: Branch information dictionary.
        """
        self.status = branch_info.get("status").get("value")
        self.name = branch_info.get("name")
        self.schema_id = branch_info.get("schema_id")

    @contextlib.contextmanager
    def activate_branch(self, pynetbox):
        """
        Context manager to activate the branch by setting the schema ID in the pynetbox headers.

        :param pynetbox: The pynetbox API instance whose headers will be updated.
        :raises ValueError: If the branch does not have a schema_id.
        """
        if not self.schema_id:
            raise ValueError(f"Branch '{self.branch_name}' does not have a valid schema_id.")

        original_schema_id = pynetbox.http_session.headers.get("X-NetBox-Branch")
        pynetbox.http_session.headers["X-NetBox-Branch"] = self.schema_id

        try:
            yield
        finally:
            if original_schema_id:
                pynetbox.http_session.headers["X-NetBox-Branch"] = original_schema_id
            else:
                pynetbox.http_session.headers.pop("X-NetBox-Branch", None)

    def delete(self):
        """
        Deletes the branch.

        :raises ValueError: If the branch does not exist.
        :raises RuntimeError: If the deletion request fails.
        """
        branch_info = self._get_branch_info()
        if not branch_info:
            raise ValueError(f"Branch '{self.branch_name}' does not exist and cannot be deleted.")

        url = f"{self.netbox_api}/api/plugins/branching/branches/{branch_info['id']}/"
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print(f"Branch '{self.branch_name}' deleted successfully.")
        else:
            raise RuntimeError(f"Failed to delete branch '{self.branch_name}'. Status code: {response.status_code}, Response: {response.text}")