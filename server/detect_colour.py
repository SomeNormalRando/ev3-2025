import cv2
import numpy as np

# lower and upper bounds for the colours in HSV
# in HSV, there are two sections of red (start & end) and one section of blue
LOWER_RED_1 = np.array([0, 150, 150])
UPPER_RED_1 = np.array([10, 255, 255])
LOWER_RED_2 = np.array([170, 150, 150])
UPPER_RED_2 = np.array([180, 255, 255])

LOWER_BLUE = np.array([90, 50, 70])
UPPER_BLUE = np.array([120, 255, 255])

RED_REAL_OBJECT_WIDTH = 1.5
BLUE_REAL_OBJECT_WIDTH = 8.5

# focal length of the camera
FOCAL_LENGTH = 500

MIN_CONTOUR_AREA = 500
CENTRE_RANGE = 25

def process_contour(
        contour: cv2.typing.MatLike, contour_centre: tuple[int, int],
        frame: cv2.typing.MatLike, midpoint_x: int,
        box_colour: tuple[int, int, int], real_object_width: float
):
    # get the bounding box coordinates
    x, y, w, h = cv2.boundingRect(contour)
    # draw the bounding box
    cv2.rectangle(frame, (x, y), (x + w, y + h), box_colour, 2)
    # draw the centre point
    cv2.circle(frame, contour_centre, 5, (0, 255, 255), -1)
    # label the centre point
    cv2.putText(frame, f"Centre {contour_centre}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # Calculate the distance to the object
    perceived_width = w  # Use the width of the bounding box
    distance = (real_object_width * FOCAL_LENGTH) / perceived_width

    location: int

    location_text = ""
    if abs(contour_centre[0] - midpoint_x) < CENTRE_RANGE:
        location = 0
        location_text = "CENTRE"
    elif contour_centre[0] < midpoint_x:
        location = -1
        location_text = "LEFT"
    else:
        location = 1
        location_text = "RIGHT"

    # Annotate the distance & location
    cv2.putText(frame, f"Distance: {distance:.2f} cm [{location_text}]", (x, y + h + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return (distance, location)


# Function to calculate the centre of a contour
def get_contour_centre(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:  # Avoid division by zero
        return None
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return cX, cY

def detect_colour_and_draw(frame: cv2.typing.MatLike, midpoint_x: int):
    # Convert the frame to HSV
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_red1 = cv2.inRange(frame_hsv, LOWER_RED_1, UPPER_RED_1)
    mask_red2 = cv2.inRange(frame_hsv, LOWER_RED_2, UPPER_RED_2)
    # combine the two red masks
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # one range for blue = only one blue mask
    mask_blue = cv2.inRange(frame_hsv, LOWER_BLUE, UPPER_BLUE)


    # ! RED
    detectedRedObjects = []

    contours_red, hierarchy_red = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i, contour in enumerate(contours_red):
        # skip if this contour is not larger than the minimum area or it is within another contour
        if cv2.contourArea(contour) < MIN_CONTOUR_AREA or hierarchy_red[0][i][3] != -1:
                continue

        contour_centre = get_contour_centre(contour)
        if contour_centre is None:
            continue

        (distance, location) = process_contour(contour, contour_centre, frame, midpoint_x, (0, 0, 255), RED_REAL_OBJECT_WIDTH)

        detectedRedObjects.append((contour_centre, distance, location))

    # ? BLUE
    detectedBlueObjects = []
    contours_blue, hierarchy_blue = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i, contour in enumerate(contours_blue):
        # skip if the contour is not larger than the minimum area
        if cv2.contourArea(contour) < MIN_CONTOUR_AREA or hierarchy_blue[0][i][3] != -1:
                continue

        contour_centre = get_contour_centre(contour)
        if contour_centre is None:
            continue

        (distance, location) = process_contour(contour, contour_centre, frame, midpoint_x, (255, 0, 0), RED_REAL_OBJECT_WIDTH)

        detectedBlueObjects.append((contour_centre, distance, location))

    return (frame, detectedRedObjects, detectedBlueObjects)
    # # Display the frame
    # cv2.imshow("Frame", frame)

    # # Exit on pressing 'q'
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# capt.release()
# cv2.destroyAllWindows()