import cv2
from cv2.typing import MatLike

from config import RED_REAL_OBJECT_WIDTH, BLUE_REAL_OBJECT_WIDTH, YELLOW_REAL_OBJECT_WIDTH, FOCAL_LENGTH, MIN_CONTOUR_AREA, CENTRE_RANGE

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

def detect_colour_and_draw(
    frame: MatLike, midpoint_x: int,
    red1_lower: MatLike, red1_upper: MatLike,
    red2_lower: MatLike, red2_upper: MatLike,
    blue_lower: MatLike, blue_upper: MatLike,
    yellow_lower: MatLike, yellow_upper: MatLike,
):
    # Convert the frame to HSV
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_red1 = cv2.inRange(frame_hsv, red1_lower, red1_upper)
    mask_red2 = cv2.inRange(frame_hsv, red2_lower, red2_upper)
    # combine the two red masks
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # one range for blue = only one blue mask
    mask_blue = cv2.inRange(frame_hsv, blue_lower, blue_upper)

    mask_yellow = cv2.inRange(frame_hsv, yellow_lower, yellow_upper)


    # ! RED
    red_detected_objects = []

    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for i, contour in enumerate(contours_red):
    for contour in contours_red:
        # skip if this contour is not larger than the minimum area 
        if cv2.contourArea(contour) < MIN_CONTOUR_AREA:
                continue

        contour_centre = get_contour_centre(contour)
        if contour_centre is None:
            continue

        (distance, location) = process_contour(contour, contour_centre, frame, midpoint_x, (0, 0, 255), RED_REAL_OBJECT_WIDTH)

        red_detected_objects.append((contour_centre, distance, location))

    # ? BLUE

    blue_detected_objects = []
    contours_blue, hierarchy_blue = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i, contour in enumerate(contours_blue):
        # skip if the contour is not larger than the minimum area or it is within another contour
        if cv2.contourArea(contour) < MIN_CONTOUR_AREA or hierarchy_blue[0][i][3] != -1:
                continue

        contour_centre = get_contour_centre(contour)
        if contour_centre is None:
            continue

        (distance, location) = process_contour(contour, contour_centre, frame, midpoint_x, (255, 0, 0), BLUE_REAL_OBJECT_WIDTH)

        blue_detected_objects.append((contour_centre, distance, location))

    # ~ YELLOW

    yellow_detected_objects = []
    contours_yellow, hierarchy_yellow = cv2.findContours(mask_yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i, contour in enumerate(contours_yellow):
        # skip if the contour is not larger than the minimum area or it is within another contour
        if cv2.contourArea(contour) < MIN_CONTOUR_AREA or hierarchy_yellow[0][i][3] != -1:
                continue

        contour_centre = get_contour_centre(contour)
        if contour_centre is None:
            continue

        (distance, location) = process_contour(contour, contour_centre, frame, midpoint_x, (0, 255, 255), YELLOW_REAL_OBJECT_WIDTH)

        yellow_detected_objects.append((contour_centre, distance, location))


    return (frame, red_detected_objects, blue_detected_objects, yellow_detected_objects)