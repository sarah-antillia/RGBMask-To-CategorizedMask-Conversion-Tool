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
# RGBMask2CategorizedMaskConverter.py

import os
import cv2
import shutil
import glob
import numpy as np
import traceback
from PIL import Image
from CategorizerConfig import CategorizerConfig

from tensorflow.keras.utils import to_categorical

class RGBMask2CategorizedMaskConverter:
  def __init__(self, mask_categorizer_ini, verbose=True):
    self.verbose         = verbose
    self.config          = CategorizerConfig(mask_categorizer_ini)
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
    #  rgb_map dict  takes the following format
    #                { key1:value1, key2:value2,...}
    #  rgb_map     = { (0, 0, 0): 0, (0, 255, 0):1, (255,0,0):2, (0, 0, 255):3,...  }
  
    self.rgb_color = []
    for item in self.rgb_map:
      self.rgb_color += [list(item)]
    # rgb_color = [[0, 0, 0], [0, 255, 0], [255, 0, 0], [0, 0, 255]]
    print("rgb_color {}".format(self.rgb_color))
  
    self.num_classes = len(self.rgb_map)
    self.rgb_array   = np.array(self.rgb_color)
    self.rgb_array   = self.rgb_array.reshape((-1, 1, 1, 3))

    # Create a flattened palette from self.rgb_map 
    self.palette = []
    for item in self.rgb_map:
      self.palette += list(item)
    # palette   = [0, 0, 0, 0, 255, 0, 255,0,0, 0, 0, 255]
    print("palette {}".format(self.palette))


  def convert(self):
    if os.path.exists(self.categorized_masks_dir):
      shutil.rmtree(self.categorized_masks_dir)
    os.makedirs(self.categorized_masks_dir)
    rgb_mask_files = glob.glob(self.rgb_masks_dir + "/*" + self.rgb_file_format)

    for rgb_mask_file in rgb_mask_files:
       categorized_mask = self.convert_one(rgb_mask_file)
       basename = os.path.basename(rgb_mask_file)
       categorized_mask_file = basename.replace(self.rgb_file_format, self.categorized_file_format)
       categorized_mask_filepath = os.path.join(self.categorized_masks_dir, categorized_mask_file) 
       np.savez_compressed(categorized_mask_filepath, mask=categorized_mask)
       print("Converted {}  to {}".format(rgb_mask_file, categorized_mask_filepath))

  # Return PIL indexed-image 
  def rgb_mask_to_indexed_mask(self, rgb_mask_file):
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


  def convert_one(self, rgb_mask_file):
    # 1 convert rgb mask to Indexed mask
    # PIL indexed_mask will be returned
    indexed_mask = self.rgb_mask_to_indexed_mask(rgb_mask_file)
    
    # convert PIL image to nummpu array
    indexed_array = np.array(indexed_mask)
    if self.verbose:
      print("Shape of indexed array :", indexed_array.shape)
    # from tensorflow.keras.utils import to_categorical

    # 2 create categorized_mask (numpy array)
    categorized_mask = to_categorical(indexed_array, num_classes=self.num_classes)
    if self.verbose:
      print("Shape of categorized_mask:", categorized_mask.shape)
    return categorized_mask
    

if __name__ == "__main__":
  try:
    mask_categorizer_ini ="./mask_categorizer.ini"

    converter = RGBMask2CategorizedMaskConverter(mask_categorizer_ini, verbose=True)
    converter.convert()

  except:
    traceback.print_exc()
