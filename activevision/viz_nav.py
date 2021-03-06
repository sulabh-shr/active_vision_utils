import os
from PIL import Image
import matplotlib.pyplot as plt

from activevision.defaults import AVD_DATASET
from activevision.annotations import AVDAnnotations, AVDCategoryAnns
from activevision.utils.plot_utils import bboxplot_in_img


def visualize_boxes_and_move(scene, box_type='instance', start_idx=0):
    data_root = AVD_DATASET
    if box_type == 'instance':
        scene_ann = AVDAnnotations(data_root=data_root)
    else:
        scene_ann = AVDCategoryAnns(data_root=data_root)
    scene_ann.load_annotations(scenes=[scene])

    input_map = {
        'w': 'forward',
        's': 'backward',
        'a': 'rotate_ccw',
        'd': 'rotate_cw',
        'z': 'left',
        'x': 'right'
    }

    input_ = start_idx
    fig, ax = plt.subplots(1, figsize=(16, 9))

    while True:
        try:
            input_ = int(input_)
            img_name = scene_ann.idx2image(scene=scene, idx=input_)
        except ValueError:
            if input_ == 'q':
                print('Quitting')
                break
            elif input_ in input_map:
                dir = input_map[input_]
                next_img = scene_ann.get_neighbor_image(scene=scene, img_name=img_name,
                                                        direction=dir)
                if next_img == '':
                    print(f'No image available in direction: **{dir}**! Try another command.')
                else:
                    img_name = next_img
            else:
                print(f'Invalid input! Possible inputs:\n{input_map}')
                print('Or input a number < number of images in current scene or "q" to Quit.')

        img_path = scene_ann.img_name2path(scene=scene, name=img_name)
        img = Image.open(img_path)
        if box_type == 'instance':
            boxes_dict = scene_ann.get_image_boxes(scene, img_name)
        else:
            boxes_dict = scene_ann.get_image_boxes(scene, img_name, box_type=box_type)

        bboxes = []
        labels = []

        if box_type == 'instance' or box_type == 'both':
            bboxes += list(boxes_dict['instance_boxes'])
            labels += boxes_dict['instance_names']
        if box_type == 'category' or box_type == 'both':
            bboxes += list(boxes_dict['category_boxes'])
            labels += boxes_dict['category_names']

        plt.cla()
        fig, ax = bboxplot_in_img(img, bboxes=bboxes,
                                  labels=labels,
                                  fig=fig, ax=ax, return_fig=True)
        ax.set_title(img_name)
        plt.draw()
        plt.pause(0.01)
        input_ = input('\nEnter command:  ')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', '-s', type=str, required=True,
                        help='Name of scene to visualize.')
    parser.add_argument('--type', type=str, required=True, choices=['instance', 'category', 'both'],
                        help='Type of bounding boxes to display')
    parser.add_argument('--idx', type=int, required=False, default=0,
                        help='Index to start visualizations from.')

    args = parser.parse_args()

    visualize_boxes_and_move(scene=args.scene, box_type=args.type, start_idx=args.idx)
