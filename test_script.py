import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot receive frame (stream end?). Exiting ...")
        break
    cv2.imshow('frame', frame)
    
    # Check if the 'q' key is pressed or if the window is closed
    if cv2.waitKey(1) == ord('q') or cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
