from pynetbox_branching import Branch
from dotenv import load_dotenv
from datetime import datetime
import pynetbox
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
NETBOX_API = os.getenv("NETBOX_API")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

# Initialize pynetbox API instance
nb = pynetbox.api(
    NETBOX_API,
    token=NETBOX_TOKEN
)

'''
Create a branch

`create=True` - create the branch if it doesn't already exist
`wait_on_ready=True` - wait for Branch.DEFAULT_TILEOUT seconds for the branch to be ready, or fail
'''

branch_name = f"new-branch-{datetime.now().strftime('%Y%m%d%H%M%S')}"
new_branch = Branch(netbox_api=NETBOX_API,
                    netbox_token=NETBOX_TOKEN,
                    branch_name=branch_name,
                    create=True,
                    wait_on_ready=True)

'''
Inspect branch details
'''

print(f'''
Branch name: {new_branch.name}
Status: {new_branch.status}
Schema ID: {new_branch.schema_id}
''')


'''
Use the branch context manager to run pynetbox operations against the branch

The context manager will automatically set the pynetbox http "X-NetBox-Branch" headers to
the branch schema_id and then set them back to the original value when the context manager exits.

All pynetbox operations must happen within the with statement or they will not be run against the branch.
'''

with new_branch.activate_branch(pynetbox=nb):
    sites = nb.dcim.sites.create(name="New Site", slug="branch-site") # Add a site to the branch
    sites = nb.dcim.sites.all() # Get all sites in the branch
    
    print(f"Sites in {new_branch.name}:") # Display sites in the branch
    for site in sites:
        print(f"Site Name: {site.name}, Slug: {site.slug}, ID: {site.id}")

'''
Use pynetbox to list sites in the main branch
'''
sites = nb.dcim.sites.all()
print("Sites in main:")
for site in sites:
    print(f"Site Name: {site.name}, Slug: {site.slug}, ID: {site.id}")


'''
Delete the branch

Checks if the branch still exists in NetBox and if so, deletes it.
'''
new_branch.delete()