import types
import sys
from utils import encode_features

fake_main = types.ModuleType('__main__')
fake_main.encode_features = encode_features
sys.modules['__main__'] = fake_main
