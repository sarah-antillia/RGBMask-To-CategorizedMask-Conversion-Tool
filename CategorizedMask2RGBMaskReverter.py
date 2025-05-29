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

# 2025/05/29
# CategorizedMask2RGBMaskReverter.py

import os
import sys
import numpy as np
import glob
import shutil
from PIL import Image
from CategorizerConfig import CategorizerConfig
import traceback

class CategorizedMask2RGBMaskReverter:

  def __init__(self, mask_decatorizer_ini, verbose=False):
    self.verbose = verbose
    self.config  = CategorizerConfig( mask_decatorizer_ini)
     
    self.rgb_file_format = self.config.get(CategorizerConfig.MASK_CATEGORIZER,"rgb_file_format", dvalue=".png") 
    self.rgb_map = self.config.get(CategorizerConfig.MASK_CATEGORIZER, "rgb_map")
    self.rev_rgb_map = {v: k for k, v in self.rgb_map.items()} 
    self.categorized_file_format = self.config.get(CategorizerConfig.MASK_CATEGORIZER,"categorized_file_format", dvalue=".npz")
    self.categorized_masks_dir   = self.config.get(CategorizerConfig.MASK_CATEGORIZER,"categorized_masks_dir")
    self.rgb_masks_dir           = self.config.get(CategorizerConfig.MASK_CATEGORIZER,"rgb_masks_dir")
    self.reverted_masks_dir      = self.config.get(CategorizerConfig.MASK_CATEGORIZER,"reverted_masks_dir")

  def revert(self):
    if os.path.exists(self.reverted_masks_dir):
      shutil.rmtree(self.reverted_masks_dir)
    os.makedirs(self.reverted_masks_dir)     
    cat_mask_files = glob.glob(self.categorized_masks_dir + "/*" + self.categorized_file_format)
     
    for cat_mask_file in cat_mask_files:
      rgb_mask = self.revert_one(cat_mask_file)
      basename = os.path.basename(cat_mask_file)
      rgb_filename = basename.replace(self.categorized_file_format, self.rgb_file_format)
      rgb_filepath = os.path.join(self.reverted_masks_dir, rgb_filename)
      rgb_mask.save(rgb_filepath)
      print("Save reverted rgb_mask file {}".format(rgb_filepath))

  def read_categorized_mask_file(self, npz_file):
    loaded = np.load(npz_file)
    keys   = list(loaded.keys())
    name   = "mask"
    categorized_mask = None
    if name in keys:
      categorized_mask = loaded[name]
    return categorized_mask
  
  def revert_one(self, cat_mask_file):
    categorized_mask = self.read_categorized_mask_file(cat_mask_file)
    print("Shape fo categorized_mask {}".format(categorized_mask.shape))
    height, width, num_classes = categorized_mask.shape
    indexed_mask = np.argmax(categorized_mask, axis=-1)
    #print(indexed_mask)    
    #print("Indexed mask shape {}".format(indexed_mask.shape))
    print("Mask file {} height {} width {} num_classe {}".format(cat_mask_file, height, width, num_classes))
    rgb_mask = np.zeros((height, width, 3), dtype=np.uint8)
    for index, color in self.rev_rgb_map.items():
      rgb_mask[indexed_mask == index] = color

    # Return PIL image
    return Image.fromarray(rgb_mask)
  
if __name__ == "__main__":
  try:
    mask_decategorizer_ini = "./mask_decategorizer.ini"
    if len(sys.argv) == 2:
      mask_decategorizer_ini = sys.argv[1]

    reverter = CategorizedMask2RGBMaskReverter(mask_decategorizer_ini, verbose=True)
    reverter.revert()
  except:
    traceback.print_exc()
