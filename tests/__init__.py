import sys
import os
from dotenv import load_dotenv
load_dotenv()
environment = os.environ["ENVIRONMENT"]='testing'

sys.path.append('../../')