import os
from os import walk, getcwd, path, mkdir
from PIL import Image
# Covert to YOLO Format
def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)



# Get current working directory.
wd = getcwd()
mypath = wd + '\\Annotations\\Annotations'

# Get Annotation files
csv_list = []
for (dirpath, dirnames, filenames) in walk(wd):
    csv_list.extend([dirpath + '\\frameAnnotationsBOX.csv'] for file in filenames if file == 'frameAnnotationsBOX.csv')

# If Images and Labes directories do not exists. Create them to avoid errors.
if not path.exists(wd + '\\Images'):
    mkdir(wd + '\\Images')
if not path.exists(wd + '\\Labels'):
    mkdir(wd + '\\Labels')

# Check if classes were defined before
f_classes = []
if path.exists('classes.cfg'):
    file = open('classes.cfg', 'r')
    f_classes = file.read().split('/n')

# Automatically detect what classes have been added.
classes = []
for csv in csv_list:
    csv_path = csv
    csv_file = open(csv_path[0], "r")
    rows = csv_file.read().split('\n')
    ct = 0
    for row in rows:
        if (ct > 1 and len(row)>2):
            cls = row.split(';')[1]
            if cls not in classes:
                classes.append(cls)
        ct = ct + 1

# Check if anything changed
changed = False
if len(classes) == len(f_classes):
    for cls in classes:
        if cls not in f_classes:
            changed = True
else:
    changed = True

# If changed ask user to continue.
if changed:
    print('Class values are not same before.')
    print('Saved classes:')
    print(f_classes)
    print('Current classes:')
    print(classes)
    while True:
        dec = input('Do you want to proceed? (y/n)')
        if dec == 'n':
            exit()
        if dec == 'y':
            break
        print('Wrong input!')

# Apply function and rearrange files according to Standard YOLO format.
for csv in csv_list:
    # Get rid of sample files.
    if 'Annotations' not in csv[0].split('\\'):
        continue
    csv_file = open(csv[0], "r")
    rows = csv_file.read().split('\n')
    imsc = csv[0].split('\\')
    index = 0
    for dir in range(len(imsc)):
        if imsc[dir] == 'Annotations':
            index = dir
    imsc = imsc[index+1:-1]
    imsc = wd + '\\' + imsc[0] + '\\' + '\\'.join(imsc) + '\\frames\\'
    ct = 0
    for row in rows:
        if (ct > 1 and len(row)>2):
            # Convert to array
            elements = row.split(';')

            # Set x, y values
            xmin = elements[2]
            xmax = elements[4]
            ymin = elements[3]
            ymax = elements[5]

            # Gather class information.
            cls_id = classes.index(elements[1])
            img_path = imsc + elements[0].split('/')[-1]
            im = Image.open(img_path)
            w = int(im.size[0])
            h = int(im.size[1])
            b = (float(xmin), float(xmax), float(ymin), float(ymax))
            bb = convert((w,h), b)

            # Save output
            outfile = open(f"{wd}\\Labels\\{''.join(elements[0].split('/')[-1].split('.')[:-1])}.txt", 'a+')
            im.save(f"{wd}\\Images\\{elements[0].split('/')[-1]}")
            outfile.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

            # Show Progress
            print(f"{elements[1]} located at {xmin}, {ymin} - {xmax}, {ymax} in {elements[0].split('/')[-1]}")
        ct = ct + 1

# Save what are the classes are.
file = open('classes.cfg', 'w+')
file.write('\n'.join(classes))