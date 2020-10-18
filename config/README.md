# Configuration file

This is an example of a configuration file for preprocessing

```
# Example configuration file:

work_dir:       /home/student/dl2/grp5/cca5/dataset/workdir
metadata_file:  /home/student/dl2/grp5/cca5/dataset/dai-asllvd.xlsx
clean_workdir:  False

phases: 
  download, 
  segment, 
  skeleton, 
  filter,
  split,
  normalize

download:
  output_dir:     ../../original
  url:            http://csr.bu.edu/ftp/asl/asllvd/asl-data2/quicktime
  file_pattern:   '{session}/scene{scene}-camera{camera}.mov'
  metadata_url:   http://www.bu.edu/asllrp/dai-asllvd-BU_glossing_with_variations_HS_information-extended-urls-RU.xlsx

segment:
  input_dir:    ../../original
  output_dir:   segmented
  fps_in:       60
  fps_out:      30

skeleton:
  openpose:   /home/student/dl2/grp5/cca5/openpose/openpose/build
  input_dir:  ./segmented
  output_dir: ./skeleton
  model_path: ./st-gcn/models

filter:
  input_dir:  ./skeleton
  output_dir: ./filtered
  points:     1, 2, 3, 5, 6,
              88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108,
              109, 111, 113, 115, 117, 119, 121, 123, 125, 127, 129

split:
  input_dir:  ./filtered
  output_dir: ./splitted
  test:       20
  val:        0
  seed:       2

normalize:
  input_dir:      ./splitted
  output_dir:     ./normalized
  joints:         27
  channels:       3
  num_person:     1
  repeat_frames:  True
  max_frames:     63

# debug_opts:
#  download_items:   5
#  split_items:      5
#  pose_items:       5
#  gendata_items:    5
#  gendata_joints:   27

```