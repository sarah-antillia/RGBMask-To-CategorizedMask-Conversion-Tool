# Copyright 2025 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# CategorizerConfig.py
#
import os
import sys
import glob
import traceback

from ConfigParser import ConfigParser

class CategorizerConfig(ConfigParser):
  # CATEGORIZED_MASK Section
  MASK_CATEGORIZER   = "mask_categorizer"
 
  # Constructor
  # 
  def __init__(self, config_path, verbose=True):
    super().__init__(config_path, verbose)


if __name__ == "__main__":
  try:
    file = "./mask_categorizer.ini"
    parser = CategorizerConfig(file)
    
    rgb_map = parser.get(CategorizerConfig.MASK_CATEGORIZER, "rgb_map", dvalue={(0,0,0):0})
    print(rgb_map)
  except:
    traceback.print_exc()
