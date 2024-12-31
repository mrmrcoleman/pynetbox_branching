# pynetbox-branching

> [!WARNING]
> This is a personal project for now and has not been thoroughy tested  
> You are **strongly advised against** using this against production NetBox instances  

> [!NOTE]  
> This is likely a stopgap solution until we get branching support into `pynetbox` however I am still interested in feedback on this approach. Please create an issue or come and find me in the NetDev Slack: [https://netdev.chat/](https://netdev.chat/)  

## Overview

`pynetbox-branching` is a Python library designed to simplify the management of branches in NetBox and enable seamless interaction with NetBox objects on specific branches. This library works alongside `pynetbox` adding branch management capabilities, including branch creation, activation, and deletion.

## Usage

> [!TIP]
> See below for instructions on running the full example in `examples/example.py`  

**Instantiate our branch object**

First we instantiate a branch in `pynetbox-branching`. Check the code for the various available options.

In this case we use `create=True` to create the branch if it doesn't exist and `wait_on_ready=True` to wait until the branch is ready.

```
branch_name = f"new-branch-{datetime.now().strftime('%Y%m%d%H%M%S')}"
new_branch = Branch(netbox_api=NETBOX_API,
                    netbox_token=NETBOX_TOKEN,
                    branch_name=branch_name,
                    create=True,
                    wait_on_ready=True)

# Output
Waiting for branch 'new-branch-20241231181609' to become ready...
Branch not ready yet. Checking again...
Branch not ready yet. Checking again...
Branch not ready yet. Checking again...
Branch 'new-branch-20241231181609' is now ready.
```

**Inspect branch details**

Our newly created branch can now be inspected for the last known details about the branch in NetBox.

```
print(f'''
Branch name: {new_branch.name}
Status: {new_branch.status}
Schema ID: {new_branch.schema_id}
''')

# Output

Branch name: new-branch-20241231181609
Status: ready
Schema ID: ot05qd3z
```

**Running `pynetbox` actions against our new branch**

> [!TIP]
> You can see that we need to pass a `pynetbox` object to `activate_branch()`  
> See `examples/example.py` for a complete example of how this works  

```
with new_branch.activate_branch(pynetbox=nb):
    sites = nb.dcim.sites.create(name="New Site", slug="branch-site") # Add a site to the branch
    sites = nb.dcim.sites.all() # Get all sites in the branch
    
    print(f"Sites in {new_branch.name}:") # Display sites in the branch
    for site in sites:
        print(f"Site Name: {site.name}, Slug: {site.slug}, ID: {site.id}")

# Output
Sites in new-branch-20241231181609:
Site Name: New Site, Slug: branch-site, ID: 588
```

**Delete our branch**

> [!WARNING]
> Be very careful with `.delete()`. In the NetBox Branching GUI you are asked to confirm deletions. Here deletions are **applied directly!**  

```
new_branch.delete()

# Output
Branch 'new-branch-20241231181609' deleted successfully.
```
---

## Running the example

`examples/example.py` is a fuller example of using `pynetbox-branching` alongside `pynetbox`.


Clone the repo.

```
git clone https://github.com/mrmrcoleman/pynetbox_branching
cd pynetbox_branching
```

Create your `.env` file.

```
cp .env.example .env
vim .env # <-- Add your details
```

Create and activate a VirtualEnv.

```
python3 -m venv venv
source venv/bin/activate
```

Install `pynetbox-branching`.

```
pip install -e .
```

Install the requirements for `example.py`.

```
pip install -r example-requirements.txt
```

Run the script.

```
python examples/example.py

# Output
Waiting for branch 'new-branch-20241231181609' to become ready...
Branch not ready yet. Checking again...
Branch not ready yet. Checking again...
Branch not ready yet. Checking again...
Branch 'new-branch-20241231181609' is now ready.

Branch name: new-branch-20241231181609
Status: ready
Schema ID: ot05qd3z

Sites in new-branch-20241231181609:
Site Name: New Site, Slug: branch-site, ID: 588
Sites in main:
Branch 'new-branch-20241231181609' deleted successfully.
```

