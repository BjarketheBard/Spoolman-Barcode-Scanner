import cv2
import zxingcpp
import numpy as np

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if camera.isOpened():
    print("Success! Camera Connected.")

    active_barcode = None
    reference_region = None

    saved_x_min = None
    saved_x_max = None
    saved_y_min = None
    saved_y_max = None

    clear_frames = 0
    difference_fail_frames = 0

    clear_threshold = 30
    difference_threshold = 40
    difference_fail_threshold = 8

    while True:
        success, frame = camera.read()

        if success:
            annotated_frame = frame.copy()

            results = zxingcpp.read_barcodes(frame)

            if results:
                clear_frames = 0
            else:
                clear_frames += 1

            for result in results:

                points = [
                    (result.position.top_left.x, result.position.top_left.y),
                    (result.position.top_right.x, result.position.top_right.y),
                    (result.position.bottom_right.x, result.position.bottom_right.y),
                    (result.position.bottom_left.x, result.position.bottom_left.y)
                ]

                polygon = np.array(points, dtype=np.int32)

                cv2.polylines(
                    annotated_frame,
                    [polygon],
                    True,
                    (0, 255, 0),
                    2
                )

                x_min = np.min(polygon[:, 0])
                x_max = np.max(polygon[:, 0])
                y_min = np.min(polygon[:, 1])
                y_max = np.max(polygon[:, 1])

                padding = 70

                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(frame.shape[1], x_max + padding)
                y_max = min(frame.shape[0], y_max + padding)

                barcode_region = frame[y_min:y_max, x_min:x_max]

                cv2.imshow("Barcode Region", barcode_region)

                if active_barcode is None:
                    print(result.text)
                    print(result.format)
                    print(result.position)
                    print(polygon)

                    active_barcode = result.text

                if result.text == active_barcode:
                    reference_region = barcode_region.copy()

                    saved_x_min = x_min
                    saved_x_max = x_max
                    saved_y_min = y_min
                    saved_y_max = y_max

                    difference_fail_frames = 0

            if (
                not results
                and active_barcode is not None
                and reference_region is not None
                and saved_x_min is not None
            ):
                current_region = frame[
                    saved_y_min:saved_y_max,
                    saved_x_min:saved_x_max
                ]

                if current_region.size > 0:

                    reference_gray = cv2.cvtColor(
                        reference_region,
                        cv2.COLOR_BGR2GRAY
                    )

                    current_gray = cv2.cvtColor(
                        current_region,
                        cv2.COLOR_BGR2GRAY
                    )

                    current_gray = cv2.resize(
                        current_gray,
                        (
                            reference_gray.shape[1],
                            reference_gray.shape[0]
                        )
                    )

                    difference = cv2.absdiff(
                        reference_gray,
                        current_gray
                    )

                    score = np.mean(difference)

                    print(
                        f"Clear Frames: {clear_frames} | "
                        f"Difference: {score:.2f} | "
                        f"Fail Frames: {difference_fail_frames}"
                    )

                    if score >= difference_threshold:
                        difference_fail_frames += 1
                    else:
                        difference_fail_frames = 0

                    if (
                        clear_frames >= clear_threshold
                        and difference_fail_frames >= difference_fail_threshold
                    ):
                        print("Barcode Cleared")

                        active_barcode = None
                        reference_region = None

                        saved_x_min = None
                        saved_x_max = None
                        saved_y_min = None
                        saved_y_max = None

                        clear_frames = 0
                        difference_fail_frames = 0

            cv2.imshow("Camera", annotated_frame)

            key = cv2.waitKey(1) & 0xFF

        else:
            print("Unable to see. Please check device.")
            break

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

else:
    print("Camera Unavailable. Check Camera Connection")