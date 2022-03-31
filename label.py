import cv2
import sys
import numpy as np

def connected_component(filename = 'vtest.mp4'):
    cap = cv2.VideoCapture(filename)

# Create a background substractor.
    backSub = cv2.createBackgroundSubtractorMOG2()

# Check whether the video is read successfully or not, and read the frame subsequently.
    while cap.isOpened():
        ret, frame = cap.read()
        fgmask = backSub.apply(frame)

# Find out the shadow value. 127 is default, 0 is background and 255 is foreground.
        shadowval = backSub.getShadowValue()
        ret, nmask = cv2.threshold(fgmask, shadowval, 255, cv2.THRESH_BINARY)

        height, width = nmask.shape[0], nmask.shape[1] # 576, 720
        picture, mark, records = np.zeros(shape = (height, width), dtype = 'int16'), 100, dict()

        for i in range(height):
            for j in range(width):
                if nmask[i][j] == 255: picture[i][j] = 1

# First pass for connected component.
        for i in range(height):
            for j in range(width):
                if i == 0 and j == 0:
                    if picture[i][j] == 1: 
                        picture[i][j], mark = mark, mark + 1
                    else:
                        continue

                if i == 0 and picture[i][j] == 1:
                    if picture[i][j - 1] == 0: 
                        picture[i][j], mark = mark, mark + 1
                    else: 
                        picture[i][j] = picture[i][j - 1]
                elif j == 0 and picture[i][j] == 1:
                    if picture[i - 1][j] == 0: 
                        picture[i][j], mark = mark, mark + 1
                    else: 
                        picture[i][j] = picture[i - 1][j]
                elif picture[i][j] == 1:
                    if picture[i][j - 1] == 0 and picture[i - 1][j] == 0: 
                        picture[i][j], mark = mark, mark + 1
                    elif picture[i][j - 1] != 0 and picture[i - 1][j] == 0:
                        picture[i][j] = picture[i][j - 1]
                    elif picture[i][j - 1] == 0 and picture[i - 1][j] != 0:
                        picture[i][j] = picture[i - 1][j]
                    else:
                        if picture[i][j - 1] < picture[i - 1][j]:
                            picture[i][j] = picture[i][j - 1]
                            records[picture[i - 1][j]] = picture[i][j - 1]
                        elif picture[i][j - 1] > picture[i - 1][j]:
                            picture[i][j] = picture[i - 1][j]
                            records[picture[i][j - 1]] = picture[i - 1][j]
                        elif picture[i][j - 1] == picture[i - 1][j]:
                            picture[i][j] = picture[i - 1][j]

        records_final, area_count = records.copy(), dict()

# Update the record to check which of them are the same group.
        for key, value in records.items():
            while value in records:
                records_final[key] = records[value]
                value = records_final[key]

# Second pass for the connected component, and also record the areas of the groups.
        for i in range(height):
            for j in range(width):
                if picture[i][j] in records_final:
                    picture[i][j] = records_final[picture[i][j]]

                if picture[i][j] not in area_count: 
                    area_count[picture[i][j]] = 1
                else: 
                    area_count[picture[i][j]] += 1

        remain, coords = set(), list()

# Remain the groups that their area is greater than 500.
        for key, value in area_count.items():
            if value >= 500: remain.add(key)

# Find the left up corner and the right bottom corner coordinates so that we can draw a rectangle the frame the objects.
        for number in remain:
            start_x, start_y, end_x, end_y = width - 1, height - 1, 0, 0

            for i in range(height):
                for j in range(width):
                    if picture[i][j] == number:
                        if j < start_x: start_x = j
                        if j > end_x: end_x = j
                        if i < start_y: start_y = i
                        if i > end_y: end_y = i

            start_coord, end_coord = (start_x, start_y), (end_x, end_y)
            coords.append((start_coord, end_coord))

# Draw rectangles to frame the objects.
        for i in range(1, len(coords)):
            cv2.rectangle(frame, (coords[i][0][0], coords[i][0][1]), (coords[i][1][0], coords[i][1][1]), (255, 0, 0), 2)
    
# Show the video on screen and wait few times to read the next frame.
        cv2.imshow("output", frame)
        cv2.waitKey(1)

if __name__ == "__main__":
    if len(sys.argv) > 1: connected_component(sys.argv[1])
    else: connected_component()
