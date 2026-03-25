import imutils
import cv2

# HSV range for BLACK color
blackLower = (0, 0, 0)
blackUpper = (180, 255, 50)

camera = cv2.VideoCapture(0)

prev_direction = ""   # store previous direction

while True:
    (grabbed, frame) = camera.read()
    if not grabbed:
        break

    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, blackLower, blackUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)

        if M["m00"] != 0:
            center = (int(M["m10"] / M["m00"]),
                      int(M["m01"] / M["m00"]))

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)),
                           int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

                # ---- Direction Logic ----
                direction = ""

                if radius > 250:
                    direction = "Stop"
                else:
                    if center[0] < 150:
                        direction = "Left"
                    elif center[0] > 450:
                        direction = "Right"
                    else:
                        direction = "Front"

                # Print only if direction changed
                if direction != prev_direction:
                    print(direction)
                    prev_direction = direction

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
