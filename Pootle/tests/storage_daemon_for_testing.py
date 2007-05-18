
import os
from Pootle.storage.PootleStorageServer import set_storage_root, run_storage



if __name__ == "__main__":
    set_storage_root(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testroot'))

    run_storage()
