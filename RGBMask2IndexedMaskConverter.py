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

# 2025/05/25
# RGBMask2IndexedMaskConverter.py


import os
import time
import glob
import shutil
import traceback

from PIL import Image
import numpy as np
from CategorizerConfig import CategorizerConfig

class RGBMask2IndexedMaskConverter:

  def __init__(self, categorizer_ini, verbose=False):
    self.config          = CategorizerConfig(categorizer_ini)
    self.rgb_map         = self.config.get(CategorizerConfig.MASK_CATEGORIZER,  "rgb_map")
    self.color_order     = self.config.get(CategorizerConfig.MASK_CATEGORIZER,  "color_order") 

    self.rgb_file_format = self.config.get(CategorizerConfig.MASK_CATEGORIZER,  "rgb_file_format", dvalue=".png")
    self.rgb_masks_dir   = self.config.get(CategorizerConfig.MASK_CATEGORIZER,  "rgb_masks_dir")
    
    self.indexed_file_format = self.config.get(CategorizerConfig.MASK_CATEGORIZER, "indexed_file_format", dvalue=".png")
    self.indexed_masks_dir   = self.config.get(CategorizerConfig.MASK_CATEGORIZER, "indexed_masks_dir")
    
    self.categorized_file_format = self.config.get(CategorizerConfig.MASK_CATEGORIZER, "categorized_file_format")
    self.categorized_masks_dir   = self.config.get(CategorizerConfig.MASK_CATEGORIZER, "categorized_masks_dir")
    
    print(self.rgb_map)
    self.verbose = verbose
    #  rgb_map dict  { key1:value1, key2:value2,...}
    #  rgb_map     = { (0, 0, 0): 0, (0, 255, 0):1, (255,0,0):2, (0, 0, 255):3,...  }
    self.rgb_color = []
    for item in self.rgb_map:
      self.rgb_color += [list(item)]
    # rgb_color = [[0, 0, 0], [0, 255, 0], [255, 0, 0], [0, 0, 255]]
    print("rgb_color {}".format(self.rgb_color))
  
    self.num_classes = len(self.rgb_map)
    self.rgb_array   = np.array(self.rgb_color)
    self.rgb_array   = self.rgb_array.reshape((-1, 1, 1, 3))

    self.palette = []
    for item in self.rgb_map:
      self.palette += list(item)
    # flattened palette 
    # palette   = [0, 0, 0, 0, 255, 0, 255,0,0, 0, 0, 255]
    print("palette {}".format(self.palette))
  
  def convert(self):
    if os.path.exists(self.indexed_masks_dir):
      shutil.rmtree(self.indexed_masks_dir)
    os.makedirs(self.indexed_masks_dir)
    rgb_mask_files = glob.glob(self.rgb_masks_dir + "/*" + self.rgb_file_format)
    print(rgb_mask_files)
    for rgb_mask_file in rgb_mask_files:
      print(rgb_mask_file)
      indexed_mask = self.convert_one(rgb_mask_file)
      basename      = os.path.basename(rgb_mask_file)
      indexed_mask_file = os.path.join(self.indexed_masks_dir + basename)
      indexed_mask.save(indexed_mask_file)

  # Return PIL indexed-image 
  def convert_one(self, rgb_mask_file):
    #print(rgb_mask_file)
    rgb_mask = Image.open(rgb_mask_file).convert(self.color_order)
    if self.verbose:
       width, height = rgb_mask.size
       print("--rgb_mask_file {} image width {} height {}".format(rgb_mask_file, width, height))

    rgb_mask_array   = np.array(rgb_mask)
    indexed_array = np.argmin(np.sum((rgb_mask_array - self.rgb_array)**2, axis=-1), axis=0)

    # Create PIL image
    indexed_mask = Image.fromarray(indexed_array.astype(np.uint8), mode="P")
    indexed_mask.putpalette(self.palette)
    
    return indexed_mask

if __name__ == "__main__":
  try:
    mask_categorizer_ini = "./mask_categorizer.ini"  
    rgb_mask_file     = "./sample_rgb_mask.png"
    indexed_mask_file = "./sample_indexed_mask.png"
 
    print("Started conversion from rgb_mask_file {}".format(rgb_mask_file))
    
    start_time    = time.time()
    converter     = RGBMask2IndexedMaskConverter(mask_categorizer_ini)

    indexed_mask = converter.convert_indexed_mask(rgb_mask_file)

    indexed_mask.save(indexed_mask_file)
    print("Finished conversion to {}".format(indexed_mask_file))
    
    end_time     = time.time()
    print("Elapsed time {}".format(end_time - start_time))
   
  except:
    traceback.print_exc()
