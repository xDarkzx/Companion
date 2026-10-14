# Evaluation

Companion's perception is measured, not demonstrated. Every number on this page comes from a
script in [`eval/`](../eval) and the result file it wrote to [`eval/results/`](../eval/results).
Each result file records the dataset, model revisions, settings, device, date and commit. The
tables below are generated from those files by `python eval/report.py`, and CI fails if this page
and the files disagree.

## What is measured, and why

A robot that is asked "where is the red mug?" has to get three things right, so there are three
benchmarks.

| Question | Benchmark | Script |
|---|---|---|
| Does it find the object it was asked for? | COCO val2017: all 5,000 images, with the 80 class names as the text queries | [`coco_detection.py`](../eval/coco_detection.py) |
| Does it put the object in the right place in 3D? | NYU Depth V2 labelled set, official 654-frame test split, 14 household classes | [`nyu_localization.py`](../eval/nyu_localization.py) |
| Is it fast enough to use on a robot? | 200 fixed NYU frames, after 10 warm-up frames | [`latency.py`](../eval/latency.py) |

### Finding objects (COCO)

- **Queries:** the 80 COCO category names, unmodified. They aren't rephrased into prompts, so
  the scores reflect what a person would actually say.
- **Scoring:** the standard `pycocotools` bounding-box evaluation, with a 0.05 score threshold
  and up to 100 boxes per image. That's the usual setting for reporting AP. The robot itself
  runs with a 0.2 threshold and at most 20 boxes.
- **Interpreting it:** AP averages precision over IoU thresholds from 0.5 to 0.95. AP50 only
  needs the box to overlap the truth by half, which is closer to what "point me at the mug"
  needs.

### Placing objects in 3D (NYU Depth V2)

- **Ground truth:** for each object, the median 3D point of its segmentation mask, back-projected
  from the dataset's in-filled depth with the standard Kinect intrinsics. Objects smaller than
  500 pixels or cut off by the edge of the valid region (the Eigen crop) are skipped.
- **Detection:** the detector is asked for the class names present in the frame, at the robot's
  own settings (threshold 0.2). Detections are matched to objects greedily at IoU ≥ 0.5.
- **Two depth sources** are compared for every matched object:
  - **Depth camera:** the dataset's raw Kinect frames, holes included, as a robot's RGB-D
    camera would deliver them.
  - **Monocular estimate:** Depth Anything V2 Metric Indoor Small, from the RGB image alone,
    as a robot with only a webcam would have to work.
- **Error:** the straight-line distance between the estimated position and the ground truth.

### Speed

Detection, monocular depth and localisation are timed separately for each frame at 640 × 480,
with batch size 1 and fp32. These numbers are only meaningful when nothing else is using the
GPU.

## Results

<!-- results:start -->
<!-- results:end -->

## Reproducing

1. Install the vision library with its model extras, in a Python 3.10+ environment that has a
   CUDA build of PyTorch:

   ```bash
   pip install -e "ros2_ws/src/companion_vision[models]" pycocotools h5py scipy
   ```

2. Download the data outside the repo. Set `COMPANION_DATA` if you use a location other than
   `D:/Datasets/companion`:
   - COCO: `val2017.zip` and `annotations_trainval2017.zip` from <https://cocodataset.org>.
   - NYU Depth V2: `nyu_depth_v2_labeled.mat` and `splits.mat` from the
     [NYU Depth V2 page](https://cs.nyu.edu/~fergus/datasets/nyu_depth_v2.html).

3. Run the benchmarks and regenerate this page:

   ```bash
   python eval/coco_detection.py --backend owlv2
   python eval/nyu_localization.py --backend owlv2
   python eval/latency.py --backend owlv2 --device cuda
   python eval/report.py
   ```

Per-image detections are cached in `eval/.cache/`, so an interrupted COCO run resumes where it
stopped. The datasets and caches are never committed.
